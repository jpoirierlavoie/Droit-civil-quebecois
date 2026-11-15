"""
synchroniser_plugin_gemini.py
Synchronise le plugin pratique-civile-quebecoise vers le répertoire de plugins Gemini installé.
Usage:
    python scripts/synchroniser_plugin_gemini.py          # dry-run
    python scripts/synchroniser_plugin_gemini.py --apply  # copie effective
"""
import os
import sys
import shutil
import filecmp
from pathlib import Path

SRC_DIR = Path(os.environ.get("PCQ_PLUGIN_SRC_DIR", Path(__file__).resolve().parents[1]))
DST_DIR = Path(
    os.environ.get(
        "GEMINI_PLUGIN_DST_DIR",
        Path(os.environ.get("USERPROFILE", Path.home())) / ".gemini" / "config" / "plugins" / "pratique-civile-quebecoise",
    )
)

BUNDLE_ROOT_FILES = [
    Path("plugin.json"),
    Path("mcp_config.json"),
    Path("LICENSE"),
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
        else:
            print(f"  [CONFORME] {rel_path}")
            identical += 1
            
    print(f"\n[OK] Résumé : {copied} fichier(s) mis à jour, {identical} déjà identiques sur {len(files)} fichiers analysés.")
    
    if apply_mode:
        # Re-vérification stricte
        diffs = [rel for rel in files if not filecmp.cmp(SRC_DIR / rel, DST_DIR / rel, shallow=False)]
        assert len(diffs) == 0, f"Différences persistantes après copie: {diffs}"
        print("[OK] Vérification post-synchronisation : 100% conforme.")

if __name__ == "__main__":
    main()
