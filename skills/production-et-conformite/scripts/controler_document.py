#!/usr/bin/env python3
"""Contrôleur de conformité formelle et générateur de bon de travail (.docx, .pdf).

Bibliothèque standard Python uniquement, lecture seule, aucun appel réseau.
Aucun seuil réglementaire de tribunal n'est codé en dur : transmettre les seuils
lus via `lois` par `--regles <fichier.json|etiquette>` ou par options explicites.

Usage :
    python scripts/controler_document.py <fichier>... [--regles regles.json] [--max-pages 5] [--json]
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
import zlib

_DOCX_EXTS = {".docx", ".docm"}
_PDF_EXTS = {".pdf"}
_MAX_ZIP_MEMBER_BYTES = 64 * 1024 * 1024
_MAX_ZIP_TOTAL_BYTES = 128 * 1024 * 1024
_MAX_RAW_FILE_BYTES = 128 * 1024 * 1024
_MAX_ZLIB_STREAM_BYTES = 32 * 1024 * 1024
_MAX_PDF_OBJSTM_TOTAL_BYTES = 64 * 1024 * 1024
_VANISH_TAGS = ("vanish", "specVanish", "webHidden")
_XML_OFF_VALUES = frozenset({"0", "false", "off"})

_W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
_A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
_DC_NS = "http://purl.org/dc/elements/1.1/"
_CP_NS = "http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
_DCTERMS_NS = "http://purl.org/dc/terms/"
_APP_NS = "http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"

_PDF_HEADER_RE = re.compile(rb"%PDF-(\d+\.\d+)")
_PDF_PAGE_RE = re.compile(rb"/Type\s*/Page(?![A-Za-z])")
_PDF_PAGES_COUNT_RE = re.compile(rb"/Type\s*/Pages\b[^>]*?/Count\s+(\d+)")
_PDF_ENCRYPT_RE = re.compile(rb"/Encrypt\b")
_PDF_OUTLINES_DICT_RE = re.compile(rb"/Type\s*/Outlines\b[^>]*>>|/Outlines\s*<<[^>]*>>", re.S)
_PDF_OUTLINES_RE = re.compile(rb"/Outlines\b")
_PDF_OUTLINE_COUNT_RE = re.compile(rb"/Count\s+(\d+)")
_PDF_OUTLINE_FIRST_RE = re.compile(rb"/First\s+\d+\s+\d+\s+R")
_PDF_OUTLINE_ITEM_DICT_RE = re.compile(
    rb"<<(?:(?!<<|>>).)*(?:/Title\s*(?:\(|<)(?:(?!<<|>>).)*?/(?:Parent|Dest|A|Next|Prev)\b|/(?:Parent|Dest|A|Next|Prev)\b(?:(?!<<|>>).)*?/Title\s*(?:\(|<))(?:(?!<<|>>).)*?>>",
    re.S,
)
_PDF_LINK_RE = re.compile(rb"/Subtype\s*/Link\b")
_PDF_URI_RE = re.compile(rb"/URI\s*\(((?:\\.|[^\\()])*)\)")
_PDF_MEDIABOX_RE = re.compile(
    rb"/MediaBox\s*\[\s*(-?\d+(?:\.\d+)?)\s+(-?\d+(?:\.\d+)?)\s+(-?\d+(?:\.\d+)?)\s+(-?\d+(?:\.\d+)?)\s*\]"
)
_PDF_STREAM_RE = re.compile(rb"stream(?:\r\n|\n)(.*?)(?:\r\n|\r|\n)?endstream", re.S)
_PDF_NON_TEXT_STREAM_RE = re.compile(
    rb"/Subtype\s*/(?:Image|XML|Type1C|CIDFontType0C|OpenType)\b|"
    rb"/Type\s*/(?:Metadata|XRef)\b|"
    rb"/(?:DCTDecode|JPXDecode|JBIG2Decode|CCITTFaxDecode)\b|"
    rb"/Length1\b"
)
_PDF_FILTER_RE = re.compile(rb"/Filter\b")
_PDF_TEXT_OP_RE = re.compile(
    rb"\bBT\b(?:(?!\bET\b).){0,50000}?(?:\([^)]*\)|<[0-9A-Fa-f\s]+>|\[[^\]]*\])\s*T[jJ]\b",
    re.S,
)
_PDF_OBJSTM_RE = re.compile(rb"/Type\s*/ObjStm\b")
_PDF_FIRST_RE = re.compile(rb"/First\s+(\d+)")


def _configure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconf = getattr(stream, "reconfigure", None)
        if callable(reconf):
            reconf(encoding="utf-8", errors="replace")


def _decompress_zlib_bounded(
    data: bytes, max_bytes: int = _MAX_ZLIB_STREAM_BYTES
) -> bytes | None:
    try:
        dobj = zlib.decompressobj()
        out = dobj.decompress(data, max_bytes + 1)
        if len(out) > max_bytes or dobj.unconsumed_tail:
            return None
        tail = dobj.flush(max_bytes + 1 - len(out))
        if len(out) + len(tail) > max_bytes:
            return None
        return out + tail
    except zlib.error:
        return None


def _truncate(text: str, limit: int = 120) -> str:
    cleaned = " ".join(text.split())
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 1] + "…"


class _ZipLimitExceeded(ValueError):
    """Levée lorsqu'un membre OOXML dépasse le plafond de décompression sécurisé."""


def _is_w_flag_enabled(el: ET.Element) -> bool:
    raw = el.attrib.get(f"{{{_W_NS}}}val")
    if raw is None:
        raw = el.attrib.get("val")
    if raw is None:
        return True
    return raw.strip().lower() not in _XML_OFF_VALUES


