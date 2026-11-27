#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET
import zipfile

_W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
_MAX_DOCX_XML_BYTES = 64 * 1024 * 1024
_MAX_TEXT_FILE_BYTES = 32 * 1024 * 1024

_STANDARD_PREFIXES = frozenset({"P", "D", "PI", "DI", "MP", "OP", "GC", "R", "I", "A", "MC"})
_COTE_RE = re.compile(
    r"(?<![A-Za-z0-9.\-/])"
    r"\b(P|D(?:[A-Za-z]{1,2})?|PI|DI|MP|OP|GC|R|I|A|MC)-(0?[1-9]\d{0,3})([A-Za-z]?)\b"
    r"(?!\.\d)(?!-[rR]\.)(?!-\d)"
)
_EXPLICIT_COTE_LABEL_RE = re.compile(
    r"(?:\bPièce|\bPiece|\bExhibit|\bcote)\s+(?:la\s+|the\s+)?$",
    re.I,
)
_STATUTORY_PREFIX_RE = re.compile(
    r"(?:"
    r"(?:(?:\bc|\bch|\bchap|\brègl|\breg)\.\s*|\b(?:chapitre|chapter|loi|act|règlement|regulation)\s+)"
    r"|"
    r"(?:\bRLRQ|\bCQLR|\bL\.R\.Q\.|\bR\.S\.Q\.|\bL\.R\.C\.|\bR\.S\.C\.)(?:\s*,?\s*(?:c\.|ch\.|chap\.|chapitre|chapter|règl\.|règlement|reg\.|regulation))?\s+[A-Z]{1,3}-\d+(?:\.\d+)?(?:-r\.\d+)?(?:\s*(?:,|;|et|and|ou|or)\s+[A-Z]{1,3}-\d+(?:\.\d+)?(?:-r\.\d+)?)*\s*(?:,|;|et|and|ou|or)\s+"
    r"|"
    r"(?:(?:\bc|\bch|\bchap|\brègl|\breg)\.\s*|\b(?:chapitre|chapter|règlement|regulation)\s+)[A-Z]{1,3}-\d+(?:\.\d+)?(?:-r\.\d+)?(?:\s*(?:,|;|et|and|ou|or)\s+[A-Z]{1,3}-\d+(?:\.\d+)?(?:-r\.\d+)?)*\s*(?:,|;|et|and|ou|or)\s+"
    r")$",
    re.I,
)

_RETRAIT_PATTERNS = (
    re.compile(
        r"\[[^\]]{0,40}\b(?:Pièce|Piece|Exhibit)?\s*(P|D(?:[A-Za-z]{1,2})?|PI|DI|MP|OP|GC|R|I|A|MC)-(0?[1-9]\d{0,3})([A-Za-z]?)\b[^\]]{0,40}\b(?:retirée?|withdrawn|annulée?)\b[^\]]*\]",
        re.I,
    ),
    re.compile(
        r"\b(P|D(?:[A-Za-z]{1,2})?|PI|DI|MP|OP|GC|R|I|A|MC)-(0?[1-9]\d{0,3})([A-Za-z]?)\b\s*(?:[:—–|-]\s*)?\[[^\]]*\b(?:retirée?|withdrawn|annulée?)\b[^\]]*\]",
        re.I,
    ),
)

_INVOCATION_DEBUT_RE = re.compile(
    r"(?:tel\s+qu'il\s+appert\s+(?:de|du|des|d['’])|produite?\s+au\s+soutien|produits?\s+en\s+liasse|"
    r"as\s+appears\s+from|filed\s+in\s+support)",
    re.I,
)
_ABBREV_DOT_RE = re.compile(
    r"(?:\b(?:inc|ltée|ltee|enr|corp|co|mme|mlle|dr|prof|hon|art|par|al|chap|vol|nos?|janv|févr|fevr|avr|juill|sept|oct|nov|déc|dec|env|approx|etc)|(?<!\w)[A-Za-z])$",
    re.I,
)


def _configure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconf = getattr(stream, "reconfigure", None)
        if callable(reconf):
            reconf(encoding="utf-8", errors="replace")


