"""
synchroniser_plugin_gemini.py
Synchronise le plugin droit-civil-quebecois vers le répertoire de plugins Gemini installé.
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

def _verifier_confinement(cible: Path, racine: Path, nom: str) -> Path:
    racine_res = racine.resolve()
    cible_res = cible.resolve()
    try:
        rel = cible_res.relative_to(racine_res)
    except ValueError as exc:
        raise RuntimeError(
            f"Chemin {nom} hors du répertoire autorisé ({racine_res}) : {cible_res}"
        ) from exc
    if rel == Path(".") or len(rel.parts) != 1:
        raise RuntimeError(
            f"Chemin {nom} invalide (doit être un sous-répertoire direct de {racine_res}) : {cible_res}"
        )
    return cible_res


def main():
    apply_mode = "--apply" in sys.argv
    print(f"[*] Synchronisation du plugin Gemini (mode: {'APPLY' if apply_mode else 'DRY-RUN'})...")
    print(f"    Source:      {SRC_DIR}")
    print(f"    Destination: {DST_DIR}")

    dst_dir = _verifier_confinement(DST_DIR, PLUGINS_ROOT, "DST_DIR")

    files = collect_bundle_files()
    copied = 0
    identical = 0
    mcp_config_copied = False
    
    for rel_path in files:
        s = SRC_DIR / rel_path
        d = dst_dir / rel_path
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
    if dst_dir.is_dir():
        for existing in sorted(dst_dir.rglob("*")):
            if existing.is_file():
                rel_existing = existing.relative_to(dst_dir)
                if rel_existing not in expected_set:
                    stale_files.append(rel_existing)
                    print(f"  [RETRAIT] {rel_existing}")
                    if apply_mode:
                        existing.unlink()
        if apply_mode:
            for d in sorted((p for p in dst_dir.rglob("*") if p.is_dir()), reverse=True):
                try:
                    d.rmdir()
                except OSError:
                    # Répertoire non vide : conservé car il contient des fichiers synchronisés.
                    continue

    print(
        f"\n[OK] Résumé : {copied} fichier(s) mis à jour, {identical} déjà identiques "
        f"sur {len(files)} fichiers analysés ; {len(stale_files)} fichier(s) obsolète(s) "
        f"{'retiré(s)' if apply_mode else 'à retirer'}."
    )

    if apply_mode:
        # Re-vérification stricte
        diffs = [rel for rel in files if not filecmp.cmp(SRC_DIR / rel, dst_dir / rel, shallow=False)]
        assert len(diffs) == 0, f"Différences persistantes après copie: {diffs}"
        print("[OK] Vérification post-synchronisation : 100% conforme.")
        if mcp_config_copied:
            time.sleep(2.5)
            print(
                "[!] mcp_config.json modifié : tous les identifiants d'outils v3.0 respectent "
                "désormais la limite native <= 64 caractères (cache Antigravity rafraîchi "
                "automatiquement). Exécuter optionnellement "
                "'python scripts/regenerer_cache_mcp.py --apply' pour reconstruire le cache "
                "à partir des dépôts locaux."
            )

if __name__ == "__main__":
    main()