def _read_zip_member_bounded(
    zf: zipfile.ZipFile, member: str, total_budget: list[int] | None = None
) -> bytes | None:
    try:
        info = zf.getinfo(member)
    except KeyError:
        return None
    if info.file_size > _MAX_ZIP_MEMBER_BYTES:
        raise _ZipLimitExceeded(
            f"Membre OOXML trop volumineux ({info.file_size} octets > {_MAX_ZIP_MEMBER_BYTES}) : {member}."
        )
    if total_budget is not None and (total_budget[0] + info.file_size) > _MAX_ZIP_TOTAL_BYTES:
        raise _ZipLimitExceeded(
            f"Décompression OOXML totale dépassant {_MAX_ZIP_TOTAL_BYTES} octets sur {member}."
        )
    chunks: list[bytes] = []
    member_size = 0
    with zf.open(info, "r") as fh:
        while True:
            chunk = fh.read(65536)
            if not chunk:
                break
            member_size += len(chunk)
            if member_size > _MAX_ZIP_MEMBER_BYTES:
                raise _ZipLimitExceeded(
                    f"Membre OOXML trop volumineux à la décompression (> {_MAX_ZIP_MEMBER_BYTES} octets) : {member}."
                )
            if total_budget is not None:
                total_budget[0] += len(chunk)
                if total_budget[0] > _MAX_ZIP_TOTAL_BYTES:
                    raise _ZipLimitExceeded(
                        f"Décompression OOXML totale dépassant {_MAX_ZIP_TOTAL_BYTES} octets sur {member}."
                    )
            chunks.append(chunk)
    return b"".join(chunks)


def _parse_xml_from_zip(
    zf: zipfile.ZipFile,
    member: str,
    xml_errors: list[str] | None = None,
    total_budget: list[int] | None = None,
) -> ET.Element | None:
    data = _read_zip_member_bounded(zf, member, total_budget=total_budget)
    if data is None:
        return None
    try:
        return ET.fromstring(data)
    except ET.ParseError:
        if xml_errors is not None:
            xml_errors.append(member)
        return None


