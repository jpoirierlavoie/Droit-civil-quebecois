#!/usr/bin/env python3
"""Inspecteur local des métadonnées et structures cachées des pièces (.docx, .xlsx, .eml, .pdf, images, audio/vidéo).

Bibliothèque standard Python uniquement, lecture seule (hors option explicite --journal), aucun appel réseau.
Usage : python scripts/inspecter_piece.py <fichier>... [--journal chemin.json] [--source "..."] [--json]
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from email import policy
from email.parser import BytesParser
import hashlib
import json
import mimetypes
from pathlib import Path
import re
import struct
import sys
import xml.etree.ElementTree as ET
import zipfile
import zlib

_DOCX_EXTS = {".docx", ".docm"}
_XLSX_EXTS = {".xlsx", ".xlsm"}
_EML_EXTS = {".eml"}
_PDF_EXTS = {".pdf"}
_JPEG_EXTS = {".jpg", ".jpeg"}
_PNG_EXTS = {".png"}
_WAV_EXTS = {".wav"}
_MP3_EXTS = {".mp3"}
_MP4_EXTS = {".mp4", ".m4a", ".mov"}

_W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
_DC_NS = "http://purl.org/dc/elements/1.1/"
_CP_NS = "http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
_DCTERMS_NS = "http://purl.org/dc/terms/"
_APP_NS = "http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"
_MAIN_SS_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
_REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"

_PDF_HEADER_RE = re.compile(rb"%PDF-(\d+\.\d+)")
_PDF_PAGE_RE = re.compile(rb"/Type\s*/Page(?![A-Za-z])")
_PDF_ENCRYPT_RE = re.compile(rb"/Encrypt\b")
_PDF_ANNOTS_RE = re.compile(rb"/Annots\b")
_PDF_ACROFORM_RE = re.compile(rb"/AcroForm\b")
_PDF_SIG_RE = re.compile(rb"/Type\s*/Sig\b|/FT\s*/Sig\b")
_PDF_STREAM_RE = re.compile(rb"stream(?:\r\n|\n)(.*?)(?:\r\n|\r|\n)?endstream", re.S)
_PDF_TEXT_OP_RE = re.compile(rb"\bBT\b.*?(?:\bTj\b|\bTJ\b)", re.S)
_PDF_OBJSTM_RE = re.compile(rb"/Type\s*/ObjStm\b")
_PDF_FIRST_RE = re.compile(rb"/First\s+(\d+)")

_MP4_EPOCH_OFFSET = 2082844800  # secondes entre 1904-01-01 et 1970-01-01


def _configure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconf = getattr(stream, "reconfigure", None)
        if callable(reconf):
            reconf(encoding="utf-8", errors="replace")


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _truncate(text: str, limit: int = 120) -> str:
    cleaned = " ".join(text.split())
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 1] + "…"


def _parse_xml_from_zip(
    zf: zipfile.ZipFile, member: str, xml_errors: list[str] | None = None
) -> ET.Element | None:
    try:
        data = zf.read(member)
    except KeyError:
        return None
    try:
        return ET.fromstring(data)
    except ET.ParseError:
        if xml_errors is not None:
            xml_errors.append(member)
        return None


def _extract_ooxml_props(zf: zipfile.ZipFile) -> dict[str, str]:
    props: dict[str, str] = {}
    core = _parse_xml_from_zip(zf, "docProps/core.xml")
    if core is not None:
        mapping = {
            f"{{{_DC_NS}}}creator": "auteur_initial",
            f"{{{_CP_NS}}}lastModifiedBy": "dernier_editeur",
            f"{{{_DCTERMS_NS}}}created": "date_creation",
            f"{{{_DCTERMS_NS}}}modified": "date_modification",
            f"{{{_DC_NS}}}title": "titre",
            f"{{{_DC_NS}}}subject": "objet",
            f"{{{_CP_NS}}}revision": "revision",
        }
        for tag, label in mapping.items():
            el = core.find(tag)
            if el is not None and el.text and el.text.strip():
                props[label] = el.text.strip()

    app = _parse_xml_from_zip(zf, "docProps/app.xml")
    if app is not None:
        app_map = {
            f"{{{_APP_NS}}}Application": "application",
            f"{{{_APP_NS}}}Company": "organisation",
            f"{{{_APP_NS}}}TotalTime": "temps_edition_min",
            f"{{{_APP_NS}}}Pages": "pages_declarees",
            f"{{{_APP_NS}}}Words": "mots_declares",
        }
        for tag, label in app_map.items():
            el = app.find(tag)
            if el is not None and el.text and el.text.strip():
                props[label] = el.text.strip()
    return props


def _inspect_docx(path: Path) -> dict[str, object]:
    indicateurs: list[str] = []
    details: dict[str, object] = {}

    try:
        zf_ctx = zipfile.ZipFile(path, "r")
    except zipfile.BadZipFile:
        return {
            "statut": "erreur",
            "erreur": "Archive OOXML invalide ou corrompue (.docx).",
        }

    with zf_ctx as zf:
        xml_errors: list[str] = []
        details["proprietes"] = _extract_ooxml_props(zf)

        comments_root = _parse_xml_from_zip(zf, "word/comments.xml", xml_errors)
        commentaires: list[dict[str, str]] = []
        if comments_root is not None:
            for com in comments_root.findall(f".//{{{_W_NS}}}comment"):
                author = com.attrib.get(f"{{{_W_NS}}}author", "")
                cdate = com.attrib.get(f"{{{_W_NS}}}date", "")
                texte = "".join(com.itertext()).strip()
                commentaires.append(
                    {
                        "auteur": author,
                        "date": cdate,
                        "extrait": _truncate(texte),
                    }
                )
        details["nombre_commentaires"] = len(commentaires)
        if commentaires:
            indicateurs.append("COMMENTAIRES_WORD")
            details["commentaires_apercu"] = commentaires[:15]

        insertions = 0
        suppressions = 0
        rev_authors: set[str] = set()
        xml_targets = [
            name
            for name in zf.namelist()
            if name == "word/document.xml"
            or (name.startswith("word/header") and name.endswith(".xml"))
            or (name.startswith("word/footer") and name.endswith(".xml"))
        ]
        for member in xml_targets:
            root = _parse_xml_from_zip(zf, member, xml_errors)
            if root is None:
                continue
            for tag_local, counter_kind in (("ins", "ins"), ("del", "del")):
                for node in root.findall(f".//{{{_W_NS}}}{tag_local}"):
                    if counter_kind == "ins":
                        insertions += 1
                    else:
                        suppressions += 1
                    author = node.attrib.get(f"{{{_W_NS}}}author")
                    if author:
                        rev_authors.add(author)

        details["marques_revision"] = {
            "insertions": insertions,
            "suppressions": suppressions,
            "auteurs": sorted(rev_authors),
        }
        if insertions or suppressions:
            indicateurs.append("MARQUES_DE_REVISION")

        rels_root = _parse_xml_from_zip(zf, "word/_rels/settings.xml.rels", xml_errors)
        attached_templates: list[str] = []
        if rels_root is not None:
            for rel in rels_root:
                rel_type = rel.attrib.get("Type", "")
                if rel_type.endswith("/attachedTemplate"):
                    target = rel.attrib.get("Target", "")
                    if target:
                        attached_templates.append(target)
        if attached_templates:
            indicateurs.append("MODELE_ATTACHE")
            details["modeles_attaches"] = attached_templates

        if xml_errors:
            indicateurs.append("XML_CORROMPU")
            details["membres_xml_invalides"] = xml_errors

    return {
        "statut": "ok",
        "indicateurs": indicateurs,
        "details": details,
    }


def _inspect_xlsx(path: Path) -> dict[str, object]:
    indicateurs: list[str] = []
    details: dict[str, object] = {}

    try:
        zf_ctx = zipfile.ZipFile(path, "r")
    except zipfile.BadZipFile:
        return {
            "statut": "erreur",
            "erreur": "Archive OOXML invalide ou corrompue (.xlsx).",
        }

    with zf_ctx as zf:
        xml_errors: list[str] = []
        details["proprietes"] = _extract_ooxml_props(zf)

        wb_root = _parse_xml_from_zip(zf, "xl/workbook.xml", xml_errors)
        rels_root = _parse_xml_from_zip(zf, "xl/_rels/workbook.xml.rels", xml_errors)
        rel_targets: dict[str, str] = {}
        if rels_root is not None:
            for rel in rels_root:
                rid = rel.attrib.get("Id")
                target = rel.attrib.get("Target", "")
                if rid:
                    norm = target.lstrip("/")
                    if not norm.startswith("xl/"):
                        norm = f"xl/{norm}"
                    rel_targets[rid] = norm

        feuilles: list[dict[str, str]] = []
        target_to_sheet: dict[str, str] = {}
        has_hidden = False
        if wb_root is not None:
            for sheet in wb_root.findall(f".//{{{_MAIN_SS_NS}}}sheet"):
                name = sheet.attrib.get("name", "")
                state = sheet.attrib.get("state", "visible")
                rid = sheet.attrib.get(f"{{{_REL_NS}}}id", "")
                if state != "visible":
                    has_hidden = True
                feuilles.append({"nom": name, "etat": state})
                if rid in rel_targets:
                    target_to_sheet[rel_targets[rid]] = name

        details["feuilles"] = feuilles
        if has_hidden:
            indicateurs.append("FEUILLES_CACHEES")

        sheet_members = sorted(
            name
            for name in zf.namelist()
            if name.startswith("xl/worksheets/") and name.endswith(".xml")
        )
        formula_count = 0
        formula_samples: list[dict[str, str]] = []
        cell_count = 0
        for member in sheet_members:
            ws_root = _parse_xml_from_zip(zf, member, xml_errors)
            if ws_root is None:
                continue
            sheet_label = target_to_sheet.get(member, Path(member).stem)
            for cell in ws_root.findall(f".//{{{_MAIN_SS_NS}}}c"):
                cell_count += 1
                f_el = cell.find(f"{{{_MAIN_SS_NS}}}f")
                if f_el is not None:
                    formula_count += 1
                    if len(formula_samples) < 15:
                        ref = cell.attrib.get("r", "?")
                        expr = f_el.text or "(formule partagée ou matricielle)"
                        formula_samples.append(
                            {
                                "cellule": f"{sheet_label}!{ref}",
                                "formule": _truncate(f"={expr}", 100),
                            }
                        )

        details["nombre_cellules"] = cell_count
        details["nombre_formules"] = formula_count
        if formula_samples:
            details["echantillon_formules"] = formula_samples
        if formula_count > 0:
            indicateurs.append("FORMULES_PRESENTES")

        ext_links: list[str] = []
        for name in zf.namelist():
            if name.startswith("xl/externalLinks/_rels/") and name.endswith(".rels"):
                ext_root = _parse_xml_from_zip(zf, name, xml_errors)
                if ext_root is not None:
                    for rel in ext_root:
                        target = rel.attrib.get("Target")
                        if target:
                            ext_links.append(target)
        details["liens_externes"] = ext_links
        if ext_links:
            indicateurs.append("LIENS_EXTERNES")

        comment_files = [
            name
            for name in zf.namelist()
            if (name.startswith("xl/comments") or name.startswith("xl/threadedComments/"))
            and name.endswith(".xml")
        ]
        comment_count = 0
        for member in comment_files:
            c_root = _parse_xml_from_zip(zf, member, xml_errors)
            if c_root is None:
                continue
            comment_count += len(c_root.findall(f".//{{{_MAIN_SS_NS}}}comment"))
            comment_count += len(
                [el for el in c_root.iter() if el.tag.endswith("}threadedComment")]
            )
        details["nombre_commentaires"] = comment_count
        if comment_count > 0:
            indicateurs.append("COMMENTAIRES_TABLEUR")
        if xml_errors:
            indicateurs.append("XML_CORROMPU")
            details["membres_xml_invalides"] = xml_errors

    return {
        "statut": "ok",
        "indicateurs": indicateurs,
        "details": details,
    }


def _inspect_eml(path: Path) -> dict[str, object]:
    indicateurs: list[str] = []
    raw = path.read_bytes()
    msg = BytesParser(policy=policy.default).parsebytes(raw)

    headers_keys = (
        "From",
        "To",
        "Cc",
        "Bcc",
        "Reply-To",
        "Date",
        "Subject",
        "Message-ID",
        "In-Reply-To",
        "References",
        "X-Unsent",
    )
    en_tetes: dict[str, str] = {}
    for key in headers_keys:
        try:
            val = msg.get(key)
            if val is not None:
                en_tetes[key] = _truncate(str(val), 200)
        except Exception:
            raw_hdrs = [v for k, v in msg.raw_items() if k.lower() == key.lower()]
            if raw_hdrs:
                en_tetes[key] = _truncate(str(raw_hdrs[0]), 200)

    received_headers = msg.get_all("Received") or []
    received_count = len(received_headers)

    if en_tetes.get("X-Unsent") == "1" or (
        received_count == 0 and not en_tetes.get("Message-ID")
    ):
        indicateurs.append("BROUILLON_PROBABLE")
    if en_tetes.get("Bcc"):
        indicateurs.append("COPIE_CONFORME_INVISIBLE")
    if en_tetes.get("In-Reply-To") or en_tetes.get("References"):
        indicateurs.append("COURRIEL_DANS_CHAINE")
    if (
        en_tetes.get("Reply-To")
        and en_tetes.get("From")
        and en_tetes["Reply-To"].lower() != en_tetes["From"].lower()
    ):
        indicateurs.append("ADRESSE_REPONSE_DIFFERENTE")

    pieces_jointes: list[dict[str, object]] = []
    for part in msg.walk():
        if part.is_multipart():
            continue
        disp = part.get_content_disposition()
        filename = part.get_filename()
        ctype = part.get_content_type()
        if filename or disp == "attachment" or (
            ctype not in ("text/plain", "text/html") and disp is not None
        ):
            payload = part.get_payload(decode=True)
            size = len(payload) if payload is not None else 0
            pieces_jointes.append(
                {
                    "nom": filename or "(sans nom)",
                    "type_mime": ctype,
                    "disposition": disp or "",
                    "taille_octets": size,
                }
            )

    if pieces_jointes:
        indicateurs.append("PIECES_JOINTES_PRESENTES")

    return {
        "statut": "ok",
        "indicateurs": indicateurs,
        "details": {
            "en_tetes": en_tetes,
            "nombre_relais_received": received_count,
            "pieces_jointes": pieces_jointes,
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
        b"/"
        + re.escape(key)
        + rb"\s*(?:\(((?:\\.|[^\\()])*)\)|<([0-9A-Fa-f\s]+)>)"
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


def _try_optional_pdf_lib(path: Path) -> dict[str, object] | None:
    try:
        import pypdf  # type: ignore[import-not-found]
    except ImportError:
        pypdf = None

    if pypdf is not None:
        try:
            reader = pypdf.PdfReader(str(path))
            encrypted = bool(getattr(reader, "is_encrypted", False))
            meta_raw = {} if encrypted else (reader.metadata or {})
            meta = {
                k.lstrip("/"): _truncate(str(v), 200)
                for k, v in meta_raw.items()
                if v is not None and str(v).strip()
            }
            if encrypted:
                return {
                    "analyseur": "pypdf",
                    "chiffre": True,
                    "nombre_pages": None,
                    "pages_sans_texte": [],
                    "couche_texte": "chiffree",
                    "metadonnees": meta,
                    "annotations": None,
                    "formulaire": None,
                    "signatures": None,
                }
            empty_pages: list[int] = []
            has_annots = False
            for idx, page in enumerate(reader.pages, start=1):
                txt = (page.extract_text() or "").strip()
                if not txt:
                    empty_pages.append(idx)
                if "/Annots" in page:
                    has_annots = True
            total_pages = len(reader.pages)
            couche = (
                "absente"
                if total_pages > 0 and len(empty_pages) == total_pages
                else ("partielle" if empty_pages else "detectee")
            )
            root_obj = reader.trailer.get("/Root", {})
            has_acro = False
            has_sig = False
            try:
                resolved_root = root_obj.get_object() if hasattr(root_obj, "get_object") else root_obj
                has_acro = "/AcroForm" in resolved_root
                if has_acro:
                    acro = resolved_root["/AcroForm"].get_object()
                    has_sig = "/SigFlags" in acro
            except Exception:
                pass
            return {
                "analyseur": "pypdf",
                "chiffre": False,
                "nombre_pages": total_pages,
                "pages_sans_texte": empty_pages,
                "couche_texte": couche,
                "metadonnees": meta,
                "annotations": has_annots,
                "formulaire": has_acro,
                "signatures": has_sig,
            }
        except Exception:
            return None

    return None


def _inspect_pdf(path: Path) -> dict[str, object]:
    raw = path.read_bytes()
    header_m = _PDF_HEADER_RE.search(raw[:1024])
    version = header_m.group(1).decode("ascii") if header_m else "inconnue"

    indicateurs: list[str] = []
    lib_res = _try_optional_pdf_lib(path)

    if lib_res is not None:
        lib_res["version_pdf"] = version
        if lib_res.get("chiffre"):
            indicateurs.append("PDF_CHIFFRE")
        elif lib_res.get("couche_texte") == "absente":
            indicateurs.append("AUCUNE_COUCHE_TEXTE_DETECTEE")
        elif lib_res.get("couche_texte") == "partielle":
            indicateurs.append("COUCHE_TEXTE_PARTIELLE")
        if lib_res.get("annotations"):
            indicateurs.append("ANNOTATIONS_PRESENTES")
        if lib_res.get("formulaire"):
            indicateurs.append("FORMULAIRE_ACROFORM")
        if lib_res.get("signatures"):
            indicateurs.append("SIGNATURE_ELECTRONIQUE_DETECTEE")
        return {
            "statut": "ok",
            "indicateurs": indicateurs,
            "details": lib_res,
        }

    encrypted = bool(_PDF_ENCRYPT_RE.search(raw))

    text_stream_hits = 0
    objstm_blobs: list[bytes] = []
    if not encrypted:
        for m in _PDF_STREAM_RE.finditer(raw):
            chunk = m.group(1)
            if len(chunk) > 8_000_000:
                continue
            pre_dict = raw[max(0, m.start() - 320) : m.start()]
            is_objstm = bool(_PDF_OBJSTM_RE.search(pre_dict))
            decompressed: bytes | None = None
            try:
                decompressed = zlib.decompressobj().decompress(chunk)
            except zlib.error:
                decompressed = None
            if is_objstm and decompressed:
                first_m = _PDF_FIRST_RE.search(pre_dict)
                first_off = int(first_m.group(1)) if first_m else 0
                objstm_blobs.append(
                    decompressed[first_off:] if first_off < len(decompressed) else decompressed
                )
            else:
                for cand in (chunk, decompressed) if decompressed else (chunk,):
                    if _PDF_TEXT_OP_RE.search(cand):
                        text_stream_hits += 1
                        break

    struct_blob = raw if not objstm_blobs else (raw + b"\n" + b"\n".join(objstm_blobs))
    pages = len(_PDF_PAGE_RE.findall(struct_blob))
    has_annots = bool(_PDF_ANNOTS_RE.search(struct_blob))
    has_acro = bool(_PDF_ACROFORM_RE.search(struct_blob))
    has_sig = bool(_PDF_SIG_RE.search(struct_blob))

    meta: dict[str, str] = {}
    for pdf_key, label in (
        (b"Title", "Title"),
        (b"Author", "Author"),
        (b"Creator", "Creator"),
        (b"Producer", "Producer"),
        (b"CreationDate", "CreationDate"),
        (b"ModDate", "ModDate"),
    ):
        val = _extract_pdf_literal(struct_blob, pdf_key)
        if val:
            meta[label] = val

    if encrypted:
        couche = "chiffree"
        indicateurs.append("PDF_CHIFFRE")
    elif text_stream_hits == 0:
        couche = "absente"
        indicateurs.append("AUCUNE_COUCHE_TEXTE_DETECTEE")
    else:
        couche = "detectee"

    if has_annots:
        indicateurs.append("ANNOTATIONS_PRESENTES")
    if has_acro:
        indicateurs.append("FORMULAIRE_ACROFORM")
    if has_sig:
        indicateurs.append("SIGNATURE_ELECTRONIQUE_DETECTEE")

    return {
        "statut": "ok",
        "indicateurs": indicateurs,
        "details": {
            "analyseur": "stdlib-binaire",
            "version_pdf": version,
            "chiffre": encrypted,
            "nombre_pages_estime": pages,
            "flux_texte_detectes": text_stream_hits,
            "couche_texte": couche,
            "metadonnees": meta,
            "annotations": has_annots,
            "formulaire": has_acro,
            "signatures": has_sig,
        },
    }


def _read_u16(buf: bytes, offset: int, endian: str) -> int:
    return struct.unpack_from(f"{endian}H", buf, offset)[0]


def _read_u32(buf: bytes, offset: int, endian: str) -> int:
    return struct.unpack_from(f"{endian}I", buf, offset)[0]


def _parse_gps_ifd(tiff: bytes, offset: int, endian: str) -> dict[str, object]:
    gps: dict[str, object] = {}
    if offset + 2 > len(tiff):
        return gps
    count = _read_u16(tiff, offset, endian)
    pos = offset + 2
    for _ in range(min(count, 64)):
        if pos + 12 > len(tiff):
            break
        tag = _read_u16(tiff, pos, endian)
        typ = _read_u16(tiff, pos + 2, endian)
        num = _read_u32(tiff, pos + 4, endian)
        val_field = tiff[pos + 8 : pos + 12]
        val_offset = _read_u32(tiff, pos + 8, endian)
        pos += 12

        if tag in (0x0001, 0x0003, 0x001D) and typ == 2 and num > 0:
            raw_b = val_field[:num] if num <= 4 else (
                tiff[val_offset : val_offset + num] if val_offset + num <= len(tiff) else b""
            )
            val = raw_b.rstrip(b"\x00").decode("utf-8", errors="replace").strip()
            if val:
                label = {0x0001: "lat_ref", 0x0003: "lon_ref", 0x001D: "gps_date"}[tag]
                gps[label] = val
        elif tag in (0x0002, 0x0004) and typ == 5 and num == 3:
            if val_offset + 24 <= len(tiff):
                dms: list[float] = []
                for idx in range(3):
                    num_r = _read_u32(tiff, val_offset + idx * 8, endian)
                    den_r = _read_u32(tiff, val_offset + idx * 8 + 4, endian)
                    if den_r == 0:
                        break
                    dms.append(num_r / den_r)
                if len(dms) == 3:
                    deg = round(dms[0] + dms[1] / 60.0 + dms[2] / 3600.0, 6)
                    gps["lat_deg" if tag == 0x0002 else "lon_deg"] = deg
    return gps


def _parse_ifd(
    tiff: bytes, offset: int, endian: str, tag_map: dict[int, str]
) -> tuple[dict[str, str], int | None, int | None]:
    result: dict[str, str] = {}
    exif_ifd_offset: int | None = None
    gps_ifd_offset: int | None = None
    if offset + 2 > len(tiff):
        return result, None, None
    count = _read_u16(tiff, offset, endian)
    pos = offset + 2
    for _ in range(min(count, 256)):
        if pos + 12 > len(tiff):
            break
        tag = _read_u16(tiff, pos, endian)
        typ = _read_u16(tiff, pos + 2, endian)
        num = _read_u32(tiff, pos + 4, endian)
        val_field = tiff[pos + 8 : pos + 12]
        val_offset = _read_u32(tiff, pos + 8, endian)
        pos += 12

        if tag == 0x8769:
            exif_ifd_offset = val_offset
            continue
        if tag == 0x8825:
            result["GPSInfo_present"] = "oui"
            gps_ifd_offset = val_offset
            continue
        if tag in tag_map and typ == 2 and num > 0:
            if num <= 4:
                raw_bytes = val_field[:num]
            elif val_offset + num <= len(tiff):
                raw_bytes = tiff[val_offset : val_offset + num]
            else:
                continue
            decoded = raw_bytes.rstrip(b"\x00").decode("utf-8", errors="replace").strip()
            if decoded:
                result[tag_map[tag]] = _truncate(decoded, 120)
        elif tag == 0x0112 and typ == 3 and num == 1:
            result["orientation"] = str(_read_u16(val_field, 0, endian))
    return result, exif_ifd_offset, gps_ifd_offset


def _inspect_jpeg(path: Path) -> dict[str, object]:
    data = path.read_bytes()
    exif_tags: dict[str, object] = {}
    dimensions: dict[str, int] = {}
    pos = 2
    if data.startswith(b"\xff\xd8"):
        while pos + 2 <= len(data):
            if data[pos] != 0xFF:
                break
            marker = data[pos + 1]
            if marker == 0xFF:
                pos += 1
                continue
            if marker in (0xD9, 0xDA):
                break
            if marker in (0x00, 0x01) or 0xD0 <= marker <= 0xD7:
                pos += 2
                continue
            if pos + 4 > len(data):
                break
            seg_len = struct.unpack_from(">H", data, pos + 2)[0]
            if seg_len < 2:
                break
            seg = data[pos + 4 : pos + 2 + seg_len]
            if marker in (0xC0, 0xC1, 0xC2, 0xC3) and len(seg) >= 5:
                h, w = struct.unpack_from(">HH", seg, 1)
                dimensions = {"largeur_px": w, "hauteur_px": h}
            if marker == 0xE1 and seg.startswith(b"Exif\x00\x00"):
                tiff = seg[6:]
                if len(tiff) >= 8:
                    endian = "<" if tiff[:2] == b"II" else (">" if tiff[:2] == b"MM" else "")
                    if endian:
                        ifd0_off = _read_u32(tiff, 4, endian)
                        ifd0_map = {
                            0x010E: "description_image",
                            0x010F: "fabricant",
                            0x0110: "modele_appareil",
                            0x0131: "logiciel",
                            0x0132: "date_fichier_exif",
                            0x013B: "auteur_artiste",
                            0x8298: "droit_auteur",
                        }
                        tags, exif_sub, gps_sub = _parse_ifd(tiff, ifd0_off, endian, ifd0_map)
                        exif_tags.update(tags)
                        if exif_sub is not None:
                            sub_tags, _, _ = _parse_ifd(
                                tiff,
                                exif_sub,
                                endian,
                                {
                                    0x9003: "date_prise_de_vue",
                                    0x9004: "date_numerisation",
                                    0x9010: "fuseau_fichier",
                                    0x9011: "fuseau_prise_de_vue",
                                    0xA420: "identifiant_unique_image",
                                },
                            )
                            exif_tags.update(sub_tags)
                        if gps_sub is not None:
                            gps_data = _parse_gps_ifd(tiff, gps_sub, endian)
                            if gps_data:
                                exif_tags["gps"] = gps_data
            pos += 2 + seg_len

    indicateurs = ["EXIF_PRESENT"] if exif_tags else ["EXIF_ABSENT_OU_STRIPPE"]
    indicateurs.append("PERCEPTION_VISUELLE_REQUISE")
    details: dict[str, object] = {"exif": exif_tags}
    if dimensions:
        details["dimensions"] = dimensions
    return {
        "statut": "ok",
        "indicateurs": indicateurs,
        "details": details,
    }


def _inspect_png(path: Path) -> dict[str, object]:
    data = path.read_bytes()
    text_chunks: dict[str, str] = {}
    dimensions: dict[str, int] = {}
    mtime_chunk: str | None = None
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        pos = 8
        while pos + 12 <= len(data):
            length = struct.unpack_from(">I", data, pos)[0]
            ctype = data[pos + 4 : pos + 8]
            if pos + 12 + length > len(data):
                break
            chunk_data = data[pos + 8 : pos + 8 + length]
            if ctype == b"IHDR" and len(chunk_data) >= 8:
                w, h = struct.unpack_from(">II", chunk_data, 0)
                dimensions = {"largeur_px": w, "hauteur_px": h}
            elif ctype == b"tEXt" and b"\x00" in chunk_data:
                k, v = chunk_data.split(b"\x00", 1)
                text_chunks[k.decode("latin-1", errors="replace")] = _truncate(
                    v.decode("latin-1", errors="replace"), 150
                )
            elif ctype == b"zTXt" and b"\x00" in chunk_data:
                nul = chunk_data.find(b"\x00")
                if nul > 0 and nul + 2 <= len(chunk_data) and chunk_data[nul + 1] == 0:
                    k = chunk_data[:nul].decode("latin-1", errors="replace")
                    try:
                        v = zlib.decompress(chunk_data[nul + 2 :]).decode("latin-1", errors="replace")
                        text_chunks[k] = _truncate(v, 150)
                    except zlib.error:
                        pass
            elif ctype == b"iTXt":
                nul1 = chunk_data.find(b"\x00")
                if nul1 > 0 and nul1 + 3 <= len(chunk_data):
                    k = chunk_data[:nul1].decode("latin-1", errors="replace")
                    comp_flag = chunk_data[nul1 + 1]
                    comp_method = chunk_data[nul1 + 2]
                    rest = chunk_data[nul1 + 3 :]
                    nul2 = rest.find(b"\x00")
                    if nul2 >= 0:
                        rest2 = rest[nul2 + 1 :]
                        nul3 = rest2.find(b"\x00")
                        if nul3 >= 0:
                            raw_txt = rest2[nul3 + 1 :]
                            if comp_flag == 1 and comp_method == 0:
                                try:
                                    raw_txt = zlib.decompress(raw_txt)
                                except zlib.error:
                                    raw_txt = b""
                            if raw_txt:
                                text_chunks[k] = _truncate(
                                    raw_txt.decode("utf-8", errors="replace"), 150
                                )
            elif ctype == b"tIME" and len(chunk_data) == 7:
                yr, mo, dy, hr, mn, sc = struct.unpack_from(">HBBBBB", chunk_data, 0)
                mtime_chunk = f"{yr:04d}-{mo:02d}-{dy:02d}T{hr:02d}:{mn:02d}:{sc:02d}Z"
            pos += 12 + length
            if ctype == b"IEND":
                break
    indicateurs = ["METADONNEES_PNG_PRESENTES"] if (text_chunks or mtime_chunk) else []
    indicateurs.append("PERCEPTION_VISUELLE_REQUISE")
    details: dict[str, object] = {"chunks_texte": text_chunks}
    if dimensions:
        details["dimensions"] = dimensions
    if mtime_chunk:
        details["horodatage_png_tIME"] = mtime_chunk
    return {
        "statut": "ok",
        "indicateurs": indicateurs,
        "details": details,
    }


def _inspect_wav(path: Path) -> dict[str, object]:
    data = path.read_bytes()
    details: dict[str, object] = {}
    info_tags: dict[str, str] = {}
    if len(data) < 12 or data[:4] != b"RIFF" or data[8:12] != b"WAVE":
        return {"statut": "erreur", "erreur": "En-tête RIFF/WAVE invalide."}

    pos = 12
    data_bytes = 0
    byte_rate = 0
    while pos + 8 <= len(data):
        cid = data[pos : pos + 4]
        csize = struct.unpack_from("<I", data, pos + 4)[0]
        body_start = pos + 8
        body_end = min(body_start + csize, len(data))
        chunk = data[body_start:body_end]
        if cid == b"fmt " and len(chunk) >= 16:
            audio_fmt, channels, sample_rate, byte_rate, _, bits_per_sample = struct.unpack_from(
                "<HHIIHH", chunk, 0
            )
            details["audio"] = {
                "format_code": audio_fmt,
                "canaux": channels,
                "frequence_hz": sample_rate,
                "bits_par_echantillon": bits_per_sample,
            }
        elif cid == b"data":
            data_bytes = csize
        elif cid == b"LIST" and len(chunk) >= 4 and chunk[:4] == b"INFO":
            ipos = 4
            while ipos + 8 <= len(chunk):
                tag_id = chunk[ipos : ipos + 4].decode("latin-1", errors="replace")
                tsize = struct.unpack_from("<I", chunk, ipos + 4)[0]
                tval = chunk[ipos + 8 : min(ipos + 8 + tsize, len(chunk))]
                txt = tval.rstrip(b"\x00").decode("utf-8", errors="replace").strip()
                if txt:
                    info_tags[tag_id] = _truncate(txt, 150)
                ipos += 8 + tsize + (tsize % 2)
        pos = body_start + csize + (csize % 2)

    if byte_rate > 0 and data_bytes > 0:
        details["duree_secondes_estimee"] = round(data_bytes / byte_rate, 2)
    if info_tags:
        details["metadonnees_info"] = info_tags
    indicateurs = ["METADONNEES_MEDIA_PRESENTES"] if info_tags else []
    indicateurs.append("PERCEPTION_AUDITIVE_REQUISE")
    return {"statut": "ok", "indicateurs": indicateurs, "details": details}


def _inspect_mp3(path: Path) -> dict[str, object]:
    data = path.read_bytes()
    tags: dict[str, str] = {}
    if data.startswith(b"ID3") and len(data) >= 10:
        ver_major = data[3]
        flags = data[5]
        s = data[6:10]
        tag_size = ((s[0] & 0x7F) << 21) | ((s[1] & 0x7F) << 14) | ((s[2] & 0x7F) << 7) | (s[3] & 0x7F)
        pos = 10 + (10 if (flags & 0x40) else 0)
        end = min(10 + tag_size, len(data))
        if ver_major in (3, 4):
            while pos + 10 <= end:
                fid = data[pos : pos + 4]
                if fid == b"\x00\x00\x00\x00":
                    break
                if ver_major == 4:
                    fs = data[pos + 4 : pos + 8]
                    fsize = ((fs[0] & 0x7F) << 21) | ((fs[1] & 0x7F) << 14) | ((fs[2] & 0x7F) << 7) | (fs[3] & 0x7F)
                else:
                    fsize = struct.unpack_from(">I", data, pos + 4)[0]
                if fsize <= 0 or pos + 10 + fsize > end:
                    break
                payload = data[pos + 10 : pos + 10 + fsize]
                if fid.startswith(b"T") and len(payload) >= 1:
                    enc = payload[0]
                    raw_txt = payload[1:]
                    codec = {0: "latin-1", 1: "utf-16", 2: "utf-16-be", 3: "utf-8"}.get(enc, "utf-8")
                    val_parts = [p.strip() for p in raw_txt.decode(codec, errors="replace").split("\x00") if p.strip()]
                    val = " : ".join(val_parts)
                    if val:
                        tags[fid.decode("ascii", errors="replace")] = _truncate(val, 150)
                pos += 10 + fsize
    indicateurs = ["METADONNEES_ID3_PRESENTES"] if tags else []
    indicateurs.append("PERCEPTION_AUDITIVE_REQUISE")
    return {"statut": "ok", "indicateurs": indicateurs, "details": {"tags_id3": tags}}


def _mp4_time_to_iso(seconds_since_1904: int) -> str | None:
    if seconds_since_1904 <= _MP4_EPOCH_OFFSET:
        return None
    unix_ts = seconds_since_1904 - _MP4_EPOCH_OFFSET
    return datetime.fromtimestamp(unix_ts, tz=timezone.utc).isoformat()


def _inspect_mp4(path: Path) -> dict[str, object]:
    data = path.read_bytes()
    details: dict[str, object] = {}
    tracks: list[str] = []

    def _walk(start: int, end: int, depth: int = 0) -> None:
        if depth > 4:
            return
        pos = start
        while pos + 8 <= end:
            size = struct.unpack_from(">I", data, pos)[0]
            btype = data[pos + 4 : pos + 8]
            hdr = 8
            if size == 1 and pos + 16 <= end:
                size = struct.unpack_from(">Q", data, pos + 8)[0]
                hdr = 16
            elif size == 0:
                size = end - pos
            if size < hdr or pos + size > end:
                break
            b_start = pos + hdr
            b_end = pos + size
            if btype == b"ftyp" and b_start + 4 <= b_end:
                details["marque_conteneur"] = data[b_start : b_start + 4].decode("ascii", errors="replace")
            elif btype == b"mvhd" and b_start + 4 <= b_end:
                ver = data[b_start]
                if ver == 0 and b_start + 20 <= b_end:
                    c_t, m_t, ts, dur = struct.unpack_from(">IIII", data, b_start + 4)
                elif ver == 1 and b_start + 32 <= b_end:
                    c_t, m_t, ts, dur = struct.unpack_from(">QQIQ", data, b_start + 4)
                else:
                    c_t = m_t = ts = dur = 0
                c_iso = _mp4_time_to_iso(c_t)
                m_iso = _mp4_time_to_iso(m_t)
                if c_iso:
                    details["date_creation_conteneur"] = c_iso
                if m_iso:
                    details["date_modification_conteneur"] = m_iso
                if ts > 0 and dur > 0:
                    details["duree_secondes"] = round(dur / ts, 2)
            elif btype == b"hdlr" and b_start + 12 <= b_end:
                subtype = data[b_start + 8 : b_start + 12].decode("ascii", errors="replace")
                if subtype in ("vide", "soun", "text", "subt"):
                    tracks.append(subtype)
            elif btype in (b"moov", b"trak", b"mdia"):
                _walk(b_start, b_end, depth + 1)
            pos = b_end

    _walk(0, len(data))
    if tracks:
        details["pistes_detectees"] = sorted(set(tracks))
    indicateurs: list[str] = []
    if details.get("date_creation_conteneur") or details.get("date_modification_conteneur"):
        indicateurs.append("METADONNEES_MEDIA_PRESENTES")
    if "vide" in tracks or path.suffix.lower() in (".mp4", ".mov"):
        indicateurs.append("PERCEPTION_AUDIOVISUELLE_REQUISE")
    else:
        indicateurs.append("PERCEPTION_AUDITIVE_REQUISE")
    return {"statut": "ok", "indicateurs": indicateurs, "details": details}


def _extraire_dates_internes(item: dict[str, object]) -> dict[str, str]:
    dates: dict[str, str] = {}
    details = item.get("details")
    if not isinstance(details, dict):
        return dates
    props = details.get("proprietes")
    if isinstance(props, dict):
        for k in ("date_creation", "date_modification"):
            if k in props:
                dates[k] = str(props[k])
    en_tetes = details.get("en_tetes")
    if isinstance(en_tetes, dict) and "Date" in en_tetes:
        dates["date_courriel"] = str(en_tetes["Date"])
    meta = details.get("metadonnees")
    if isinstance(meta, dict):
        for k in ("CreationDate", "ModDate"):
            if k in meta:
                dates[k] = str(meta[k])
    exif = details.get("exif")
    if isinstance(exif, dict):
        for k in ("date_prise_de_vue", "date_numerisation", "date_fichier_exif"):
            if k in exif:
                dates[k] = str(exif[k])
    for k in ("horodatage_png_tIME", "date_creation_conteneur", "date_modification_conteneur"):
        if k in details:
            dates[k] = str(details[k])
    return dates


def inspecter_fichier(path: Path) -> dict[str, object]:
    base: dict[str, object] = {"chemin": str(path)}
    if not path.exists():
        base["statut"] = "erreur"
        base["erreur"] = "Fichier introuvable."
        return base
    if not path.is_file():
        base["statut"] = "erreur"
        base["erreur"] = "Le chemin désigne un répertoire, pas un fichier."
        return base

    stat = path.stat()
    ext = path.suffix.lower()
    mime, _ = mimetypes.guess_type(path.name)
    base.update(
        {
            "nom": path.name,
            "extension": ext or "(sans extension)",
            "type_mime_presume": mime or "application/octet-stream",
            "taille_octets": stat.st_size,
            "date_fichier_utc": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
            "sha256": _sha256_file(path),
        }
    )

    if ext in _DOCX_EXTS:
        spec = _inspect_docx(path)
    elif ext in _XLSX_EXTS:
        spec = _inspect_xlsx(path)
    elif ext in _EML_EXTS:
        spec = _inspect_eml(path)
    elif ext in _PDF_EXTS:
        spec = _inspect_pdf(path)
    elif ext in _JPEG_EXTS:
        spec = _inspect_jpeg(path)
    elif ext in _PNG_EXTS:
        spec = _inspect_png(path)
    elif ext in _WAV_EXTS:
        spec = _inspect_wav(path)
    elif ext in _MP3_EXTS:
        spec = _inspect_mp3(path)
    elif ext in _MP4_EXTS:
        spec = _inspect_mp4(path)
    else:
        spec = {
            "statut": "ok",
            "indicateurs": ["INSPECTION_GENERIQUE"],
            "details": {},
        }

    base.update(spec)
    return base


def ecrire_journal_garde(
    journal_path: Path,
    resultats: list[dict[str, object]],
    source: str = "fournie par l'avocat",
) -> list[dict[str, object]]:
    """Ajoute les empreintes, dates et provenance au journal de garde local (JSON ou Markdown)."""
    horodatage = datetime.now(tz=timezone.utc).isoformat()
    entrees: list[dict[str, object]] = []
    for item in resultats:
        if item.get("statut") != "ok":
            continue
        entrees.append(
            {
                "horodatage_prise_en_charge_utc": horodatage,
                "nom": item.get("nom"),
                "chemin": item.get("chemin"),
                "extension": item.get("extension"),
                "taille_octets": item.get("taille_octets"),
                "sha256": item.get("sha256"),
                "date_fichier_utc": item.get("date_fichier_utc"),
                "dates_internes": _extraire_dates_internes(item),
                "source": source,
                "indicateurs": item.get("indicateurs", []),
            }
        )

    def _md_cell(val: object) -> str:
        return " ".join(str(val).replace("|", "\\|").splitlines()).strip()

    journal_path.parent.mkdir(parents=True, exist_ok=True)
    if journal_path.suffix.lower() == ".md":
        header = (
            "# Journal de garde des pièces\n\n"
            "| Prise en charge (UTC) | Fichier | Taille (octets) | SHA-256 | Dates | Source | Signaux |\n"
            "|---|---|---|---|---|---|---|\n"
        )
        rows = []
        for e in entrees:
            dates_str = ", ".join(f"{k}={v}" for k, v in dict(e["dates_internes"]).items()) or str(
                e["date_fichier_utc"]
            )
            sigs = ", ".join(str(x) for x in list(e["indicateurs"])) or "aucun"
            rows.append(
                f"| {_md_cell(e['horodatage_prise_en_charge_utc'])} | {_md_cell(e['nom'])} | {e['taille_octets']} | "
                f"`{e['sha256']}` | {_md_cell(dates_str)} | {_md_cell(e['source'])} | {_md_cell(sigs)} |"
            )
        existing_md = journal_path.read_text(encoding="utf-8") if journal_path.is_file() else ""
        prefix = existing_md if existing_md.strip() else header
        if prefix and not prefix.endswith("\n"):
            prefix += "\n"
        journal_path.write_text(prefix + "\n".join(rows) + ("\n" if rows else ""), encoding="utf-8", newline="\n")
    else:
        existant: list[dict[str, object]] = []
        if journal_path.is_file():
            raw_existing = journal_path.read_text(encoding="utf-8").strip()
            if raw_existing:
                try:
                    loaded = json.loads(raw_existing)
                except json.JSONDecodeError as exc:
                    raise ValueError(
                        f"Journal de garde JSON existant invalide ({journal_path}) — écriture annulée pour préserver l'historique : {exc}"
                    ) from exc
                if isinstance(loaded, dict) and isinstance(loaded.get("entrees"), list):
                    existant = loaded["entrees"]
                elif isinstance(loaded, list):
                    existant = loaded
                else:
                    raise ValueError(
                        f"Structure de journal de garde JSON non reconnue ({journal_path}) — écriture annulée."
                    )
        doc = {"version": "1.0", "entrees": existant + entrees}
        journal_path.write_text(
            json.dumps(doc, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    return entrees


def _format_texte(resultats: list[dict[str, object]]) -> str:
    lignes: list[str] = []
    for item in resultats:
        lignes.append(f"=== {item.get('chemin')} ===")
        if item.get("statut") != "ok":
            lignes.append(f"ERREUR : {item.get('erreur')}")
            lignes.append("")
            continue
        lignes.append(
            f"Format : {item['extension']} | Taille : {item['taille_octets']} octets | SHA-256 : {str(item['sha256'])[:16]}…"
        )
        indicateurs = item.get("indicateurs") or []
        lignes.append(
            "Signaux : " + (", ".join(str(x) for x in indicateurs) if indicateurs else "aucun signal particulier")
        )
        details = item.get("details") or {}
        lignes.append(json.dumps(details, ensure_ascii=False, indent=2))
        lignes.append("")
    return "\n".join(lignes)


def main(argv: list[str] | None = None) -> int:
    _configure_stdio()
    parser = argparse.ArgumentParser(
        description="Inspecter les métadonnées et structures cachées de pièces locales (.docx, .xlsx, .eml, .pdf, images, audio/vidéo)."
    )
    parser.add_argument("fichiers", nargs="+", help="Chemins des fichiers à inspecter.")
    parser.add_argument(
        "--journal",
        type=Path,
        default=None,
        help="Chemin du journal de garde (.json ou .md) où consigner empreintes, dates et provenance.",
    )
    parser.add_argument(
        "--source",
        default="fournie par l'avocat",
        help="Mention de provenance consignée dans --journal.",
    )
    parser.add_argument("--json", action="store_true", help="Afficher le résultat au format JSON.")
    args = parser.parse_args(argv)

    resultats = [inspecter_fichier(Path(f)) for f in args.fichiers]
    if args.journal is not None:
        try:
            ecrire_journal_garde(args.journal, resultats, source=args.source)
        except ValueError as exc:
            print(f"Erreur journal de garde : {exc}", file=sys.stderr)
            return 2

    if args.json:
        print(json.dumps(resultats, ensure_ascii=False, indent=2))
    else:
        print(_format_texte(resultats), end="")

    has_error = any(r.get("statut") != "ok" for r in resultats)
    return 1 if has_error else 0


if __name__ == "__main__":
    raise SystemExit(main())
