#!/usr/bin/env python3
"""Exécuteur et vérificateur de la suite d'évaluation comportementale (« evals ») v3.

Bibliothèque standard Python uniquement, aucun appel réseau.
Usages :
    python evals/executer_evals.py --liste
    python evals/executer_evals.py --auto-test
    python evals/executer_evals.py --reponses chemin/vers/reponses.json [--json]
"""

from __future__ import annotations

import argparse
import contextlib
from datetime import date, time
import importlib.util
import io
import json
from pathlib import Path
import re
import struct
import sys
import tempfile
from typing import Any
import unittest
import zipfile
import zlib

RACINE = Path(__file__).resolve().parent.parent
SCENARIOS_PATH = Path(__file__).resolve().parent / "scenarios.json"


def _configure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconf = getattr(stream, "reconfigure", None)
        if callable(reconf):
            reconf(encoding="utf-8", errors="replace")


def _charger_module(rel_path: str, nom_module: str) -> Any:
    module_path = RACINE / rel_path
    spec = importlib.util.spec_from_file_location(nom_module, module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Impossible de charger le module {rel_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[nom_module] = module
    spec.loader.exec_module(module)
    return module


def charger_scenarios(path: Path = SCENARIOS_PATH) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("scenarios"), list):
        raise ValueError(f"{path} : objet JSON avec clé 'scenarios' (liste) attendu")
    return data["scenarios"]


def evaluer_reponse(scenario: dict[str, Any], texte: str) -> dict[str, Any]:
    """Évalue une réponse textuelle par rapport aux expressions attendues et interdites."""
    manquants: list[str] = []
    interdits_trouves: list[str] = []

    for pat in scenario.get("doit_contenir", []):
        if not re.search(pat, texte, flags=re.I | re.M):
            manquants.append(pat)

    for pat in scenario.get("ne_doit_pas_contenir", []):
        if re.search(pat, texte, flags=re.I | re.M):
            interdits_trouves.append(pat)

    reussi = not manquants and not interdits_trouves
    return {
        "id": scenario["id"],
        "competence": scenario["competence"],
        "palier": scenario.get("palier"),
        "reussi": reussi,
        "manquants": manquants,
        "interdits_trouves": interdits_trouves,
    }


def _creer_fixture_docx_complet(
    dest: Path,
    *,
    texte: str = "PROJET DE DÉFENSE — sans numéro de cour",
    avec_commentaires: bool = True,
    avec_revisions: bool = False,
    pages_app: str = "7",
    police: str = "Calibri",
    taille_half_pt: str = "22",
    marge_twips: str = "1440",
    interligne_line: str = "240",
) -> None:
    content_types = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/word/document.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
        '<Override PartName="/word/styles.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>'
        + (
            '<Override PartName="/word/comments.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.comments+xml"/>'
            if avec_commentaires
            else ""
        )
        + '<Override PartName="/docProps/core.xml" '
        'ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>'
        '<Override PartName="/docProps/app.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>'
        "</Types>"
    )
    rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
        'Target="word/document.xml"/>'
        '<Relationship Id="rId2" '
        'Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" '
        'Target="docProps/core.xml"/>'
        '<Relationship Id="rId3" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" '
        'Target="docProps/app.xml"/>'
        "</Relationships>"
    )
    rev_xml = (
        '<w:ins w:id="1" w:author="Me Tremblay" w:date="2026-09-10T14:20:00Z">'
        "<w:r><w:t>Ajout suivi</w:t></w:r></w:ins>"
        if avec_revisions
        else ""
    )
    document = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        "<w:body><w:p>"
        f'<w:pPr><w:spacing w:line="{interligne_line}" w:lineRule="auto"/></w:pPr>'
        f'<w:r><w:rPr><w:rFonts w:ascii="{police}" w:hAnsi="{police}"/><w:sz w:val="{taille_half_pt}"/></w:rPr>'
        f"<w:t>{texte}</w:t></w:r>{rev_xml}</w:p>"
        "<w:sectPr>"
        '<w:pgSz w:w="12240" w:h="15840"/>'
        f'<w:pgMar w:top="{marge_twips}" w:right="{marge_twips}" w:bottom="{marge_twips}" w:left="{marge_twips}"/>'
        "</w:sectPr>"
        "</w:body></w:document>"
    )
    styles = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        "<w:docDefaults><w:rPrDefault><w:rPr>"
        f'<w:rFonts w:ascii="{police}" w:hAnsi="{police}"/><w:sz w:val="{taille_half_pt}"/>'
        "</w:rPr></w:rPrDefault></w:docDefaults></w:styles>"
    )
    comments = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:comments xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        '<w:comment w:id="1" w:author="Me Tremblay" w:date="2026-09-10T14:20:00Z">'
        "<w:p><w:r><w:t>Ne pas produire avant d'avoir vérifié la prescription.</w:t></w:r></w:p>"
        "</w:comment></w:comments>"
    )
    core = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<cp:coreProperties '
        'xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
        'xmlns:dc="http://purl.org/dc/elements/1.1/">'
        "<dc:creator>Me Tremblay</dc:creator>"
        "</cp:coreProperties>"
    )
    app = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties">'
        f"<Pages>{pages_app}</Pages><Words>1200</Words>"
        "</Properties>"
    )
    with zipfile.ZipFile(dest, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr("_rels/.rels", rels)
        zf.writestr("word/document.xml", document)
        zf.writestr("word/styles.xml", styles)
        if avec_commentaires:
            zf.writestr("word/comments.xml", comments)
        zf.writestr("docProps/core.xml", core)
        zf.writestr("docProps/app.xml", app)


def _creer_fixture_jpeg_exif(dest: Path) -> None:
    """Construit un JPEG minimal avec segment APP1 Exif valide (Make + DateTimeOriginal)."""
    # TIFF little-endian : header (8 bytes) + IFD0 (2 + 2*12 + 4 = 30 bytes) + strings + ExifIFD
    make_b = b"Canon\x00"
    date_b = b"2026:06:15 10:22:00\x00"
    ifd0_offset = 8
    # 2 entries in IFD0: 0x010F Make, 0x8769 ExifIFD
    ifd0_size = 2 + 2 * 12 + 4
    make_off = ifd0_offset + ifd0_size
    exif_ifd_off = make_off + len(make_b)
    exif_ifd_size = 2 + 1 * 12 + 4
    date_off = exif_ifd_off + exif_ifd_size

    tiff = bytearray()
    tiff += b"II" + struct.pack("<HI", 42, ifd0_offset)
    tiff += struct.pack("<H", 2)
    tiff += struct.pack("<HHII", 0x010F, 2, len(make_b), make_off)
    tiff += struct.pack("<HHII", 0x8769, 4, 1, exif_ifd_off)
    tiff += struct.pack("<I", 0)
    tiff += make_b
    tiff += struct.pack("<H", 1)
    tiff += struct.pack("<HHII", 0x9003, 2, len(date_b), date_off)
    tiff += struct.pack("<I", 0)
    tiff += date_b

    app1_payload = b"Exif\x00\x00" + bytes(tiff)
    app1_seg = b"\xff\xe1" + struct.pack(">H", len(app1_payload) + 2) + app1_payload
    jpeg = b"\xff\xd8" + app1_seg + b"\xff\xd9"
    dest.write_bytes(jpeg)


def _creer_fixture_wav(dest: Path) -> None:
    """Construit un WAV minimal PCM 1 s + chunk LIST INFO."""
    sample_rate = 8000
    channels = 1
    bits = 16
    byte_rate = sample_rate * channels * bits // 8
    data_bytes = b"\x00" * byte_rate
    fmt_chunk = struct.pack("<4sIHHIIHH", b"fmt ", 16, 1, channels, sample_rate, byte_rate, 2, bits)
    data_chunk = struct.pack("<4sI", b"data", len(data_bytes)) + data_bytes
    icrd_txt = b"2026-06-15\x00\x00"
    info_body = b"INFO" + struct.pack("<4sI", b"ICRD", len(icrd_txt)) + icrd_txt
    list_chunk = struct.pack("<4sI", b"LIST", len(info_body)) + info_body
    riff_body = b"WAVE" + fmt_chunk + data_chunk + list_chunk
    dest.write_bytes(struct.pack("<4sI", b"RIFF", len(riff_body)) + riff_body)


def _creer_fixture_pdf_scan(dest: Path) -> None:
    """Construit un PDF minimal sans couche texte ni /Outlines."""
    pdf = (
        b"%PDF-1.4\n"
        b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n"
        b"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n"
        b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >> endobj\n"
        b"%%EOF\n"
    )
    dest.write_bytes(pdf)


def executer_tests_outils(scenarios: list[dict[str, Any]]) -> list[str]:
    """Exécute les assertions déterministes attachées aux 4 outils Python locaux."""
    erreurs: list[str] = []
    calcul_mod = _charger_module(
        "skills/gestion-du-mandat/scripts/calcul_delai.py", "calcul_delai"
    )
    inspect_mod = _charger_module(
        "skills/analyse-et-strategie/scripts/inspecter_piece.py", "inspecter_piece"
    )
    ctrl_mod = _charger_module(
        "skills/production-et-conformite/scripts/controler_document.py", "controler_document"
    )
    cotes_mod = _charger_module(
        "skills/production-et-conformite/scripts/verifier_cotes.py", "verifier_cotes"
    )

    for sc in scenarios:
        spec = sc.get("test_outil")
        if not spec:
            continue
        sid = sc["id"]
        outil = spec.get("outil")
        if outil == "calcul_delai":
            for cas in spec.get("cas", []):
                heure_raw = cas.get("heure_notification")
                heure = time.fromisoformat(heure_raw) if heure_raw else None
                res = calcul_mod.calculer_delai(
                    ancrage=date.fromisoformat(cas["ancrage"]),
                    valeur=int(cas["valeur"]),
                    unite=cas["unite"],
                    sens=cas["sens"],
                    mode_notification=cas["mode_notification"],
                    heure_notification=heure,
                )
                att = cas["attendu"]
                for cle in (
                    "ancrage_effectif",
                    "echeance_brute",
                    "echeance",
                    "echeance_report_suivant",
                    "reportee",
                ):
                    if cle in att and res.get(cle) != att[cle]:
                        erreurs.append(
                            f"{sid} ({cas['nom']}) : {cle}={res.get(cle)!r}, attendu {att[cle]!r}"
                        )
                if "nb_reports" in att and len(res.get("reports", [])) != att["nb_reports"]:
                    erreurs.append(
                        f"{sid} ({cas['nom']}) : len(reports)={len(res.get('reports', []))}, attendu {att['nb_reports']}"
                    )
                av_blob = "\n".join(res.get("avertissements", []))
                for sous_chaine in att.get("avertissements_contient", []):
                    if sous_chaine.lower() not in av_blob.lower():
                        erreurs.append(
                            f"{sid} ({cas['nom']}) : avertissement attendu contenant {sous_chaine!r} absent"
                        )

            res_presc = calcul_mod.calculer_delai(date(2023, 11, 21), 3, "ans", regime="prescription")
            if res_presc.get("echeance_brute") != "2026-11-21" or res_presc.get("echeance") != "2026-11-23" or not res_presc.get("reporter_samedi"):
                erreurs.append(f"{sid} : calcul_delai prescription 2023-11-21 + 3 ans inattendu ({res_presc})")
            res_li = calcul_mod.calculer_delai(date(2023, 11, 21), 3, "ans", regime="li")
            if res_li.get("echeance") != "2026-11-21" or res_li.get("reporter_samedi") is not False:
                erreurs.append(f"{sid} : calcul_delai li 2023-11-21 + 3 ans ne doit pas reporter le samedi ({res_li})")
            res_li_sat = calcul_mod.calculer_delai(date(2023, 11, 21), 3, "ans", regime="li", reporter_samedi=True)
            if res_li_sat.get("echeance") != "2026-11-23" or res_li_sat.get("reporter_samedi") is not True:
                erreurs.append(f"{sid} : calcul_delai li reporter_samedi=True attendu 2026-11-23 ({res_li_sat})")
            res_leap = calcul_mod.calculer_delai(date(2024, 2, 29), 3, "ans", regime="prescription")
            if res_leap.get("echeance_brute") != "2027-02-28" or res_leap.get("echeance") != "2027-03-01":
                erreurs.append(f"{sid} : calcul_delai bissextile 2024-02-29 + 3 ans inattendu ({res_leap})")
            res_jan2_cpc = calcul_mod.calculer_delai(date(2025, 1, 2), 1, "ans", regime="cpc")
            res_jan2_li = calcul_mod.calculer_delai(date(2025, 1, 2), 1, "ans", regime="prescription")
            if res_jan2_cpc.get("echeance") != "2026-01-05" or res_jan2_li.get("echeance") != "2026-01-02":
                erreurs.append(f"{sid} : divergence 2 janvier cpc vs prescription inattendue ({res_jan2_cpc.get('echeance')} / {res_jan2_li.get('echeance')})")

            res_tech_sans_h = calcul_mod.calculer_delai(
                date(2026, 6, 15), 10, "jours", mode_notification="technologique", heure_notification=None
            )
            if not any("sans heure précisée" in a for a in res_tech_sans_h.get("notes_ancrage", [])):
                erreurs.append(f"{sid} : mode technologique sans heure doit avertir ({res_tech_sans_h})")
            res_tech_sec = calcul_mod.calculer_delai(
                date(2026, 5, 4), 15, "jours", mode_notification="technologique", heure_notification=time(17, 0, 1)
            )
            if res_tech_sec.get("heure_notification") != "17:00:01" or res_tech_sec.get("echeance") != "2026-05-20":
                erreurs.append(f"{sid} : heure 17:00:01 mal formatée ou reportée ({res_tech_sec})")
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                rc_overflow = calcul_mod.main(["9999-12-31", "--jours", "10", "--json"])
            if rc_overflow != 2:
                erreurs.append(f"{sid} : débordement date 9999-12-31 attendu rc=2, obtenu {rc_overflow}")
        elif outil == "inspecter_piece":
            if spec.get("fixture") == "docx_avec_commentaire":
                with tempfile.TemporaryDirectory() as tmp:
                    docx_path = Path(tmp) / "Defense_finale.docx"
                    _creer_fixture_docx_complet(docx_path, avec_commentaires=True)
                    res = inspect_mod.inspecter_fichier(docx_path)
                    att = spec["attendu"]
                    if res.get("statut") != att.get("statut"):
                        erreurs.append(f"{sid} : statut={res.get('statut')!r}, attendu {att.get('statut')!r}")
                    inds = set(res.get("indicateurs", []))
                    for ind in att.get("indicateurs_contient", []):
                        if ind not in inds:
                            erreurs.append(f"{sid} : indicateur {ind!r} manquant ({sorted(inds)})")
                    nb_com = int(res.get("details", {}).get("nombre_commentaires", 0))
                    if nb_com < int(att.get("nombre_commentaires_min", 0)):
                        erreurs.append(f"{sid} : nombre_commentaires={nb_com} insuffisant")

                    tmp_dir = Path(tmp)
                    vanish_docx = tmp_dir / "masque.docx"
                    with zipfile.ZipFile(vanish_docx, "w") as zf:
                        zf.writestr("[Content_Types].xml", '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"/>')
                        zf.writestr(
                            "word/document.xml",
                            '<?xml version="1.0"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>'
                            '<w:p><w:r><w:rPr><w:vanish/></w:rPr><w:t>Instruction cachée</w:t></w:r>'
                            '<w:r><w:rPr><w:vanish w:val="0"/></w:rPr><w:t>Texte visible</w:t></w:r></w:p>'
                            "</w:body></w:document>",
                        )
                    r_van = inspect_mod.inspecter_fichier(vanish_docx)
                    if "TEXTE_MASQUE_DOCX" not in r_van.get("indicateurs", []) or r_van.get("details", {}).get("texte_masque", {}).get("occurrences") != 1:
                        erreurs.append(f"{sid} : w:vanish non détecté exactement 1x dans inspecter_piece ({r_van})")

                    xlsx_p = tmp_dir / "tableau_cache.xlsx"
                    with zipfile.ZipFile(xlsx_p, "w") as zf:
                        zf.writestr(
                            "xl/workbook.xml",
                            '<?xml version="1.0"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
                            'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>'
                            '<sheet name="Visible" sheetId="1" r:id="rId1"/>'
                            '<sheet name="Cachee" sheetId="2" state="hidden" r:id="rId2"/>'
                            "</sheets></workbook>",
                        )
                        zf.writestr(
                            "xl/_rels/workbook.xml.rels",
                            '<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>'
                            '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet2.xml"/>'
                            "</Relationships>",
                        )
                        zf.writestr(
                            "xl/worksheets/sheet1.xml",
                            '<?xml version="1.0"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
                            '<cols><col min="3" max="3" hidden="1"/></cols>'
                            '<sheetData><row r="1"><c r="A1"><v>1</v></c></row>'
                            '<row r="2" hidden="1"><c r="A2"><v>999</v></c></row></sheetData></worksheet>',
                        )
                        zf.writestr(
                            "xl/worksheets/sheet2.xml",
                            '<?xml version="1.0"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData/></worksheet>',
                        )
                    r_xlsx = inspect_mod.inspecter_fichier(xlsx_p)
                    inds_x = set(r_xlsx.get("indicateurs", []))
                    if "FEUILLES_CACHEES" not in inds_x or "LIGNES_OU_COLONNES_MASQUEES" not in inds_x:
                        erreurs.append(f"{sid} : feuilles/lignes/colonnes masquées .xlsx manquées ({r_xlsx})")

                    old_cap = inspect_mod._MAX_ZIP_MEMBER_BYTES
                    try:
                        inspect_mod._MAX_ZIP_MEMBER_BYTES = 128
                        r_cap = inspect_mod.inspecter_fichier(vanish_docx)
                        if r_cap.get("statut") != "erreur":
                            erreurs.append(f"{sid} : plafond de décompression inspecter_piece non appliqué ({r_cap})")
                    finally:
                        inspect_mod._MAX_ZIP_MEMBER_BYTES = old_cap

                    propre_docx = tmp_dir / "propre_insp.docx"
                    with zipfile.ZipFile(propre_docx, "w") as zf:
                        zf.writestr("[Content_Types].xml", '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"/>')
                        zf.writestr(
                            "word/document.xml",
                            '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>'
                            '<w:p><w:r><w:t>OK</w:t></w:r></w:p></w:body></w:document>',
                        )
                    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                        rc_insp_clean = inspect_mod.main([str(propre_docx), "--json"])
                        rc_insp_ind = inspect_mod.main([str(docx_path), "--json"])
                        rc_insp_err = inspect_mod.main([str(tmp_dir / "introuvable.docx"), "--json"])
                    if (rc_insp_clean, rc_insp_ind, rc_insp_err) != (0, 1, 2):
                        erreurs.append(
                            f"{sid} : codes de sortie CLI inspecter_piece attendus (0, 1, 2), obtenu {(rc_insp_clean, rc_insp_ind, rc_insp_err)}"
                        )
        elif outil == "inspecter_piece_journal":
            with tempfile.TemporaryDirectory() as tmp:
                tmp_dir = Path(tmp)
                jpg_path = tmp_dir / "photo.jpg"
                wav_path = tmp_dir / "enregistrement.wav"
                journal_json = tmp_dir / "journal.json"
                journal_md = tmp_dir / "journal.md"
                _creer_fixture_jpeg_exif(jpg_path)
                _creer_fixture_wav(wav_path)
                r_jpg = inspect_mod.inspecter_fichier(jpg_path)
                r_wav = inspect_mod.inspecter_fichier(wav_path)
                att = spec["attendu"]
                if att.get("jpeg_exif_detecte"):
                    exif = r_jpg.get("details", {}).get("exif", {})
                    if exif.get("fabricant") != "Canon" or "2026:06:15" not in exif.get("date_prise_de_vue", ""):
                        erreurs.append(f"{sid} : EXIF Canon/date non extrait ({exif})")
                if att.get("wav_duree_detectee"):
                    if r_wav.get("details", {}).get("duree_secondes_estimee") != 1.0:
                        erreurs.append(f"{sid} : durée WAV attendue 1.0, obtenu {r_wav.get('details')}")
                inspect_mod.ecrire_journal_garde(journal_json, [r_jpg, r_wav], source="Client X")
                inspect_mod.ecrire_journal_garde(journal_md, [r_jpg, r_wav], source="Client X")
                j_data = json.loads(journal_json.read_text(encoding="utf-8"))
                if len(j_data.get("entrees", [])) < int(att.get("journal_entrees_min", 2)):
                    erreurs.append(f"{sid} : journal JSON incomplet ({j_data})")
                if "enregistrement.wav" not in journal_md.read_text(encoding="utf-8"):
                    erreurs.append(f"{sid} : journal Markdown ne contient pas enregistrement.wav")

                # Cas limites : XML corrompu non bloquant, PNG iTXt compressé, journal corrompu préservé
                bad_docx = tmp_dir / "corrompu.docx"
                with zipfile.ZipFile(bad_docx, "w") as zf:
                    zf.writestr("word/document.xml", "<w:document>BROKEN")
                r_bad_docx = inspect_mod.inspecter_fichier(bad_docx)
                if r_bad_docx.get("statut") != "ok" or "XML_CORROMPU" not in r_bad_docx.get("indicateurs", []):
                    erreurs.append(f"{sid} : gestion XML corrompu inattendue ({r_bad_docx})")

                ihdr = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
                def _png_chunk(ct: bytes, d: bytes) -> bytes:
                    return struct.pack(">I", len(d)) + ct + d + struct.pack(">I", zlib.crc32(ct + d) & 0xFFFFFFFF)
                itxt_comp = b"XML:com.adobe.xmp\x00\x01\x00\x00\x00" + zlib.compress(b"<xmp>Meta</xmp>")
                png_path = tmp_dir / "meta.png"
                png_path.write_bytes(b"\x89PNG\r\n\x1a\n" + _png_chunk(b"IHDR", ihdr) + _png_chunk(b"iTXt", itxt_comp) + _png_chunk(b"IEND", b""))
                r_png = inspect_mod.inspecter_fichier(png_path)
                if r_png.get("details", {}).get("chunks_texte", {}).get("XML:com.adobe.xmp") != "<xmp>Meta</xmp>":
                    erreurs.append(f"{sid} : iTXt PNG compressé mal décodé ({r_png})")

                corrupt_j = tmp_dir / "corrupt_journal.json"
                corrupt_j.write_text("{CORRUPT_HISTORY", encoding="utf-8")
                try:
                    inspect_mod.ecrire_journal_garde(corrupt_j, [r_wav], source="Test")
                    erreurs.append(f"{sid} : journal corrompu écrasé silencieusement")
                except ValueError:
                    if corrupt_j.read_text(encoding="utf-8") != "{CORRUPT_HISTORY":
                        erreurs.append(f"{sid} : contenu du journal corrompu altéré")
        elif outil == "controler_document":
            with tempfile.TemporaryDirectory() as tmp:
                tmp_dir = Path(tmp)
                docx_path = tmp_dir / "Demande_simplifiee.docx"
                pdf_path = tmp_dir / "cahier.pdf"
                _creer_fixture_docx_complet(
                    docx_path,
                    avec_commentaires=True,
                    avec_revisions=True,
                    pages_app="7",
                    police="Comic Sans MS",
                    taille_half_pt="20",
                    marge_twips="720",
                )
                _creer_fixture_pdf_scan(pdf_path)
                seuils = {
                    "max_pages": 5,
                    "polices_attendues": ["Times New Roman", "Arial"],
                    "taille_min_pt": 11.0,
                    "marge_min_po": 1.0,
                    "exiger_couche_texte": True,
                    "exiger_signets": True,
                }
                res_docx = ctrl_mod.controler_fichier(docx_path, regles=seuils, etiquette_regles="C.Q. 535.3")
                res_pdf = ctrl_mod.controler_fichier(pdf_path, regles=seuils, etiquette_regles="C.Q.")
                att = spec["attendu"]
                if res_docx.get("statut_conformite") != att.get("docx_statut_conformite"):
                    erreurs.append(
                        f"{sid} : docx statut_conformite={res_docx.get('statut_conformite')!r}"
                    )
                docx_codes = {a["code"] for a in res_docx.get("bon_de_travail", [])}
                for code in att.get("docx_codes_contient", []):
                    if code not in docx_codes:
                        erreurs.append(f"{sid} : code bon de travail docx manquant {code!r} ({sorted(docx_codes)})")
                pdf_codes = {a["code"] for a in res_pdf.get("bon_de_travail", [])}
                for code in att.get("pdf_codes_contient", []):
                    if code not in pdf_codes:
                        erreurs.append(f"{sid} : code bon de travail pdf manquant {code!r} ({sorted(pdf_codes)})")

                # Cas limites : styles Word inutilisés ignorés + PDF 1.5 /ObjStm + --regles introuvable
                clean_docx = tmp_dir / "propre.docx"
                with zipfile.ZipFile(clean_docx, "w") as zf:
                    zf.writestr("[Content_Types].xml", '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"/>')
                    zf.writestr(
                        "word/document.xml",
                        '<?xml version="1.0"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>'
                        '<w:p><w:pPr><w:pStyle w:val="Normal"/><w:spacing w:line="360" w:lineRule="auto"/></w:pPr>'
                        '<w:r><w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/><w:sz w:val="24"/></w:rPr><w:t>OK</w:t></w:r></w:p>'
                        '<w:sectPr><w:pgSz w:w="12240" w:h="15840"/><w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440"/></w:sectPr>'
                        "</w:body></w:document>",
                    )
                    zf.writestr(
                        "word/styles.xml",
                        '<?xml version="1.0"?><w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                        '<w:style w:type="paragraph" w:styleId="Normal" w:default="1"><w:rPr><w:rFonts w:ascii="Times New Roman"/><w:sz w:val="24"/></w:rPr></w:style>'
                        '<w:style w:type="paragraph" w:styleId="BalloonText"><w:rPr><w:rFonts w:ascii="Tahoma"/><w:sz w:val="16"/></w:rPr></w:style>'
                        "</w:styles>",
                    )
                    zf.writestr("docProps/app.xml", '<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"><Pages>3</Pages></Properties>')
                r_clean = ctrl_mod.controler_fichier(
                    clean_docx,
                    regles={"max_pages": 5, "polices_attendues": ["Times New Roman"], "taille_min_pt": 12.0, "marge_min_po": 1.0, "interligne_min": 1.5},
                )
                if r_clean.get("statut_conformite") != "CONFORME":
                    erreurs.append(f"{sid} : style inutilisé BalloonText a causé un faux négatif ({r_clean.get('constats')})")

                obj_body = (
                    b"<< /Type /Catalog /Pages 2 0 R /Outlines 4 0 R >>\n"
                    b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>\n"
                    b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>\n"
                    b"<< /Type /Outlines /First 5 0 R /Last 5 0 R /Count 1 >>\n"
                    b"<< /Title (Onglet 1) /Parent 4 0 R >>\n"
                )
                comp_stm = zlib.compress(b"1 0\n" + obj_body)
                pdf15_p = tmp_dir / "objstm.pdf"
                pdf15_p.write_bytes(
                    b"%PDF-1.5\n10 0 obj << /Type /ObjStm /N 5 /First 4 /Filter /FlateDecode /Length "
                    + str(len(comp_stm)).encode("ascii")
                    + b" >>\nstream\n"
                    + comp_stm
                    + b"\nendstream\nendobj\n%%EOF\n"
                )
                r_pdf15 = ctrl_mod.controler_fichier(pdf15_p, regles={"max_pages": 5, "exiger_signets": True})
                if r_pdf15.get("details", {}).get("nombre_pages") != 1 or not r_pdf15.get("details", {}).get("signets_presents"):
                    erreurs.append(f"{sid} : /ObjStm PDF 1.5 non détecté ({r_pdf15.get('details')})")
                endos_pdf = tmp_dir / "endos.pdf"
                endos_pdf.write_bytes(
                    b"%PDF-1.4\n1 0 obj << /Type /Pages /Kids [2 0 R 3 0 R] /Count 2 >> endobj\n"
                    b"2 0 obj << /Type /Page /Parent 1 0 R /MediaBox [0 0 612 792] >> endobj\n"
                    b"3 0 obj << /Type /Page /Parent 1 0 R /MediaBox [0 0 792 612] >> endobj\n"
                    b"4 0 obj << /Length 12 >>\nstream\nBT (Ok) Tj ET\nendstream\nendobj\n%%EOF\n"
                )
                r_endos = ctrl_mod.controler_fichier(endos_pdf, regles={"max_pages": 5})
                fmt_endos = r_endos.get("details", {}).get("format_page_po", {})
                if fmt_endos.get("us_letter") is not True or fmt_endos.get("orientations_detectees") != ["paysage", "portrait"]:
                    erreurs.append(f"{sid} : endos US Letter paysage rejeté ({fmt_endos})")
                jpg_scan_pdf = tmp_dir / "jpg_scan.pdf"
                jpg_payload = b"\xFF\xD8\xFF\xE0\x00\x10JFIF BT (faux) Tj ET \xFF\xD9"
                jpg_scan_pdf.write_bytes(
                    b"%PDF-1.4\n1 0 obj << /Type /Pages /Kids [2 0 R] /Count 1 >> endobj\n"
                    b"2 0 obj << /Type /Page /Parent 1 0 R /MediaBox [0 0 612 792] >> endobj\n"
                    b"3 0 obj << /Type /XObject /Subtype /Image /Filter /DCTDecode /Length "
                    + str(len(jpg_payload)).encode("ascii")
                    + b" >>\nstream\n"
                    + jpg_payload
                    + b"\nendstream\nendobj\n%%EOF\n"
                )
                r_jpg_scan = ctrl_mod.controler_fichier(jpg_scan_pdf, regles={"max_pages": 5, "exiger_ocr": True})
                if r_jpg_scan.get("details", {}).get("couche_texte") != "absente":
                    erreurs.append(f"{sid} : flux image JPEG avec séquence BT..Tj pris à tort pour couche OCR ({r_jpg_scan.get('details')})")
                try:
                    ctrl_mod._charger_regles(str(tmp_dir / "absent.json"), {})
                    erreurs.append(f"{sid} : --regles JSON absent ignoré silencieusement")
                except FileNotFoundError as exc:
                    # Comportement attendu : --regles pointant vers un fichier absent doit lever FileNotFoundError.
                    if not str(exc):
                        erreurs.append(f"{sid} : exception FileNotFoundError vide pour --regles absent")

                vanish_ctrl = tmp_dir / "vanish_ctrl.docx"
                with zipfile.ZipFile(vanish_ctrl, "w") as zf:
                    zf.writestr("[Content_Types].xml", '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"/>')
                    zf.writestr(
                        "word/document.xml",
                        '<?xml version="1.0"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>'
                        '<w:p><w:r><w:rPr><w:rFonts w:ascii="Times New Roman"/><w:sz w:val="24"/><w:vanish/></w:rPr><w:t>Masqué</w:t></w:r></w:p>'
                        '<w:sectPr><w:pgSz w:w="12240" w:h="15840"/><w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440"/></w:sectPr>'
                        "</w:body></w:document>",
                    )
                    zf.writestr("docProps/app.xml", '<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"><Pages>2</Pages></Properties>')
                r_van_ctrl = ctrl_mod.controler_fichier(vanish_ctrl, regles={"max_pages": 5})
                van_codes = {a["code"] for a in r_van_ctrl.get("bon_de_travail", [])}
                if r_van_ctrl.get("statut_conformite") != "NON_CONFORME" or "SUPPRIMER_TEXTE_MASQUE" not in van_codes:
                    erreurs.append(f"{sid} : w:vanish non rejeté par controler_document ({r_van_ctrl})")

                corrupt_ctrl = tmp_dir / "corps_corrompu.docx"
                with zipfile.ZipFile(corrupt_ctrl, "w") as zf:
                    zf.writestr("word/document.xml", "<<<BROKEN_XML")
                    zf.writestr("docProps/app.xml", '<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"><Pages>2</Pages></Properties>')
                r_corrupt_ctrl = ctrl_mod.controler_fichier(corrupt_ctrl, regles={"max_pages": 5})
                corrupt_codes = {a["code"] for a in r_corrupt_ctrl.get("bon_de_travail", [])}
                if r_corrupt_ctrl.get("statut_conformite") != "A_VERIFIER" or "CORPS_XML_ILLISIBLE" not in corrupt_codes:
                    erreurs.append(f"{sid} : XML corrompu non signalé A_VERIFIER / CORPS_XML_ILLISIBLE ({r_corrupt_ctrl})")

                with contextlib.redirect_stdout(io.StringIO()):
                    rc_clean = ctrl_mod.main([
                        str(clean_docx),
                        "--max-pages", "5",
                        "--police-attendue", "Times New Roman",
                        "--taille-min-pt", "12",
                        "--marge-min-po", "1.0",
                        "--interligne-min", "1.5",
                        "--json",
                    ])
                    rc_van = ctrl_mod.main([str(vanish_ctrl), "--max-pages", "5", "--json"])
                    rc_corrupt = ctrl_mod.main([str(corrupt_ctrl), "--max-pages", "5", "--json"])
                    rc_missing = ctrl_mod.main([str(tmp_dir / "absent_cli.docx"), "--json"])
                if (rc_clean, rc_van, rc_corrupt, rc_missing) != (0, 1, 1, 2):
                    erreurs.append(
                        f"{sid} : codes de sortie CLI attendus (0, 1, 1, 2), obtenu {(rc_clean, rc_van, rc_corrupt, rc_missing)}"
                    )

                old_ctrl_cap = ctrl_mod._MAX_ZIP_MEMBER_BYTES
                try:
                    ctrl_mod._MAX_ZIP_MEMBER_BYTES = 128
                    r_ctrl_cap = ctrl_mod.controler_fichier(clean_docx, regles={"max_pages": 5})
                    with contextlib.redirect_stdout(io.StringIO()):
                        rc_cap = ctrl_mod.main([str(clean_docx), "--max-pages", "5", "--json"])
                    if r_ctrl_cap.get("statut") != "erreur" or rc_cap != 2:
                        erreurs.append(f"{sid} : plafond de décompression controler_document non appliqué ({r_ctrl_cap}, rc={rc_cap})")
                finally:
                    ctrl_mod._MAX_ZIP_MEMBER_BYTES = old_ctrl_cap
        elif outil == "verifier_cotes":
            with tempfile.TemporaryDirectory() as tmp:
                tmp_dir = Path(tmp)
                acte_p = tmp_dir / "demande_modifiee.md"
                bord_p = tmp_dir / "bordereau.md"
                acte_p.write_text(
                    "DEMANDE INTRODUCTIVE MODIFIÉE\n"
                    "1. Voir Pièce P-3.\n"
                    "2. Voir Pièce P-1.\n"
                    "3. [Pièce P-2 retirée].\n"
                    "4. Le contrat est invoqué tel qu'il appert d'une copie du courriel du 5 juin.\n",
                    encoding="utf-8",
                )
                bord_p.write_text(
                    "| Cote | Désignation |\n| P-1 | Contrat |\n| P-2 | Courriel actif |\n| P-3 | Facture |\n",
                    encoding="utf-8",
                )
                res_c = cotes_mod.verifier_ensemble_cotes([acte_p], bordereau=bord_p, mode_modifie=True)
                types_found = {a["type"] for a in res_c.get("anomalies", [])}
                for exp_type in spec["attendu"].get("anomalies_types_contient", []):
                    if exp_type not in types_found:
                        erreurs.append(f"{sid} : anomalie attendue {exp_type!r} absente ({sorted(types_found)})")

                # Cas limites : abréviation légale Acme Inc. + RLRQ/CQLR multi-chapitres + DA-1 + R-1 + P-01..P-02 + longue clause >250 car.
                acte_ok = tmp_dir / "acte_abbrev.md"
                acte_ok.write_text(
                    "1. Tel qu'il appert de la facture de Acme Inc. (RLRQ, c. P-39 et R-20 ; CQLR, chapter I-3), produite sous la cote **Pièce P-01** ;\n"
                    "2. Suite du dossier selon **Pièce P-02**, demande de permission sous **Pièce R-1** et pièce codéfendeur **Exhibit DA-1** ;\n"
                    "3. Moreover, the Defendant duly executed the master commercial lease agreement dated May 14, 2024 governing all premises, maintenance duties, CAM reconciliations and renewal options between the landlord and corporate tenant across every suite, as appears from the executed copy produced in support hereof as **Exhibit P-03** ;\n",
                    encoding="utf-8",
                )
                bord_ok = tmp_dir / "bordereau_abbrev.md"
                bord_ok.write_text(
                    "| Cote | Pièce |\n| P-1 | Facture |\n| P-2 | Contrat |\n| P-3 | Bail commercial |\n| R-1 | Décision |\n| DA-1 | Pièce codéfendeur |\n",
                    encoding="utf-8",
                )
                res_ok = cotes_mod.verifier_ensemble_cotes([acte_ok], bordereau=bord_ok)
                if res_ok.get("nombre_anomalies") != 0:
                    erreurs.append(f"{sid} : faux positif sur abréviation/chapitre/DA-1/clause>250 ({res_ok.get('anomalies')})")

                acte_reutil = tmp_dir / "acte_reutilisee.md"
                acte_reutil.write_text(
                    "DEMANDE MODIFIÉE\n"
                    "1. Voir Pièce P-1.\n"
                    "2. [Pièce P-2 retirée].\n"
                    "3. Voir toujours la Pièce P-2 déjà produite.\n",
                    encoding="utf-8",
                )
                res_reutil = cotes_mod.verifier_ensemble_cotes([acte_reutil], mode_modifie=True)
                if "COTE_GELEE_REUTILISEE" not in {a["type"] for a in res_reutil.get("anomalies", [])}:
                    erreurs.append(f"{sid} : réutilisation de cote retirée dans le même acte non détectée ({res_reutil})")

                bord_colon = tmp_dir / "bordereau_colon.md"
                bord_colon.write_text("P-1 : Contrat\nP-2 : [Retirée]\nP-3 : Facture\n", encoding="utf-8")
                acte_colon = tmp_dir / "acte_colon.md"
                acte_colon.write_text("1. Pièce P-1\n2. Pièce P-2 : [Retirée]\n3. Pièce P-3\n", encoding="utf-8")
                if cotes_mod.main(["--acte", str(acte_colon), "--bordereau", str(bord_colon), "--modifie", "--json"]) != 0:
                    erreurs.append(f"{sid} : P-2 : [Retirée] avec deux-points non reconnu comme cote gelée")

                with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                    rc_cotes_clean = cotes_mod.main(["--acte", str(acte_ok), "--bordereau", str(bord_ok), "--json"])
                    rc_cotes_anom = cotes_mod.main(["--acte", str(acte_p), "--bordereau", str(bord_p), "--modifie", "--json"])
                    rc_cotes_err = cotes_mod.main(["--acte", str(tmp_dir / "absent_acte.md"), "--json"])
                if (rc_cotes_clean, rc_cotes_anom, rc_cotes_err) != (0, 1, 2):
                    erreurs.append(
                        f"{sid} : codes de sortie CLI verifier_cotes attendus (0, 1, 2), obtenu {(rc_cotes_clean, rc_cotes_anom, rc_cotes_err)}"
                    )
        else:
            erreurs.append(f"{sid} : outil de test inconnu {outil!r}")
    return erreurs


def auto_test() -> int:
    scenarios = charger_scenarios()
    erreurs: list[str] = []

    if not scenarios:
        erreurs.append("Aucun scénario trouvé dans evals/scenarios.json.")

    for sc in scenarios:
        for champ in ("doit_contenir", "ne_doit_pas_contenir"):
            for pat in sc.get(champ, []):
                try:
                    re.compile(pat, flags=re.I | re.M)
                except re.error as exc:
                    erreurs.append(f"{sc['id']} ({champ}) : regex invalide {pat!r} ({exc})")

    erreurs.extend(executer_tests_outils(scenarios))

    # Exécuter les tests unitaires sur fixtures du vérificateur statique
    loader = unittest.TestLoader()
    suite = loader.discover(str(Path(__file__).resolve().parent), pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=0)
    unit_res = runner.run(suite)
    if not unit_res.wasSuccessful():
        erreurs.append(
            f"Tests unitaires du vérificateur en échec : "
            f"{len(unit_res.failures)} échec(s), {len(unit_res.errors)} erreur(s)"
        )

    # Auto-vérification du moteur d'évaluation de réponses (positif et négatif)
    sc_rj01 = next((s for s in scenarios if s["id"] == "RJ-01"), None)
    if sc_rj01 is not None:
        ok = evaluer_reponse(
            sc_rj01,
            "En droit civil québécois, la garantie de qualité relève de l'art. 1726 C.c.Q. "
            "et la dénonciation du vice de l'art. 1739 C.c.Q.",
        )
        bad = evaluer_reponse(
            sc_rj01,
            "Selon l'art. 1641 de la Cour de cassation, vous devez agir vite.",
        )
        if not ok["reussi"]:
            erreurs.append(f"Auto-test positif RJ-01 a échoué : {ok}")
        if bad["reussi"]:
            erreurs.append("Auto-test négatif RJ-01 aurait dû détecter art. 1641 / Cour de cassation.")

    sc_rd06 = next((s for s in scenarios if s["id"] == "RD-06"), None)
    if sc_rd06 is not None:
        ok_rd06 = evaluer_reponse(
            sc_rd06,
            "L'avis d'assignation indique 15 jours, ou 30 jours selon l'art. 490 C.p.c. "
            "En vertu de l'art. 101 al. 1 C.p.c., préavis d'au moins 3 jours, sous réserve des "
            "délais particuliers (art. 527 : 5 jours) ; serment requis seulement si la preuve "
            "n'est pas déjà au dossier.",
        )
        if not ok_rd06["reussi"]:
            erreurs.append(f"Auto-test positif RD-06 a échoué : {ok_rd06}")
        bad_rd06 = evaluer_reponse(
            sc_rd06,
            "Avis d'assignation : 15 jours ou 30 jours (art. 490 C.p.c.). "
            "Selon l'art. 101 C.p.c. : notification au moins 5 jours à l'avance (3 jours si urgence), "
            "serment si la preuve n'est pas au dossier.",
        )
        if bad_rd06["reussi"]:
            erreurs.append(
                "Auto-test négatif RD-06 aurait dû détecter l'attribution de 5 jours à l'art. 101."
            )

    sc_rd11 = next((s for s in scenarios if s["id"] == "RD-11"), None)
    if sc_rd11 is not None:
        ok_rd11 = evaluer_reponse(
            sc_rd11,
            "Replace Statement of Claim with Originating Application and Affidavit of Documents "
            "with List of Exhibits. Keep Affidavit (official English term under art. 105 C.C.P.). "
            "Cite article 1457 C.C.Q. (never section, which applies to statutes) and translate the "
            "endos into English.",
        )
        ok_rd11_sworn = evaluer_reponse(
            sc_rd11,
            "Originating Application, Table of Exhibits, Sworn Statement, article 1457 C.C.Q., "
            "section 4 of the statutory act, and English endos.",
        )
        if not ok_rd11["reussi"] or not ok_rd11_sworn["reussi"]:
            erreurs.append(f"Auto-test positif RD-11 a échoué : {ok_rd11} / {ok_rd11_sworn}")
        bad_rd11 = evaluer_reponse(
            sc_rd11,
            "Originating Application with Affidavit of Documents, article 1457 C.C.Q., "
            "section 3 of the statute, and English endos.",
        )
        if bad_rd11["reussi"]:
            erreurs.append(
                "Auto-test négatif RD-11 aurait dû rejeter Affidavit of Documents non remplacé."
            )

    sc_rj06 = next((s for s in scenarios if s["id"] == "RJ-06"), None)
    if sc_rj06 is not None:
        ok_rj06 = evaluer_reponse(
            sc_rj06,
            "Dans le corpus de 110 textes, qccs-dist-mtl a preseance-sur qccs-div-mtl (fr-only). "
            "L'orientation amf-ig-45-106 interprete v-1.1-r.21 sans force de loi ; les directives QCCA restent hors Vague 1.",
        )
        bad_rj06 = evaluer_reponse(
            sc_rj06,
            "Les 97 lois indexées confirment que l'Instruction générale 45-106 a force de loi.",
        )
        if not ok_rj06["reussi"] or bad_rj06["reussi"]:
            erreurs.append(f"Auto-test RJ-06 échoué : ok={ok_rj06}, bad={bad_rj06}")

    sc_pc08 = next((s for s in scenarios if s["id"] == "PC-08"), None)
    if sc_pc08 is not None:
        ok_pc08 = evaluer_reponse(
            sc_pc08,
            "Les vérifications octets, XML Word, OCR/signets PDF et continuité des cotes par controler_document.py "
            "et verifier_cotes.py ont été omises (environnement nuage sans Python). Voir le bon de travail manuel.",
        )
        bad_pc08 = evaluer_reponse(
            sc_pc08,
            "J'ai exécuté controler_document.py avec succès sur votre cahier.",
        )
        if not ok_pc08["reussi"] or bad_pc08["reussi"]:
            erreurs.append(f"Auto-test PC-08 échoué : ok={ok_pc08}, bad={bad_pc08}")

    sc_rj07 = next((s for s in scenarios if s["id"] == "RJ-07"), None)
    if sc_rj07 is not None:
        ok_rj07 = evaluer_reponse(
            sc_rj07,
            "Arrêt obligatoire sur le volet jurisprudentiel suite à [CLEF_ABSENTE] : l'interrogation de juris "
            "exige votre clé API CanLII personnelle active. Rétablir l'accès sur https://acces.poirierlavoie.ca/moi.",
        )
        bad_rj07 = evaluer_reponse(
            sc_rj07,
            "Malgré [CLEF_ABSENTE] sur CanLII (voir acces.poirierlavoie.ca/moi pour arrêt), "
            "2020 QCCA 495 établit que la responsabilité est solidaire.",
        )
        if not ok_rj07["reussi"] or bad_rj07["reussi"]:
            erreurs.append(f"Auto-test RJ-07 échoué : ok={ok_rj07}, bad={bad_rj07}")

    sc_ph104 = next((s for s in scenarios if s["id"] == "PH1-04"), None)
    if sc_ph104 is not None:
        ok_ph104 = evaluer_reponse(
            sc_ph104,
            "Voici le bloc en ligne pour etat-dossier/phase-ouverture-dossier.md. "
            "Tout classement PUBLIC est bloqué (CONFIDENTIEL) ; l'inspection octets/XML/SHA-256 via "
            "inspecter_piece.py a été omise et ajoutée au bon de travail manuel.",
        )
        bad_ph104 = evaluer_reponse(
            sc_ph104,
            "J'ai écrit le fichier etat-dossier/phase-ouverture-dossier.md sur votre disque en bloc CONFIDENTIEL ; "
            "vérification omise au bon de travail.",
        )
        if not ok_ph104["reussi"] or bad_ph104["reussi"]:
            erreurs.append(f"Auto-test PH1-04 échoué : ok={ok_ph104}, bad={bad_ph104}")

    if erreurs:
        for err in erreurs:
            print(err, file=sys.stderr)
        return 1

    print(
        f"Auto-test réussi : {len(scenarios)} scénarios validés, "
        "assertions déterministes des 4 scripts locaux et tests unitaires du vérificateur conformes."
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    _configure_stdio()
    parser = argparse.ArgumentParser(
        description="Suite d'évaluation comportementale de Droit civil québécois."
    )
    parser.add_argument("--liste", action="store_true", help="Lister les scénarios d'évaluation.")
    parser.add_argument(
        "--auto-test",
        action="store_true",
        help="Valider le schéma, compiler les regex et exécuter les tests d'outils déterministes.",
    )
    parser.add_argument(
        "--reponses",
        type=Path,
        default=None,
        help="Fichier JSON {id_scenario: texte_reponse} à noter selon les critères.",
    )
    parser.add_argument("--json", action="store_true", help="Sortie structurée en JSON.")
    args = parser.parse_args(argv)

    scenarios = charger_scenarios()

    if args.liste:
        if args.json:
            print(
                json.dumps(
                    [
                        {
                            "id": s["id"],
                            "competence": s["competence"],
                            "palier": s.get("palier"),
                            "titre": s["titre"],
                            "declencheur_negatif": s.get("declencheur_negatif", False),
                        }
                        for s in scenarios
                    ],
                    ensure_ascii=False,
                    indent=2,
                )
            )
        else:
            for sc in scenarios:
                palier = f" | Palier {sc['palier']}" if sc.get("palier") else ""
                neg = " | [NEG]" if sc.get("declencheur_negatif") else ""
                print(f"{sc['id']} | {sc['competence']}{palier}{neg} | {sc['titre']}")
        return 0

    if args.reponses is not None:
        reponses = json.loads(args.reponses.read_text(encoding="utf-8"))
        if not isinstance(reponses, dict):
            print("Erreur : le fichier de réponses doit contenir un objet JSON.", file=sys.stderr)
            return 2
        resultats = [
            evaluer_reponse(sc, str(reponses.get(sc["id"], "")))
            for sc in scenarios
            if sc["id"] in reponses
        ]
        reussis = sum(1 for r in resultats if r["reussi"])
        rapport = {
            "evalues": len(resultats),
            "reussis": reussis,
            "echoues": len(resultats) - reussis,
            "details": resultats,
        }
        if args.json:
            print(json.dumps(rapport, ensure_ascii=False, indent=2))
        else:
            print(f"Score : {reussis}/{len(resultats)}")
            for r in resultats:
                etat = "OK" if r["reussi"] else "ECHEC"
                print(f"[{etat}] {r['id']} ({r['competence']})")
                if r["manquants"]:
                    print(f"  Manquants : {r['manquants']}")
                if r["interdits_trouves"]:
                    print(f"  Interdits : {r['interdits_trouves']}")
        return 0 if reussis == len(resultats) and resultats else 1

    return auto_test()


if __name__ == "__main__":
    raise SystemExit(main())