def _extract_docx_data(path: Path) -> dict[str, object]:
    try:
        zf_ctx = zipfile.ZipFile(path, "r")
    except zipfile.BadZipFile:
        return {"statut": "erreur", "erreur": "Archive OOXML invalide ou corrompue (.docx)."}

    try:
        with zf_ctx as zf:
            total_budget = [0]
            xml_errors: list[str] = []
            core_meta: dict[str, str] = {}
            core = _parse_xml_from_zip(zf, "docProps/core.xml", xml_errors, total_budget)
            if core is not None:
                for tag, label in (
                    (f"{{{_DC_NS}}}creator", "auteur_initial"),
                    (f"{{{_CP_NS}}}lastModifiedBy", "dernier_editeur"),
                    (f"{{{_DCTERMS_NS}}}created", "date_creation"),
                    (f"{{{_DCTERMS_NS}}}modified", "date_modification"),
                    (f"{{{_DC_NS}}}title", "titre"),
                    (f"{{{_DC_NS}}}subject", "objet"),
                ):
                    el = core.find(tag)
                    if el is not None and el.text and el.text.strip():
                        core_meta[label] = el.text.strip()

            app_meta: dict[str, str] = {}
            pages_declarees: int | None = None
            mots_declares: int | None = None
            app = _parse_xml_from_zip(zf, "docProps/app.xml", xml_errors, total_budget)
            if app is not None:
                for tag, label in (
                    (f"{{{_APP_NS}}}Application", "application"),
                    (f"{{{_APP_NS}}}Company", "organisation"),
                    (f"{{{_APP_NS}}}Pages", "pages_declarees"),
                    (f"{{{_APP_NS}}}Words", "mots_declares"),
                ):
                    el = app.find(tag)
                    if el is not None and el.text and el.text.strip():
                        app_meta[label] = el.text.strip()
                if "pages_declarees" in app_meta and app_meta["pages_declarees"].isdigit():
                    pages_declarees = int(app_meta["pages_declarees"])
                if "mots_declares" in app_meta and app_meta["mots_declares"].isdigit():
                    mots_declares = int(app_meta["mots_declares"])

            polices: set[str] = set()
            tailles_pt: set[float] = set()
            interlignes_ratio: set[float] = set()
            interlignes_pt: set[float] = set()

            theme_root = _parse_xml_from_zip(zf, "word/theme/theme1.xml", xml_errors, total_budget)
            theme_fonts: dict[str, str] = {}
            if theme_root is not None:
                major = theme_root.find(f".//{{{_A_NS}}}majorFont/{{{_A_NS}}}latin")
                minor = theme_root.find(f".//{{{_A_NS}}}minorFont/{{{_A_NS}}}latin")
                if major is not None and major.attrib.get("typeface"):
                    theme_fonts["major"] = major.attrib["typeface"]
                if minor is not None and minor.attrib.get("typeface"):
                    theme_fonts["minor"] = minor.attrib["typeface"]

            def _scan_formatting(root: ET.Element | None) -> None:
                if root is None:
                    return
                for rf in root.findall(f".//{{{_W_NS}}}rFonts"):
                    for attr in ("ascii", "hAnsi", "cs", "eastAsia"):
                        val = rf.attrib.get(f"{{{_W_NS}}}{attr}")
                        if val:
                            polices.add(val)
                    for attr in ("asciiTheme", "hAnsiTheme"):
                        tval = rf.attrib.get(f"{{{_W_NS}}}{attr}", "")
                        if tval.startswith("minor") and "minor" in theme_fonts:
                            polices.add(theme_fonts["minor"])
                        elif tval.startswith("major") and "major" in theme_fonts:
                            polices.add(theme_fonts["major"])
                for sz_tag in ("sz", "szCs"):
                    for sz in root.findall(f".//{{{_W_NS}}}{sz_tag}"):
                        raw_val = sz.attrib.get(f"{{{_W_NS}}}val")
                        if raw_val and raw_val.isdigit():
                            tailles_pt.add(round(int(raw_val) / 2.0, 2))
                for sp in root.findall(f".//{{{_W_NS}}}spacing"):
                    raw_line = sp.attrib.get(f"{{{_W_NS}}}line")
                    rule = sp.attrib.get(f"{{{_W_NS}}}lineRule", "auto")
                    if raw_line and raw_line.isdigit():
                        val_i = int(raw_line)
                        if rule == "auto":
                            interlignes_ratio.add(round(val_i / 240.0, 2))
                        else:
                            interlignes_pt.add(round(val_i / 20.0, 2))

            styles_root = _parse_xml_from_zip(zf, "word/styles.xml", xml_errors, total_budget)
            doc_root = _parse_xml_from_zip(zf, "word/document.xml", xml_errors, total_budget)
            extra_roots_map: dict[str, ET.Element] = {}
            for m in zf.namelist():
                if (
                    (m.startswith("word/header") or m.startswith("word/footer"))
                    and m.endswith(".xml")
                ) or m in ("word/footnotes.xml", "word/endnotes.xml"):
                    r_ext = _parse_xml_from_zip(zf, m, xml_errors, total_budget)
                    if r_ext is not None:
                        extra_roots_map[m] = r_ext
            extra_roots = list(extra_roots_map.values())
            doc_trees = [r for r in [doc_root, *extra_roots] if r is not None]

            used_style_ids: set[str] = set()
            for tree in doc_trees:
                for st_tag in ("pStyle", "rStyle", "tblStyle"):
                    for el in tree.findall(f".//{{{_W_NS}}}{st_tag}"):
                        sval = el.attrib.get(f"{{{_W_NS}}}val")
                        if sval:
                            used_style_ids.add(sval)

            used_style_elements: list[ET.Element] = []
            if styles_root is not None:
                doc_defs = styles_root.find(f"{{{_W_NS}}}docDefaults")
                if doc_defs is not None:
                    _scan_formatting(doc_defs)
                    used_style_elements.append(doc_defs)
                styles_by_id: dict[str, ET.Element] = {}
                for st_el in styles_root.findall(f"{{{_W_NS}}}style"):
                    sid = st_el.attrib.get(f"{{{_W_NS}}}styleId")
                    if sid:
                        styles_by_id[sid] = st_el
                        if st_el.attrib.get(f"{{{_W_NS}}}default") == "1":
                            used_style_ids.add(sid)
                resolved_ids = set(used_style_ids)
                frontier = list(used_style_ids)
                for _ in range(10):
                    nxt: list[str] = []
                    for sid in frontier:
                        st_el = styles_by_id.get(sid)
                        if st_el is None:
                            continue
                        based = st_el.find(f"{{{_W_NS}}}basedOn")
                        if based is not None:
                            bval = based.attrib.get(f"{{{_W_NS}}}val")
                            if bval and bval not in resolved_ids:
                                resolved_ids.add(bval)
                                nxt.append(bval)
                    if not nxt:
                        break
                    frontier = nxt
                for sid in sorted(resolved_ids):
                    st_el = styles_by_id.get(sid)
                    _scan_formatting(st_el)
                    if st_el is not None:
                        used_style_elements.append(st_el)

            for tree in doc_trees:
                _scan_formatting(tree)

            vanish_occurrences = 0
            vanish_tags: set[str] = set()
            vanish_excerpts: list[str] = []
            for tree in [*doc_trees, *used_style_elements]:
                for v_tag in _VANISH_TAGS:
                    for el in tree.findall(f".//{{{_W_NS}}}{v_tag}"):
                        if _is_w_flag_enabled(el):
                            vanish_occurrences += 1
                            vanish_tags.add(f"w:{v_tag}")
            for tree in doc_trees:
                for run in tree.findall(f".//{{{_W_NS}}}r"):
                    rpr = run.find(f"{{{_W_NS}}}rPr")
                    if rpr is None:
                        continue
                    if any(
                        _is_w_flag_enabled(fl)
                        for v_tag in _VANISH_TAGS
                        for fl in rpr.findall(f"{{{_W_NS}}}{v_tag}")
                    ):
                        txt = "".join(t.text or "" for t in run.findall(f".//{{{_W_NS}}}t")).strip()
                        if txt and len(vanish_excerpts) < 10:
                            vanish_excerpts.append(_truncate(txt))

            marges_po: dict[str, float] = {}
            format_page_po: dict[str, object] = {}
            if doc_root is not None:
                for pg_mar in doc_root.findall(f".//{{{_W_NS}}}pgMar"):
                    for side, label in (
                        ("top", "haut"),
                        ("bottom", "bas"),
                        ("left", "gauche"),
                        ("right", "droite"),
                    ):
                        raw_twip = pg_mar.attrib.get(f"{{{_W_NS}}}{side}")
                        if raw_twip and raw_twip.lstrip("-").isdigit():
                            val_po = round(int(raw_twip) / 1440.0, 2)
                            if label not in marges_po or val_po < marges_po[label]:
                                marges_po[label] = val_po
                pg_sizes: list[dict[str, object]] = []
                for pg_sz in doc_root.findall(f".//{{{_W_NS}}}pgSz"):
                    w_raw = pg_sz.attrib.get(f"{{{_W_NS}}}w")
                    h_raw = pg_sz.attrib.get(f"{{{_W_NS}}}h")
                    if w_raw and h_raw and w_raw.isdigit() and h_raw.isdigit():
                        w_po = round(int(w_raw) / 1440.0, 2)
                        h_po = round(int(h_raw) / 1440.0, 2)
                        est_portrait_letter = abs(w_po - 8.5) <= 0.1 and abs(h_po - 11.0) <= 0.1
                        est_paysage_letter = abs(w_po - 11.0) <= 0.1 and abs(h_po - 8.5) <= 0.1
                        est_letter = est_portrait_letter or est_paysage_letter
                        orientation = "paysage" if est_paysage_letter or w_po > h_po else "portrait"
                        pg_sizes.append(
                            {
                                "largeur_po": w_po,
                                "hauteur_po": h_po,
                                "us_letter": est_letter,
                                "orientation": orientation,
                            }
                        )
                if pg_sizes:
                    non_letter = [p for p in pg_sizes if not p["us_letter"]]
                    format_page_po = dict(non_letter[0] if non_letter else pg_sizes[0])
                    orientations = sorted({str(p["orientation"]) for p in pg_sizes})
                    if len(orientations) > 1:
                        format_page_po["orientations_detectees"] = orientations
                    if len(pg_sizes) > 1:
                        format_page_po["sections_inspectees"] = len(pg_sizes)

            comments_root = _parse_xml_from_zip(zf, "word/comments.xml", xml_errors, total_budget)
            commentaires: list[dict[str, str]] = []
            if comments_root is not None:
                for com in comments_root.findall(f".//{{{_W_NS}}}comment"):
                    commentaires.append(
                        {
                            "auteur": com.attrib.get(f"{{{_W_NS}}}author", ""),
                            "date": com.attrib.get(f"{{{_W_NS}}}date", ""),
                            "extrait": _truncate("".join(com.itertext()).strip()),
                        }
                    )

            insertions = 0
            suppressions = 0
            rev_authors: set[str] = set()
            rev_roots: list[ET.Element] = []
            if doc_root is not None:
                rev_roots.append(doc_root)
            for m, r_ext in extra_roots_map.items():
                if (m.startswith("word/header") or m.startswith("word/footer")) and m.endswith(".xml"):
                    rev_roots.append(r_ext)
            for root in rev_roots:
                for tag_local in ("ins", "del"):
                    for node in root.findall(f".//{{{_W_NS}}}{tag_local}"):
                        if tag_local == "ins":
                            insertions += 1
                        else:
                            suppressions += 1
                        auth = node.attrib.get(f"{{{_W_NS}}}author")
                        if auth:
                            rev_authors.add(auth)

            corps_illisible = doc_root is None
    except _ZipLimitExceeded as exc:
        return {"statut": "erreur", "erreur": str(exc)}

    return {
        "statut": "ok",
        "format": "docx",
        "details": {
            "corps_illisible": corps_illisible,
            "membres_xml_invalides": xml_errors,
            "pages_declarees": pages_declarees,
            "mots_declares": mots_declares,
            "polices_detectees": sorted(polices),
            "tailles_pt_detectees": sorted(tailles_pt),
            "marges_po": marges_po,
            "format_page_po": format_page_po,
            "interlignes_ratio": sorted(interlignes_ratio),
            "interlignes_pt": sorted(interlignes_pt),
            "nombre_commentaires": len(commentaires),
            "commentaires_apercu": commentaires[:10],
            "texte_masque": {
                "occurrences": vanish_occurrences,
                "balises": sorted(vanish_tags),
                "extraits": vanish_excerpts,
            },
            "marques_revision": {
                "insertions": insertions,
                "suppressions": suppressions,
                "auteurs": sorted(rev_authors),
            },
            "metadonnees": {"core": core_meta, "app": app_meta},
        },
    }