def _lire_texte_document(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(f"Fichier introuvable : {path}")
    ext = path.suffix.lower()
    if ext in (".docx", ".docm"):
        try:
            with zipfile.ZipFile(path, "r") as zf:
                info = zf.getinfo("word/document.xml")
                if info.file_size > _MAX_DOCX_XML_BYTES:
                    raise ValueError(
                        f"{path} : document.xml trop volumineux ({info.file_size} octets > {_MAX_DOCX_XML_BYTES})"
                    )
                with zf.open(info, "r") as fh:
                    raw = fh.read(_MAX_DOCX_XML_BYTES + 1)
                if len(raw) > _MAX_DOCX_XML_BYTES:
                    raise ValueError(
                        f"{path} : document.xml trop volumineux à la décompression (> {_MAX_DOCX_XML_BYTES} octets)"
                    )
            root = ET.fromstring(raw)
        except (zipfile.BadZipFile, KeyError, ET.ParseError) as exc:
            raise ValueError(f"{path} : archive .docx invalide ou sans document.xml ({exc})") from exc
        paras: list[str] = []
        for p in root.findall(f".//{{{_W_NS}}}p"):
            chunks: list[str] = []
            for el in p.iter():
                if el.tag == f"{{{_W_NS}}}t" and el.text:
                    chunks.append(el.text)
                elif el.tag == f"{{{_W_NS}}}tab":
                    chunks.append(" ")
                elif el.tag in (f"{{{_W_NS}}}br", f"{{{_W_NS}}}cr"):
                    chunks.append("\n")
            txt = "".join(chunks).strip()
            if txt:
                paras.append(txt)
        return "\n".join(paras)
    size = path.stat().st_size
    if size > _MAX_TEXT_FILE_BYTES:
        raise ValueError(
            f"{path} : fichier texte trop volumineux ({size} octets > {_MAX_TEXT_FILE_BYTES})"
        )
    return path.read_text(encoding="utf-8")


def _iter_cotes_matches(
    texte: str,
    prefixes_autorises: set[str] | None = None,
    prefixes_d_extra: set[str] | None = None,
):
    for m in _COTE_RE.finditer(texte):
        pre = texte[max(0, m.start() - 60) : m.start()]
        is_explicit = bool(_EXPLICIT_COTE_LABEL_RE.search(pre))
        if not is_explicit and _STATUTORY_PREFIX_RE.search(pre):
            continue
        raw_pref = m.group(1)
        pref = raw_pref.upper()
        if pref not in _STANDARD_PREFIXES:
            is_requested = bool(prefixes_autorises and pref in prefixes_autorises)
            is_known_extra = bool(prefixes_d_extra and pref in prefixes_d_extra)
            if not (is_explicit or is_requested or is_known_extra):
                continue
        if prefixes_autorises and pref not in prefixes_autorises:
            continue
        num = int(m.group(2))
        suf = m.group(3).upper()
        yield m, pref, num, suf, f"{pref}-{num}{suf}"


def _extraire_cotes(
    texte: str,
    prefixes_autorises: set[str] | None = None,
    prefixes_d_extra: set[str] | None = None,
) -> tuple[list[tuple[str, int, str, str]], set[str], set[str]]:
    retirees: set[str] = set()
    retrait_spans: list[tuple[int, int]] = []
    for pat in _RETRAIT_PATTERNS:
        for m in pat.finditer(texte):
            pref = m.group(1).upper()
            if pref not in _STANDARD_PREFIXES:
                pre_ctx = texte[max(0, m.start() - 32) : m.start()]
                if not (
                    _EXPLICIT_COTE_LABEL_RE.search(pre_ctx)
                    or (prefixes_autorises and pref in prefixes_autorises)
                    or (prefixes_d_extra and pref in prefixes_d_extra)
                    or re.search(r"\b(?:Pièce|Piece|Exhibit)\b", m.group(0), re.I)
                ):
                    continue
            if prefixes_autorises and pref not in prefixes_autorises:
                continue
            retirees.add(f"{pref}-{int(m.group(2))}{m.group(3).upper()}")
            retrait_spans.append((m.start(), m.end()))

    premieres: list[tuple[str, int, str, str]] = []
    deja_vues: set[str] = set()
    actives_dans_texte: set[str] = set()
    for m, pref, num, suf, cote in _iter_cotes_matches(texte, prefixes_autorises, prefixes_d_extra):
        in_retrait = any(s <= m.start() < e for s, e in retrait_spans)
        if not in_retrait:
            actives_dans_texte.add(cote)
        if cote not in deja_vues:
            deja_vues.add(cote)
            premieres.append((pref, num, suf, cote))
    return premieres, retirees, actives_dans_texte


def _fin_clause_invocation(texte: str, start: int, limite: int = 450) -> int:
    end = min(len(texte), start + limite)
    pos = start
    depth = 0
    while pos < end:
        ch = texte[pos]
        if ch == "(":
            depth += 1
        elif ch == ")" and depth > 0:
            depth -= 1
        elif ch == "\n" or (ch == ";" and depth == 0):
            return pos
        if ch == ".":
            before = texte[max(start, pos - 16) : pos]
            after = texte[pos + 1 : min(len(texte), pos + 3)]
            if after and not after[0].isspace():
                pos += 1
                continue
            if _ABBREV_DOT_RE.search(before):
                pos += 1
                continue
            return pos
        pos += 1
    return end


def _detecter_invocations_sans_cote(
    texte: str,
    prefixes_autorises: set[str] | None = None,
    prefixes_d_extra: set[str] | None = None,
) -> list[str]:
    alertes: list[str] = []
    for m in _INVOCATION_DEBUT_RE.finditer(texte):
        clause_end = _fin_clause_invocation(texte, m.start())
        extrait = texte[m.start() : clause_end]
        cotes = [c[4] for c in _iter_cotes_matches(extrait, prefixes_autorises, prefixes_d_extra)]
        if not cotes:
            ctx_extrait = texte[max(0, m.start() - 16) : clause_end]
            if not [c[4] for c in _iter_cotes_matches(ctx_extrait, prefixes_autorises, prefixes_d_extra)]:
                alertes.append(" ".join(extrait.split())[:120])
    return alertes


def verifier_ensemble_cotes(
    actes: list[Path],
    bordereau: Path | None = None,
    matrice: Path | None = None,
    prefixes: list[str] | None = None,
    mode_modifie: bool = False,
) -> dict[str, object]:
    prefixes_set = {p.upper() for p in prefixes} if prefixes else None
    anomalies: list[dict[str, object]] = []
    bon_de_travail: list[str] = []
    cotes_par_document: dict[str, dict[str, object]] = {}

    actes_cotes_actives: set[str] = set()
    actes_cotes_retirees: set[str] = set()
    prefixes_d_extra: set[str] = set()

    for acte_path in actes:
        txt = _lire_texte_document(acte_path)
        premieres, retirees, actives_dans_texte = _extraire_cotes(txt, prefixes_set, prefixes_d_extra)
        for pref, _, _, _ in premieres:
            if pref not in _STANDARD_PREFIXES:
                prefixes_d_extra.add(pref)
        sans_cote = _detecter_invocations_sans_cote(txt, prefixes_set, prefixes_d_extra)
        est_modifie = mode_modifie or ("MODIFIÉ" in txt.upper()) or bool(retirees)

        reutilisees_acte = sorted(retirees & actives_dans_texte)
        if reutilisees_acte:
            anomalies.append(
                {
                    "type": "COTE_GELEE_REUTILISEE",
                    "document": str(acte_path),
                    "cotes": reutilisees_acte,
                    "detail": (
                        f"Cotes déclarées retirées mais encore invoquées activement dans {acte_path.name} "
                        f"(gel art. 206–208 requis) : {', '.join(reutilisees_acte)}."
                    ),
                }
            )

        par_prefixe: dict[str, list[tuple[int, str, str]]] = {}
        for pref, num, suf, cote in premieres:
            par_prefixe.setdefault(pref, []).append((num, suf, cote))
            if cote in retirees and cote not in actives_dans_texte:
                actes_cotes_retirees.add(cote)
            else:
                actes_cotes_actives.add(cote)

        for pref, items in par_prefixe.items():
            max_vu = 0
            for num, _, cote in items:
                if cote in retirees and cote not in actives_dans_texte:
                    continue
                if num < max_vu:
                    anomalies.append(
                        {
                            "type": "ORDRE_INVERSE",
                            "document": str(acte_path),
                            "prefixe": pref,
                            "cote": cote,
                            "detail": (
                                f"{cote} invoquée pour la première fois après une cote supérieure "
                                f"({pref}-{max_vu}) dans {acte_path.name}."
                            ),
                        }
                    )
                elif num > max_vu:
                    max_vu = num

            nums_presents = {num for num, _, _ in items}
            nums_retires_pref = {
                int(m.group(2))
                for r in retirees
                if (m := _COTE_RE.match(r)) and m.group(1).upper() == pref
            }
            if nums_presents:
                plafond = max(nums_presents)
                trous = [
                    f"{pref}-{n}"
                    for n in range(1, plafond + 1)
                    if n not in nums_presents and n not in nums_retires_pref
                ]
                if trous:
                    anomalies.append(
                        {
                            "type": "SAUT_NUMEROTATION",
                            "document": str(acte_path),
                            "prefixe": pref,
                            "cotes_manquantes": trous,
                            "detail": (
                                f"Cotes manquantes dans la séquence {pref} de {acte_path.name} : {', '.join(trous)}"
                                + (" (vérifier si retirées avec marque explicite art. 206–208)." if est_modifie else ".")
                            ),
                        }
                    )

        for extrait in sans_cote:
            anomalies.append(
                {
                    "type": "INVOCATION_SANS_COTE",
                    "document": str(acte_path),
                    "extrait": extrait,
                    "detail": f"Mention apparente de pièce sans cote détectée dans {acte_path.name} : « {extrait} »",
                }
            )

        cotes_par_document[str(acte_path)] = {
            "mode_modifie_detecte": est_modifie,
            "ordre_premiere_invocation": [c[3] for c in premieres],
            "cotes_retirees_gelees": sorted(retirees),
            "invocations_sans_cote": sans_cote,
        }

    def _verifier_annexe(label: str, path_opt: Path | None) -> None:
        if path_opt is None:
            return
        txt = _lire_texte_document(path_opt)
        premieres, retirees, actives_annexe = _extraire_cotes(txt, prefixes_set, prefixes_d_extra)
        cotes_doc = {c[3] for c in premieres}
        actives_doc = (cotes_doc - retirees) | actives_annexe

        manquantes_dans_doc = sorted(actes_cotes_actives - actives_doc)
        orphelines_dans_doc = sorted(actives_doc - actes_cotes_actives - actes_cotes_retirees)
        reutilisees = sorted(actives_doc & actes_cotes_retirees)

        if manquantes_dans_doc:
            anomalies.append(
                {
                    "type": f"ABSENTE_{label.upper()}",
                    "document": str(path_opt),
                    "cotes": manquantes_dans_doc,
                    "detail": f"Cotes invoquées dans l'acte mais absentes de {label} : {', '.join(manquantes_dans_doc)}.",
                }
            )
        if orphelines_dans_doc:
            anomalies.append(
                {
                    "type": f"ORPHELINE_{label.upper()}",
                    "document": str(path_opt),
                    "cotes": orphelines_dans_doc,
                    "detail": f"Cotes présentes dans {label} sans invocation dans l'acte : {', '.join(orphelines_dans_doc)}.",
                }
            )
        if reutilisees:
            anomalies.append(
                {
                    "type": "COTE_GELEE_REUTILISEE",
                    "document": str(path_opt),
                    "cotes": reutilisees,
                    "detail": (
                        f"Cotes retirées dans l'acte modifié mais actives dans {label} "
                        f"(gel art. 206–208 requis) : {', '.join(reutilisees)}."
                    ),
                }
            )
        cotes_par_document[str(path_opt)] = {
            "role": label,
            "cotes": [c[3] for c in premieres],
            "cotes_retirees_gelees": sorted(retirees),
        }

    _verifier_annexe("bordereau", bordereau)
    _verifier_annexe("matrice", matrice)

    for anom in anomalies:
        bon_de_travail.append(str(anom["detail"]))

    return {
        "statut": "CONFORME" if not anomalies else "ANOMALIES_DETECTEES",
        "nombre_anomalies": len(anomalies),
        "cotes_par_document": cotes_par_document,
        "anomalies": anomalies,
        "bon_de_travail": bon_de_travail,
    }


def _format_texte(res: dict[str, object]) -> str:
    lignes = [
        f"Statut concordance des cotes : {res['statut']} ({res['nombre_anomalies']} anomalie(s))"
    ]
    anomalies = list(res.get("anomalies") or [])
    if anomalies:
        lignes.append("Anomalies relevées :")
        for idx, a in enumerate(anomalies, start=1):
            lignes.append(f"  {idx}. [{a['type']}] {a['detail']}")
    else:
        lignes.append("Aucune anomalie détectée.")
    return "\n".join(lignes)


def main(argv: list[str] | None = None) -> int:
    _configure_stdio()
    parser = argparse.ArgumentParser(
        description="Vérifier la continuité et la concordance des cotes de pièces (actes, bordereau, matrice)."
    )
    parser.add_argument(
        "--acte",
        action="append",
        type=Path,
        required=True,
        help="Chemin vers un acte de procédure (.txt, .md, .docx ; répétable).",
    )
    parser.add_argument(
        "--bordereau",
        type=Path,
        default=None,
        help="Chemin vers le bordereau des pièces (.txt, .md, .csv, .docx).",
    )
    parser.add_argument(
        "--matrice",
        type=Path,
        default=None,
        help="Chemin vers la matrice de concordance (.txt, .md, .csv, .docx).",
    )
    parser.add_argument(
        "--prefixe",
        action="append",
        default=[],
        help="Filtrer sur un préfixe de cote précis (ex. P, D, R, I, A, MC ; répétable).",
    )
    parser.add_argument(
        "--modifie",
        action="store_true",
        help="Appliquer les règles de gel des cotes retirées sur acte modifié (art. 206–208 C.p.c.).",
    )
    parser.add_argument("--json", action="store_true", help="Afficher le résultat au format JSON.")
    args = parser.parse_args(argv)

    try:
        res = verifier_ensemble_cotes(
            actes=args.acte,
            bordereau=args.bordereau,
            matrice=args.matrice,
            prefixes=args.prefixe or None,
            mode_modifie=args.modifie,
        )
    except Exception as exc:
        print(f"Erreur : {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        print(_format_texte(res))
    return 1 if res.get("nombre_anomalies", 0) > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
