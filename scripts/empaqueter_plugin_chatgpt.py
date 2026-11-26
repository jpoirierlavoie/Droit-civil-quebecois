#!/usr/bin/env python3
"""
empaqueter_plugin_chatgpt.py
Empaquete le greffon universel ChatGPT (Web et Desktop) sans badge « Desktop only »
au format Portable Agent Plugins 1.0 dans dist/droit-civil-quebecois-chatgpt-universal.zip.

Usage :
    python scripts/empaqueter_plugin_chatgpt.py          # validation à sec (dry-run)
    python scripts/empaqueter_plugin_chatgpt.py --apply  # génère l'archive ZIP et retire les anciennes
"""

from __future__ import annotations

import json
import os
import sys
import zipfile
from pathlib import Path

SRC_DIR = Path(os.environ.get("DCQ_PLUGIN_SRC_DIR", Path(__file__).resolve().parents[1])).resolve()
AGENT_PLUGINS_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
UNIVERSAL_ZIP_NAME = "droit-civil-quebecois-chatgpt-universal.zip"
STALE_ZIP_NAMES = (
    "droit-civil-quebecois-chatgpt-plugin.zip",
    "droit-civil-quebecois-chatgpt-skills-only.zip",
)
FORBIDDEN_ARCHIVE_NAMES = frozenset(
    {
        ".mcp.json",
        "mcp.json",
        ".codex-plugin",
        ".antigravity-plugin",
        ".claude-plugin",
        ".agents",
        ".github",
        ".app.json",
        "mcp_config.json",
        "gemini-extension.json",
        "AGENTS.md",
        "CLAUDE.md",
        "GEMINI.md",
    }
)
FORBIDDEN_CODEX_KEYS = frozenset({"mcpServers", "apps", "requires_local_executor"})
FORBIDDEN_TOP_LEVEL_KEYS = frozenset({"skills", "mcpServers", "apps", "requires_local_executor"})
PORTABLE_METADATA_KEYS = (
    "name",
    "version",
    "description",
    "author",
    "homepage",
    "repository",
    "license",
    "keywords",
)
ROOT_DOCS = ("LICENSE", "NOTICE", "SECURITY.md", "README.md")
MAX_SKILL_IDENTITY_LEN = 64
_FIXED_ZIP_DT = (2026, 1, 1, 0, 0, 0)


def _ecrire_entree_deterministe(
    zf: zipfile.ZipFile, arcname: str, data: bytes, *, executable: bool = False
) -> None:
    info = zipfile.ZipInfo(filename=arcname, date_time=_FIXED_ZIP_DT)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.create_system = 3
    mode = 0o100755 if executable else 0o100644
    info.external_attr = (mode & 0xFFFF) << 16
    zf.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def construire_manifeste_portable(codex_manifest: dict[str, object]) -> dict[str, object]:
    """Construit le manifeste racine plugin.json conforme à Agent Plugins 1.0.0."""
    for interdit in sorted(FORBIDDEN_CODEX_KEYS):
        if interdit in codex_manifest:
            raise ValueError(
                f"Clé interdite dans .codex-plugin/plugin.json pour un paquet universel : {interdit}"
            )

    portable: dict[str, object] = {"$schema": AGENT_PLUGINS_SCHEMA}
    for key in PORTABLE_METADATA_KEYS:
        if key not in codex_manifest:
            raise ValueError(f"Champ requis absent de .codex-plugin/plugin.json : {key}")
        portable[key] = codex_manifest[key]

    interface = codex_manifest.get("interface")
    if not isinstance(interface, dict):
        raise ValueError("Objet 'interface' absent de .codex-plugin/plugin.json")

    portable["extensions"] = {
        "com.openai": {
            "interface": interface,
        }
    }
    for interdit in sorted(FORBIDDEN_TOP_LEVEL_KEYS):
        if interdit in portable:
            raise ValueError(f"Clé top-level interdite dans le manifeste portable : {interdit}")
    return portable


def collecter_fichiers_archive(src_dir: Path) -> list[tuple[str, Path]]:
    """Collecte les fichiers du paquet universel triés en chemins POSIX relatifs."""
    entrees: list[tuple[str, Path]] = []

    for rel in ROOT_DOCS:
        chemin = src_dir / rel
        if not chemin.is_file():
            raise FileNotFoundError(f"Fichier racine manquant : {chemin}")
        entrees.append((rel, chemin))

    for dossier in ("assets", "agents", "skills"):
        base = src_dir / dossier
        if not base.is_dir():
            raise FileNotFoundError(f"Répertoire requis manquant : {base}")
        for chemin in sorted(base.rglob("*")):
            if not chemin.is_file():
                continue
            if chemin.name.endswith(".pyc") or "__pycache__" in chemin.parts:
                continue
            rel_posix = chemin.relative_to(src_dir).as_posix()
            entrees.append((rel_posix, chemin))

    return sorted(entrees, key=lambda item: item[0])