def _decode_pdf_bytes(raw_val: bytes) -> str:
    if raw_val.startswith(b"\xfe\xff"):
        return raw_val[2:].decode("utf-16-be", errors="replace").strip("\x00")
    if raw_val.startswith(b"\xff\xfe"):
        return raw_val[2:].decode("utf-16-le", errors="replace").strip("\x00")
    return raw_val.decode("latin-1", errors="replace").strip("\x00")


def _extract_pdf_literal(blob: bytes, key: bytes) -> str | None:
    pattern = re.compile(
        b"/" + re.escape(key) + rb"\s*(?:\(((?:\\.|[^\\()])*)\)|<([0-9A-Fa-f\s]+)>)"
    )
    m = pattern.search(blob)
    if not m:
        return None
    if m.group(1) is not None:
        raw = m.group(1)
        unescaped = re.sub(
            rb"\\([\\()nrtbf])",
            lambda hit: {
                b"\\": b"\\",
                b"(": b"(",
                b")": b")",
                b"n": b"\n",
                b"r": b"\r",
                b"t": b"\t",
                b"b": b"\b",
                b"f": b"\f",
            }[hit.group(1)],
            raw,
        )
        return _truncate(_decode_pdf_bytes(unescaped), 200)
    hex_str = re.sub(rb"\s+", b"", m.group(2))
    if len(hex_str) % 2 == 1:
        hex_str += b"0"
    try:
        return _truncate(_decode_pdf_bytes(bytes.fromhex(hex_str.decode("ascii"))), 200)
    except ValueError:
        return None


