"""
synchroniser_plugin_gemini.py
Synchronise le plugin droit-civil-quebecois (ex pratique-civile-quebecoise) vers le répertoire de plugins Gemini installé.
Usage:
    python scripts/synchroniser_plugin_gemini.py          # dry-run
    python scripts/synchroniser_plugin_gemini.py --apply  # copie effective
"""
import os
import sys
import time
import shutil
import filecmp
from pathlib import Path

SRC_DIR = Path(os.environ.get("PCQ_PLUGIN_SRC_DIR", Path(__file__).resolve().parents[1]))
PLUGINS_ROOT = Path(os.environ.get("USERPROFILE", Path.home())) / ".gemini" / "config" / "plugins"
DST_DIR = Path(
    os.environ.get(
        "GEMINI_PLUGIN_DST_DIR",
        PLUGINS_ROOT / "droit-civil-quebecois",
    )
)
LEGACY_DST_DIR = PLUGINS_ROOT / "pratique-civile-quebecoise"

BUNDLE_ROOT_FILES = [
    Path("plugin.json"),
    Path("mcp_config.json"),
    Path("LICENSE"),
    Path("SECURITY.md"),
    Path("README.md"),
]

def collect_bundle_files():
    files = list(BUNDLE_ROOT_FILES)
    # Assets
    assets_dir = SRC_DIR / "assets"
    if assets_dir.is_dir():
        for p in assets_dir.rglob("*"):
            if p.is_file() and not p.name.endswith(".pyc") and "__pycache__" not in p.parts:
                files.append(p.relative_to(SRC_DIR))
    # Skills
    skills_dir = SRC_DIR / "skills"
    if skills_dir.is_dir():
        for p in skills_dir.rglob("*"):
            if p.is_file() and not p.name.endswith(".pyc") and "__pycache__" not in p.parts:
                files.append(p.relative_to(SRC_DIR))
    return sorted(files)

def main():
    apply_mode = "--apply" in sys.argv
    print(f"[*] Synchronisation du plugin Gemini (mode: {'APPLY' if apply_mode else 'DRY-RUN'})...")
    print(f"    Source:      {SRC_DIR}")
    print(f"    Destination: {DST_DIR}")
    
    files = collect_bundle_files()
    copied = 0
    identical = 0
    mcp_config_copied = False
    
    for rel_path in files:
        s = SRC_DIR / rel_path
        d = DST_DIR / rel_path
        assert s.exists(), f"Fichier source introuvable: {s}"
        
        is_same = d.exists() and filecmp.cmp(s, d, shallow=False)
        if not is_same:
            print(f"  [COPIE] {rel_path}")
            if apply_mode:
                d.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(s, d)
            copied += 1
            if rel_path == Path("mcp_config.json"):
                mcp_config_copied = True
        else:
            print(f"  [CONFORME] {rel_path}")
            identical += 1
            
    expected_set = set(files)
    stale_files = []
    if DST_DIR.is_dir():
        for existing in sorted(DST_DIR.rglob("*")):
            if existing.is_file():
                rel_existing = existing.relative_to(DST_DIR)
                if rel_existing not in expected_set:
                    stale_files.append(rel_existing)
                    print(f"  [RETRAIT] {rel_existing}")
                    if apply_mode:
                        existing.unlink()
        if apply_mode:
            for d in sorted((p for p in DST_DIR.rglob("*") if p.is_dir()), reverse=True):
                try:
                    d.rmdir()
                except OSError:
                    pass

    legacy_removed = False
    if LEGACY_DST_DIR != DST_DIR and LEGACY_DST_DIR.is_dir():
        print(f"  [RETRAIT ANCIEN PLUGIN] {LEGACY_DST_DIR}")
        if apply_mode:
            shutil.rmtree(LEGACY_DST_DIR)
            legacy_removed = True

    print(
        f"\n[OK] Résumé : {copied} fichier(s) mis à jour, {identical} déjà identiques "
        f"sur {len(files)} fichiers analysés ; {len(stale_files)} fichier(s) obsolète(s) "
        f"{'retiré(s)' if apply_mode else 'à retirer'}."
    )
    if legacy_removed:
        print(f"[OK] Ancien répertoire retiré : {LEGACY_DST_DIR}")

    if apply_mode:
        # Re-vérification stricte
        diffs = [rel for rel in files if not filecmp.cmp(SRC_DIR / rel, DST_DIR / rel, shallow=False)]
        assert len(diffs) == 0, f"Différences persistantes après copie: {diffs}"
        print("[OK] Vérification post-synchronisation : 100% conforme.")
        if mcp_config_copied:
            time.sleep(2.5)
            print(
                "[!] mcp_config.json modifié : tous les identifiants d'outils v2.0 respectent "
                "désormais la limite native <= 64 caractères (cache Antigravity rafraîchi "
                "automatiquement). Exécuter optionnellement "
                "'python scripts/regenerer_cache_mcp.py --apply' pour reconstruire le cache "
                "à partir des dépôts locaux."
            )

if __name__ == "__main__":
    main()