def valider_entrees_archive(nom_plugin: str, noms_archive: list[str]) -> None:
    """Vérifie la sûreté des chemins et la conformité OpenAI avant et après écriture."""
    noms_set = set(noms_archive)
    skill_dirs: set[str] = set()
    for nom in noms_archive:
        if not nom or nom != nom.strip():
            raise ValueError(f"Nom d'entrée invalide dans l'archive : {nom!r}")
        if "\\" in nom or nom.startswith("/"):
            raise ValueError(f"Chemin non POSIX ou absolu dans l'archive : {nom}")
        segments = nom.split("/")
        if any(seg in ("", ".", "..") for seg in segments):
            raise ValueError(f"Segment de chemin dangereux dans l'archive : {nom}")
        if any(seg in FORBIDDEN_ARCHIVE_NAMES for seg in segments):
            raise ValueError(f"Fichier ou dossier exclu présent dans l'archive : {nom}")
        if len(segments) >= 2 and segments[0] == "skills":
            skill_dirs.add(segments[1])
        elif segments[0] == "agents":
            if len(segments) != 2 or not segments[1].endswith(".md"):
                raise ValueError(f"Entrée agents/ invalide dans l'archive : {nom}")
            agent_id = f"{nom_plugin}:{segments[1][:-3]}"
            if len(agent_id) > MAX_SKILL_IDENTITY_LEN:
                raise ValueError(
                    f"Identifiant persona trop long ({len(agent_id)} > {MAX_SKILL_IDENTITY_LEN}) : {agent_id}"
                )

    if not skill_dirs:
        raise ValueError("Aucune compétence trouvée sous skills/")

    for skill in sorted(skill_dirs):
        if f"skills/{skill}/SKILL.md" not in noms_set:
            raise ValueError(f"SKILL.md manquant pour la compétence : {skill}")
        identite = f"{nom_plugin}:{skill}"
        if len(identite) > MAX_SKILL_IDENTITY_LEN:
            raise ValueError(
                f"Identifiant composé trop long ({len(identite)} > {MAX_SKILL_IDENTITY_LEN}) : {identite}"
            )


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    apply_mode = "--apply" in args

    codex_path = SRC_DIR / ".codex-plugin" / "plugin.json"
    if not codex_path.is_file():
        raise FileNotFoundError(f"Manifeste source introuvable : {codex_path}")

    codex_manifest = json.loads(codex_path.read_text(encoding="utf-8"))
    if not isinstance(codex_manifest, dict):
        raise ValueError(".codex-plugin/plugin.json doit contenir un objet JSON")

    portable_manifest = construire_manifeste_portable(codex_manifest)
    root_manifest_path = SRC_DIR / "plugin.json"
    if not root_manifest_path.is_file():
        raise FileNotFoundError(f"Manifeste racine introuvable : {root_manifest_path}")
    root_manifest = json.loads(root_manifest_path.read_text(encoding="utf-8"))
    if root_manifest != portable_manifest:
        raise ValueError(
            "plugin.json racine diverge de la forme portable construite depuis .codex-plugin/plugin.json"
        )
    manifest_bytes = (json.dumps(portable_manifest, ensure_ascii=False, indent=2) + "\n").encode(
        "utf-8"
    )
    entrees = collecter_fichiers_archive(SRC_DIR)
    noms_archive = ["plugin.json", *(rel for rel, _ in entrees)]
    nom_plugin = str(portable_manifest["name"])
    valider_entrees_archive(nom_plugin, noms_archive)

    dist_dir = SRC_DIR / "dist"
    zip_path = dist_dir / UNIVERSAL_ZIP_NAME
    stale_present = [dist_dir / name for name in STALE_ZIP_NAMES if (dist_dir / name).exists()]

    print(
        f"[*] Empaquetage universel ChatGPT ({'APPLY' if apply_mode else 'DRY-RUN'}) : "
        f"{len(noms_archive)} fichier(s)"
    )
    print(f"    Source : {SRC_DIR}")
    print(f"    Cible  : {zip_path}")

    if not apply_mode:
        for stale in stale_present:
            print(f"  [RETRAIT PRÉVU] {stale.relative_to(SRC_DIR).as_posix()}")
        print("[OK] Validation à sec réussie.")
        return 0

    dist_dir.mkdir(parents=True, exist_ok=True)
    tmp_path = dist_dir / f".{UNIVERSAL_ZIP_NAME}.tmp"
    try:
        with zipfile.ZipFile(tmp_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
            _ecrire_entree_deterministe(zf, "plugin.json", manifest_bytes, executable=False)
            for rel, chemin in entrees:
                _ecrire_entree_deterministe(
                    zf, rel, chemin.read_bytes(), executable=rel.endswith(".py")
                )

        with zipfile.ZipFile(tmp_path, "r") as zf:
            bad = zf.testzip()
            if bad is not None:
                raise RuntimeError(f"Archive ZIP corrompue sur l'entrée : {bad}")
            actual_names = zf.namelist()
            valider_entrees_archive(nom_plugin, actual_names)
            parsed_root = json.loads(zf.read("plugin.json").decode("utf-8"))
            if parsed_root.get("$schema") != AGENT_PLUGINS_SCHEMA:
                raise RuntimeError("Schéma plugin.json inattendu dans l'archive générée")
            if any(k in parsed_root for k in FORBIDDEN_TOP_LEVEL_KEYS):
                raise RuntimeError("Clé top-level interdite dans plugin.json de l'archive")
    except Exception:
        tmp_path.unlink(missing_ok=True)
        raise

    os.replace(tmp_path, zip_path)

    for stale in stale_present:
        stale.unlink()
        print(f"  [RETRAIT] {stale.relative_to(SRC_DIR).as_posix()}")

    print(f"[OK] Archive générée et vérifiée : {zip_path} ({zip_path.stat().st_size} octets)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