def _extract_pdf_data(path: Path) -> dict[str, object]:
    size = path.stat().st_size
    if size > _MAX_RAW_FILE_BYTES:
        return {
            "statut": "erreur",
            "erreur": f"Fichier PDF trop volumineux ({size} octets > {_MAX_RAW_FILE_BYTES}).",
        }
    raw = path.read_bytes()
    header_m = _PDF_HEADER_RE.search(raw[:1024])
    version = header_m.group(1).decode("ascii") if header_m else "inconnue"
    encrypted = bool(_PDF_ENCRYPT_RE.search(raw))

    text_stream_hits = 0
    objstm_blobs: list[bytes] = []
    objstm_total = 0
    if not encrypted:
        for m in _PDF_STREAM_RE.finditer(raw):
            chunk = m.group(1)
            if len(chunk) > 8_000_000:
                continue
            pre_dict = raw[max(0, m.start() - 320) : m.start()]
            is_objstm = bool(_PDF_OBJSTM_RE.search(pre_dict))
            decompressed = _decompress_zlib_bounded(chunk, _MAX_ZLIB_STREAM_BYTES)
            if is_objstm and decompressed:
                first_m = _PDF_FIRST_RE.search(pre_dict)
                first_off = int(first_m.group(1)) if first_m else 0
                slice_bytes = (
                    decompressed[first_off:] if first_off < len(decompressed) else decompressed
                )
                if objstm_total + len(slice_bytes) <= _MAX_PDF_OBJSTM_TOTAL_BYTES:
                    objstm_blobs.append(slice_bytes)
                    objstm_total += len(slice_bytes)
            else:
                if _PDF_NON_TEXT_STREAM_RE.search(pre_dict):
                    continue
                if decompressed is not None:
                    if _PDF_TEXT_OP_RE.search(decompressed):
                        text_stream_hits += 1
                elif not _PDF_FILTER_RE.search(pre_dict):
                    if _PDF_TEXT_OP_RE.search(chunk):
                        text_stream_hits += 1

    struct_blob = raw if not objstm_blobs else (raw + b"\n" + b"\n".join(objstm_blobs))

    page_hits = len(_PDF_PAGE_RE.findall(struct_blob))
    if page_hits == 0:
        cnt_m = _PDF_PAGES_COUNT_RE.search(struct_blob)
        if cnt_m:
            page_hits = int(cnt_m.group(1))

    outlines_ref = bool(_PDF_OUTLINES_RE.search(struct_blob))
    outline_dicts = _PDF_OUTLINES_DICT_RE.findall(struct_blob)
    outline_items = len(_PDF_OUTLINE_ITEM_DICT_RE.findall(struct_blob))
    outlines_has_first = any(bool(_PDF_OUTLINE_FIRST_RE.search(d)) for d in outline_dicts)
    outlines_nonempty_count = any(
        (cm := _PDF_OUTLINE_COUNT_RE.search(d)) is not None and int(cm.group(1)) > 0
        for d in outline_dicts
    )
    if outline_items > 0:
        has_outlines = outlines_ref or bool(outline_dicts)
        outline_titles = outline_items
    elif outline_dicts:
        has_outlines = outlines_has_first or outlines_nonempty_count
        outline_titles = 0
    else:
        has_outlines = outlines_ref
        outline_titles = 0

    link_count = len(_PDF_LINK_RE.findall(struct_blob))
    uris = [
        _truncate(_decode_pdf_bytes(m.group(1)), 200)
        for m in _PDF_URI_RE.finditer(struct_blob)
    ][:50]

    format_page_po: dict[str, object] = {}
    mediaboxes: list[dict[str, object]] = []
    for mb in _PDF_MEDIABOX_RE.finditer(struct_blob):
        x0, y0, x1, y1 = (float(mb.group(i)) for i in range(1, 5))
        w_po = round(abs(x1 - x0) / 72.0, 2)
        h_po = round(abs(y1 - y0) / 72.0, 2)
        est_portrait_letter = abs(w_po - 8.5) <= 0.1 and abs(h_po - 11.0) <= 0.1
        est_paysage_letter = abs(w_po - 11.0) <= 0.1 and abs(h_po - 8.5) <= 0.1
        est_letter = est_portrait_letter or est_paysage_letter
        orientation = "paysage" if est_paysage_letter or w_po > h_po else "portrait"
        mediaboxes.append(
            {
                "largeur_po": w_po,
                "hauteur_po": h_po,
                "us_letter": est_letter,
                "orientation": orientation,
            }
        )
    if mediaboxes:
        non_letter = [mb for mb in mediaboxes if not mb["us_letter"]]
        format_page_po = dict(non_letter[0] if non_letter else mediaboxes[0])
        orientations = sorted({str(mb["orientation"]) for mb in mediaboxes})
        if len(orientations) > 1:
            format_page_po["orientations_detectees"] = orientations

    meta: dict[str, str] = {}
    for key, label in (
        (b"Title", "Title"),
        (b"Author", "Author"),
        (b"Subject", "Subject"),
        (b"Keywords", "Keywords"),
        (b"Creator", "Creator"),
        (b"Producer", "Producer"),
        (b"CreationDate", "CreationDate"),
        (b"ModDate", "ModDate"),
    ):
        val = _extract_pdf_literal(struct_blob, key)
        if val:
            meta[label] = val

    couche = "chiffree" if encrypted else ("detectee" if text_stream_hits > 0 else "absente")
    return {
        "statut": "ok",
        "format": "pdf",
        "details": {
            "version_pdf": version,
            "chiffre": encrypted,
            "nombre_pages": page_hits,
            "couche_texte": couche,
            "flux_texte_detectes": text_stream_hits,
            "signets_presents": has_outlines,
            "titres_signets_detectes": outline_titles,
            "nombre_liens": link_count,
            "uris_apercu": uris,
            "format_page_po": format_page_po,
            "metadonnees": meta,
        },
    }


def _charger_regles(regles_arg: str | None, overrides: dict[str, object]) -> tuple[str | None, dict[str, object]]:
    etiquette: str | None = None
    seuils: dict[str, object] = {}
    if regles_arg:
        cand = Path(regles_arg)
        if cand.is_file():
            loaded = json.loads(cand.read_text(encoding="utf-8"))
            if not isinstance(loaded, dict):
                raise ValueError(f"{regles_arg} : objet JSON attendu.")
            etiquette = str(loaded.get("nom") or cand.stem)
            seuils.update(loaded)
        elif regles_arg.lower().endswith(".json") or "/" in regles_arg or "\\" in regles_arg:
            raise FileNotFoundError(f"Fichier de règles introuvable : {regles_arg}")
        else:
            etiquette = regles_arg
    for k, v in overrides.items():
        if v is not None and v != [] and v is not False:
            seuils[k] = v
    return etiquette, seuils


def controler_fichier(
    path: Path,
    regles: dict[str, object] | None = None,
    etiquette_regles: str | None = None,
) -> dict[str, object]:
    """Inspecte un document (.docx ou .pdf) et génère les constats + bon de travail."""
    seuils = dict(regles or {})
    if not path.is_file():
        return {"chemin": str(path), "statut": "erreur", "erreur": "Fichier introuvable."}

    ext = path.suffix.lower()
    if ext in _DOCX_EXTS:
        brut = _extract_docx_data(path)
    elif ext in _PDF_EXTS:
        brut = _extract_pdf_data(path)
    else:
        return {
            "chemin": str(path),
            "statut": "erreur",
            "erreur": f"Format non pris en charge par controler_document.py ({ext}). Attendu : .docx ou .pdf.",
        }

    if brut.get("statut") != "ok":
        return {"chemin": str(path), **brut}

    details: dict[str, object] = dict(brut["details"])  # type: ignore[arg-type]
    fmt = str(brut["format"])
    constats: list[dict[str, object]] = []
    bon_de_travail: list[dict[str, str]] = []

    def _add_action(code: str, priorite: str, outil: str, action: str, detail: str) -> None:
        bon_de_travail.append(
            {
                "code": code,
                "priorite": priorite,
                "outil_cabinet": outil,
                "action": action,
                "detail": detail,
            }
        )

    seuils_fournis = any(
        k in seuils
        for k in (
            "max_pages",
            "polices_attendues",
            "taille_min_pt",
            "taille_max_pt",
            "marge_min_po",
            "interligne_min",
            "exiger_couche_texte",
            "exiger_signets",
        )
    )
    if not seuils_fournis:
        constats.append(
            {
                "controle": "seuils_reglementaires",
                "statut": "A_VERIFIER",
                "observe": etiquette_regles or "aucun seuil transmis",
                "attendu": "Lire le règlement du tribunal saisi via `lois` et fournir --regles / options.",
            }
        )

    max_pages = seuils.get("max_pages")
    if fmt == "docx":
        corps_illisible = bool(details.get("corps_illisible"))
        membres_inv = list(details.get("membres_xml_invalides", []))  # type: ignore[arg-type]
        if corps_illisible or membres_inv:
            constats.append(
                {
                    "controle": "integrite_ooxml",
                    "statut": "A_VERIFIER",
                    "observe": {
                        "corps_illisible": corps_illisible,
                        "membres_xml_invalides": membres_inv,
                    },
                    "attendu": "XML OOXML sain (sans membre illisible ou entités récursives)",
                }
            )
            _add_action(
                "CORPS_XML_ILLISIBLE",
                "CRITIQUE",
                "Microsoft Word / Inspecteur de document",
                "Ouvrir, réparer et réenregistrer le .docx : un flux XML requis n'a pas pu être contrôlé",
                f"Corps illisible={corps_illisible} ; membres XML invalides : {', '.join(membres_inv) or 'word/document.xml'}.",
            )

        texte_masque = dict(details.get("texte_masque", {}))  # type: ignore[arg-type]
        nb_masque = int(texte_masque.get("occurrences", 0))  # type: ignore[arg-type]
        if nb_masque > 0:
            constats.append(
                {
                    "controle": "texte_masque",
                    "statut": "NON_CONFORME",
                    "observe": texte_masque,
                    "attendu": "0 occurrence de texte masqué (w:vanish / w:specVanish / w:webHidden)",
                }
            )
            _add_action(
                "SUPPRIMER_TEXTE_MASQUE",
                "CRITIQUE",
                "Microsoft Word / Inspecteur de document",
                f"Supprimer les {nb_masque} occurrence(s) de texte masqué avant toute exportation",
                f"Balises détectées : {', '.join(texte_masque.get('balises', []))}.",
            )

        pages = details.get("pages_declarees")
        if max_pages is not None:
            if pages is None:
                constats.append(
                    {
                        "controle": "nombre_pages",
                        "statut": "A_VERIFIER",
                        "observe": "absent de docProps/app.xml",
                        "attendu": f"<= {max_pages}",
                    }
                )
                _add_action(
                    "VERIFIER_PAGINATION",
                    "HAUTE",
                    "Microsoft Word",
                    "Vérifier le nombre de pages réel à l'ouverture dans Word",
                    f"docProps/app.xml ne déclare pas le nombre de pages (plafond demandé : {max_pages}).",
                )
            elif int(pages) > int(max_pages):  # type: ignore[arg-type]
                constats.append(
                    {
                        "controle": "nombre_pages",
                        "statut": "NON_CONFORME",
                        "observe": pages,
                        "attendu": f"<= {max_pages}",
                    }
                )
                _add_action(
                    "REDUIRE_PAGINATION",
                    "CRITIQUE",
                    "Microsoft Word",
                    f"Ramener le document à {max_pages} pages ou moins",
                    f"Pages déclarées : {pages} (plafond : {max_pages}).",
                )
            else:
                constats.append(
                    {
                        "controle": "nombre_pages",
                        "statut": "OK",
                        "observe": pages,
                        "attendu": f"<= {max_pages}",
                    }
                )

        nb_com = int(details.get("nombre_commentaires", 0))  # type: ignore[arg-type]
        if nb_com > 0:
            constats.append(
                {
                    "controle": "commentaires_caches",
                    "statut": "NON_CONFORME",
                    "observe": nb_com,
                    "attendu": 0,
                }
            )
            _add_action(
                "SUPPRIMER_COMMENTAIRES",
                "CRITIQUE",
                "Microsoft Word",
                f"Supprimer les {nb_com} commentaires avant toute exportation ou transmission",
                "Risque de divulgation de stratégie ou de notes internes.",
            )

        rev = dict(details.get("marques_revision", {}))  # type: ignore[arg-type]
        nb_rev = int(rev.get("insertions", 0)) + int(rev.get("suppressions", 0))
        if nb_rev > 0:
            constats.append(
                {
                    "controle": "marques_revision",
                    "statut": "NON_CONFORME",
                    "observe": rev,
                    "attendu": "0 insertion/suppression",
                }
            )
            _add_action(
                "ACCEPTER_OU_REJETER_REVISIONS",
                "CRITIQUE",
                "Microsoft Word",
                "Accepter ou rejeter toutes les marques de révision et désactiver le suivi",
                f"{rev.get('insertions', 0)} insertion(s), {rev.get('suppressions', 0)} suppression(s).",
            )

        meta = dict(details.get("metadonnees", {}))  # type: ignore[arg-type]
        core_m = meta.get("core", {})
        if isinstance(core_m, dict) and (core_m.get("auteur_initial") or core_m.get("dernier_editeur")):
            _add_action(
                "PURGER_METADONNEES",
                "MOYENNE",
                "Microsoft Word / Inspecteur de document",
                "Contrôler et purger les propriétés personnelles (auteur, organisation) avant dépôt",
                f"Propriétés détectées : {', '.join(sorted(core_m.keys()))}.",
            )

        polices_obs = list(details.get("polices_detectees", []))  # type: ignore[arg-type]
        polices_att = seuils.get("polices_attendues")
        if isinstance(polices_att, list) and polices_att:
            att_lower = {str(p).lower() for p in polices_att}
            non_conf = [p for p in polices_obs if str(p).lower() not in att_lower]
            if non_conf or not polices_obs:
                constats.append(
                    {
                        "controle": "police",
                        "statut": "NON_CONFORME" if non_conf else "A_VERIFIER",
                        "observe": polices_obs,
                        "attendu": polices_att,
                    }
                )
                _add_action(
                    "HARMONISER_POLICE",
                    "HAUTE",
                    "Microsoft Word",
                    f"Uniformiser la police vers {', '.join(str(x) for x in polices_att)}",
                    f"Polices détectées dans le XML : {polices_obs or ['aucune détectée']}.",
                )

        tailles_obs = list(details.get("tailles_pt_detectees", []))  # type: ignore[arg-type]
        t_min = seuils.get("taille_min_pt")
        t_max = seuils.get("taille_max_pt")
        if t_min is not None or t_max is not None:
            hors = [
                t
                for t in tailles_obs
                if (t_min is not None and float(t) < float(t_min))
                or (t_max is not None and float(t) > float(t_max))
            ]
            if hors:
                constats.append(
                    {
                        "controle": "taille_police_pt",
                        "statut": "NON_CONFORME",
                        "observe": tailles_obs,
                        "attendu": {"min_pt": t_min, "max_pt": t_max},
                    }
                )
                _add_action(
                    "AJUSTER_TAILLE_POLICE",
                    "HAUTE",
                    "Microsoft Word",
                    "Corriger les tailles de police hors gabarit réglementaire (vérifier corps vs notes)",
                    f"Tailles hors plage détectées : {hors} pt.",
                )

        marges_obs = dict(details.get("marges_po", {}))  # type: ignore[arg-type]
        m_min = seuils.get("marge_min_po")
        if m_min is not None and marges_obs:
            petites = {k: v for k, v in marges_obs.items() if float(v) < float(m_min)}
            if petites:
                constats.append(
                    {
                        "controle": "marges_po",
                        "statut": "NON_CONFORME",
                        "observe": marges_obs,
                        "attendu": f">= {m_min} po",
                    }
                )
                _add_action(
                    "AJUSTER_MARGES",
                    "HAUTE",
                    "Microsoft Word",
                    f"Porter les marges insuffisantes à au moins {m_min} po",
                    f"Marges sous le seuil : {petites}.",
                )

        ratios_obs = list(details.get("interlignes_ratio", []))  # type: ignore[arg-type]
        pts_obs = list(details.get("interlignes_pt", []))  # type: ignore[arg-type]
        i_min = seuils.get("interligne_min")
        if i_min is not None:
            bas = [r for r in ratios_obs if float(r) < float(i_min)]
            min_pt_ref = min((float(t) for t in tailles_obs), default=12.0)
            bas_pt = [p for p in pts_obs if min_pt_ref > 0 and (float(p) / min_pt_ref) < float(i_min)]
            if bas or bas_pt:
                constats.append(
                    {
                        "controle": "interligne",
                        "statut": "NON_CONFORME",
                        "observe": {"ratio": ratios_obs, "pt": pts_obs},
                        "attendu": f">= {i_min}",
                    }
                )
                _add_action(
                    "AJUSTER_INTERLIGNE",
                    "HAUTE",
                    "Microsoft Word",
                    f"Régler l'interligne du texte courant à au moins {i_min}",
                    f"Interlignes sous le seuil : ratio={bas}, exact/min_pt={bas_pt}.",
                )

    elif fmt == "pdf":
        pages = int(details.get("nombre_pages", 0))  # type: ignore[arg-type]
        if max_pages is not None and not details.get("chiffre") and pages > int(max_pages):  # type: ignore[arg-type]
            constats.append(
                {
                    "controle": "nombre_pages",
                    "statut": "NON_CONFORME",
                    "observe": pages,
                    "attendu": f"<= {max_pages}",
                }
            )
            _add_action(
                "REDUIRE_PAGINATION",
                "CRITIQUE",
                "Word / Éditeur PDF",
                f"Réduire le document PDF à {max_pages} pages maximum",
                f"{pages} page(s) détectée(s).",
            )

        if details.get("chiffre"):
            constats.append(
                {
                    "controle": "chiffrement_pdf",
                    "statut": "NON_CONFORME",
                    "observe": True,
                    "attendu": False,
                }
            )
            _add_action(
                "DECHIFFRER_PDF",
                "CRITIQUE",
                "Adobe Acrobat / outil PDF",
                "Retirer le mot de passe / chiffrement avant dépôt au greffe numérique",
                "Un PDF chiffré bloque la lecture de la couche texte, des signets et l'indexation au dépôt.",
            )
        else:
            if details.get("couche_texte") == "absente":
                statut_ocr = "NON_CONFORME" if seuils.get("exiger_couche_texte") else "ALERTE"
                constats.append(
                    {
                        "controle": "couche_texte_ocr",
                        "statut": statut_ocr,
                        "observe": "absente",
                        "attendu": "detectee",
                    }
                )
                _add_action(
                    "APPLIQUER_OCR",
                    "CRITIQUE" if statut_ocr == "NON_CONFORME" else "HAUTE",
                    "Adobe Acrobat / outil OCR du cabinet",
                    "Exécuter une reconnaissance optique de caractères (OCR) sur le PDF",
                    "Aucune couche texte détectée (numérisation image seule).",
                )

            if not details.get("signets_presents"):
                statut_sig = "NON_CONFORME" if seuils.get("exiger_signets") else "ALERTE"
                constats.append(
                    {
                        "controle": "signets_outlines",
                        "statut": statut_sig,
                        "observe": False,
                        "attendu": True,
                    }
                )
                _add_action(
                    "AJOUTER_SIGNETS",
                    "HAUTE" if statut_sig == "NON_CONFORME" else "MOYENNE",
                    "Adobe Acrobat / outil PDF du cabinet",
                    "Créer les signets (/Outlines) par section, onglet ou cote de pièce",
                    "Aucun signet exploitable détecté dans le PDF.",
                )

    fmt_page = details.get("format_page_po")
    if isinstance(fmt_page, dict) and fmt_page.get("us_letter") is False:
        constats.append(
            {
                "controle": "format_papier",
                "statut": "ALERTE",
                "observe": fmt_page,
                "attendu": "US Letter 8.5 x 11 po",
            }
        )
        _add_action(
            "CONVERTIR_FORMAT_LETTRE",
            "HAUTE",
            "Word / Éditeur PDF",
            "Vérifier et convertir le format de page en US Letter (8,5 x 11 po)",
            f"Format détecté : {fmt_page.get('largeur_po')} x {fmt_page.get('hauteur_po')} po.",
        )

    statuts = {str(c.get("statut")) for c in constats}
    if "NON_CONFORME" in statuts:
        statut_global = "NON_CONFORME"
    elif "ALERTE" in statuts:
        statut_global = "AVERTISSEMENT"
    elif "A_VERIFIER" in statuts:
        statut_global = "A_VERIFIER"
    else:
        statut_global = "CONFORME"

    return {
        "chemin": str(path),
        "nom": path.name,
        "format": fmt,
        "statut": "ok",
        "statut_conformite": statut_global,
        "regles_etiquette": etiquette_regles,
        "details": details,
        "constats": constats,
        "bon_de_travail": bon_de_travail,
    }


def _format_texte(resultats: list[dict[str, object]]) -> str:
    lignes: list[str] = []
    for item in resultats:
        lignes.append(f"=== {item.get('chemin')} ===")
        if item.get("statut") != "ok":
            lignes.append(f"ERREUR : {item.get('erreur')}")
            lignes.append("")
            continue
        lignes.append(
            f"Format : {item['format']} | Conformité : {item['statut_conformite']}"
            + (f" | Règles : {item['regles_etiquette']}" if item.get("regles_etiquette") else "")
        )
        constats = list(item.get("constats") or [])
        if constats:
            lignes.append("Constats :")
            for c in constats:
                lignes.append(
                    f"  - [{c['statut']}] {c['controle']} : observé={c['observe']} (attendu={c['attendu']})"
                )
        actions = list(item.get("bon_de_travail") or [])
        if actions:
            lignes.append("Bon de travail (transformations à faire dans les outils du cabinet) :")
            for idx, act in enumerate(actions, start=1):
                lignes.append(
                    f"  {idx}. [{act['priorite']}] {act['code']} ({act['outil_cabinet']}) — {act['action']}"
                )
                lignes.append(f"     Détail : {act['detail']}")
        else:
            lignes.append("Bon de travail : aucune action requise.")
        lignes.append("")
    return "\n".join(lignes)


def main(argv: list[str] | None = None) -> int:
    _configure_stdio()
    parser = argparse.ArgumentParser(
        description="Vérifier la conformité formelle d'un .docx ou .pdf et produire un bon de travail."
    )
    parser.add_argument("fichiers", nargs="+", help="Chemins des fichiers (.docx ou .pdf).")
    parser.add_argument(
        "--regles",
        default=None,
        help="Chemin d'un fichier JSON de seuils lus via `lois` ou étiquette du tribunal.",
    )
    parser.add_argument("--max-pages", type=int, default=None, help="Plafond de pages autorisé.")
    parser.add_argument(
        "--police-attendue",
        action="append",
        default=[],
        help="Police autorisée (répétable).",
    )
    parser.add_argument("--taille-min-pt", type=float, default=None, help="Taille minimale en points.")
    parser.add_argument("--taille-max-pt", type=float, default=None, help="Taille maximale en points.")
    parser.add_argument("--marge-min-po", type=float, default=None, help="Marge minimale en pouces.")
    parser.add_argument("--interligne-min", type=float, default=None, help="Interligne minimal (ratio).")
    parser.add_argument(
        "--exiger-couche-texte",
        action="store_true",
        help="Exiger une couche texte (OCR) dans un PDF.",
    )
    parser.add_argument(
        "--exiger-signets",
        action="store_true",
        help="Exiger des signets (/Outlines) dans un PDF.",
    )
    parser.add_argument("--json", action="store_true", help="Afficher le résultat au format JSON.")
    args = parser.parse_args(argv)

    overrides: dict[str, object] = {
        "max_pages": args.max_pages,
        "polices_attendues": args.police_attendue,
        "taille_min_pt": args.taille_min_pt,
        "taille_max_pt": args.taille_max_pt,
        "marge_min_po": args.marge_min_po,
        "interligne_min": args.interligne_min,
        "exiger_couche_texte": args.exiger_couche_texte,
        "exiger_signets": args.exiger_signets,
    }
    try:
        etiquette, seuils = _charger_regles(args.regles, overrides)
    except Exception as exc:
        print(f"Erreur de lecture des règles : {exc}", file=sys.stderr)
        return 2

    resultats = [
        controler_fichier(Path(f), regles=seuils, etiquette_regles=etiquette)
        for f in args.fichiers
    ]
    if args.json:
        print(json.dumps(resultats, ensure_ascii=False, indent=2))
    else:
        print(_format_texte(resultats), end="")

    if any(r.get("statut") != "ok" for r in resultats):
        return 2
    if any(r.get("statut_conformite") in ("NON_CONFORME", "A_VERIFIER") for r in resultats):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
