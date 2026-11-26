#!/usr/bin/env python3
"""
regenerer_cache_mcp.py (script mainteneur uniquement)
Regénère de façon déterministe les 37 fichiers JSON de schémas d'outils et les 3 instructions.md
dans ~/.gemini/antigravity/mcp/ à partir des descripteurs TypeScript faisant autorité.
Prérequis : clones locaux frères de MCP-Legislation, MCP-Jurisprudence et MCP-Outils + Node.js (`npx tsx`).
Usage:
    python scripts/regenerer_cache_mcp.py                        # validation / dry-run (all)
    python scripts/regenerer_cache_mcp.py --server outils --apply  # écriture ciblée sur disque
    python scripts/regenerer_cache_mcp.py --apply                # écriture complète sur disque
"""
import argparse
import os
import json
import shutil
import subprocess
from pathlib import Path

BASE_CACHE = Path(
    os.environ.get(
        "ANTIGRAVITY_MCP_CACHE_DIR",
        Path.home() / ".gemini" / "antigravity" / "mcp",
    )
)
PLUGIN_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_PARENT = PLUGIN_ROOT.parent
REPO_LEGISLATION = Path(os.environ.get("MCP_LEGISLATION_REPO", WORKSPACE_PARENT / "MCP-Legislation"))
REPO_JURISPRUDENCE = Path(os.environ.get("MCP_JURISPRUDENCE_REPO", WORKSPACE_PARENT / "MCP-Jurisprudence"))


def _resolve_outils_repo(workspace_parent: Path) -> Path:
    env_override = os.environ.get("MCP_OUTILS_REPO")
    if env_override:
        return Path(env_override)
    preferred = workspace_parent / "MCP-Outils"
    if preferred.is_dir():
        return preferred
    for candidate in sorted(workspace_parent.iterdir()):
        pkg = candidate / "package.json"
        if candidate.is_dir() and pkg.is_file():
            try:
                if json.loads(pkg.read_text(encoding="utf-8")).get("name") == "mcp-outils":
                    return candidate
            except Exception:
                continue
    return preferred


REPO_OUTILS = _resolve_outils_repo(WORKSPACE_PARENT)
NPX_BIN = shutil.which("npx.cmd" if os.name == "nt" else "npx") or ("npx.cmd" if os.name == "nt" else "npx")

def load_legislation():
    ref_path = REPO_LEGISLATION / "fixtures" / "tools-list.reference.json"
    with open(ref_path, "r", encoding="utf-8") as f:
        tools = json.load(f)
    
    script = "import { INSTRUCTIONS } from './src/serveur.ts'; console.log(JSON.stringify(INSTRUCTIONS));"
    res = subprocess.run(
        [NPX_BIN, "--yes", "tsx", "-e", script],
        cwd=REPO_LEGISLATION,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
    )
    if res.returncode != 0:
        raise RuntimeError(f"Legislation INSTRUCTIONS extraction failed:\n{res.stderr}")
    out = res.stdout[res.stdout.find('"'):].strip()
    instructions = json.loads(out)
    
    tool_dict = {}
    for t in tools:
        tool_dict[t["name"]] = {
            "name": t["name"],
            "description": t["description"],
            "parameters": t["inputSchema"]
        }
    return "droit-civil-quebecois_lois", tool_dict, instructions

def load_jurisprudence():
    script = "import { listToolDescriptors, INSTRUCTIONS } from './src/mcp/registry.ts'; console.log(JSON.stringify({ tools: listToolDescriptors(), instructions: INSTRUCTIONS }));"
    res = subprocess.run(
        [NPX_BIN, "--yes", "tsx", "-e", script],
        cwd=REPO_JURISPRUDENCE,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
    )
    if res.returncode != 0:
        raise RuntimeError(f"Jurisprudence extraction failed:\n{res.stderr}")
    out = res.stdout[res.stdout.find("{"):]
    data = json.loads(out)
    
    tool_dict = {}
    for t in data["tools"]:
        tool_dict[t["name"]] = {
            "name": t["name"],
            "description": t["description"],
            "parameters": t["inputSchema"]
        }
    return "droit-civil-quebecois_juris", tool_dict, data["instructions"]

def load_outils():
    script = "import { listToolDescriptors, INSTRUCTIONS } from './src/mcp/server.ts'; console.log(JSON.stringify({ tools: listToolDescriptors(), instructions: INSTRUCTIONS }));"
    res = subprocess.run(
        [NPX_BIN, "--yes", "tsx", "-e", script],
        cwd=REPO_OUTILS,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
    )
    if res.returncode != 0:
        raise RuntimeError(f"Outils extraction failed:\n{res.stderr}")
    out = res.stdout[res.stdout.find("{"):]
    data = json.loads(out)
    
    tool_dict = {}
    for t in data["tools"]:
        tool_dict[t["name"]] = {
            "name": t["name"],
            "description": t["description"],
            "parameters": t["inputSchemaJson"]
        }
    return "droit-civil-quebecois_outils", tool_dict, data["instructions"]

ALL_CACHE_FOLDERS = {
    "droit-civil-quebecois_lois",
    "droit-civil-quebecois_juris",
    "droit-civil-quebecois_outils",
}
EXPECTED_COUNTS = {"lois": 10, "juris": 12, "outils": 15, "all": 37}


def main():
    parser = argparse.ArgumentParser(
        description="Régénère de façon déterministe les fichiers JSON de schémas d'outils Antigravity MCP."
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Écrire les fichiers générés dans le cache Antigravity MCP.",
    )
    parser.add_argument(
        "--server",
        choices=["lois", "juris", "outils", "all"],
        default="all",
        help="Serveur MCP ciblé (défaut: all).",
    )
    args = parser.parse_args()
    apply_mode = args.apply
    print(
        f"[*] Régénération du cache Antigravity MCP (mode: {'APPLY' if apply_mode else 'DRY-RUN'}, server: {args.server})..."
    )

    loaders = {
        "lois": load_legislation,
        "juris": load_jurisprudence,
        "outils": load_outils,
    }
    selected_keys = ["lois", "juris", "outils"] if args.server == "all" else [args.server]
    servers = [loaders[k]() for k in selected_keys]
    total_tools = 0

    if apply_mode and BASE_CACHE.is_dir():
        for existing in sorted(BASE_CACHE.iterdir()):
            if (
                existing.is_dir()
                and existing.name.startswith("droit-civil-quebecois_")
                and existing.name not in ALL_CACHE_FOLDERS
            ):
                shutil.rmtree(existing)
                print(f"\n[-] Ancien répertoire de cache retiré : {existing.name}")
    
    for srv_folder, tools, instructions in servers:
        target_dir = BASE_CACHE / srv_folder
        print(f"\n[+] Serveur {srv_folder} : {len(tools)} outils")
        total_tools += len(tools)
        
        if apply_mode:
            target_dir.mkdir(parents=True, exist_ok=True)
            for existing_json in target_dir.glob("*.json"):
                if existing_json.stem not in tools:
                    existing_json.unlink()
            with open(target_dir / "instructions.md", "w", encoding="utf-8", newline="\n") as f:
                f.write(instructions.strip() + "\n")
            
        for name, tool_data in sorted(tools.items()):
            # Vérifications d'intégrité
            if len(tool_data["description"]) <= 50:
                raise ValueError(f"Description tronquée pour {name}")
            params = tool_data["parameters"]
            if params.get("type") != "object":
                raise ValueError(f"Parameters non-object pour {name}")
            if params.get("additionalProperties") is not False:
                raise ValueError(f"additionalProperties non-false pour {name}")
            props = params.get("properties", {})
            for p_name, p_schema in props.items():
                if not p_schema.get("description"):
                    raise ValueError(f"{name}.{p_name} sans description")
                if p_schema.get("type") == "array" and not p_schema.get("items"):
                    raise ValueError(f"{name}.{p_name} array sans items")
            
            if apply_mode:
                out_path = target_dir / f"{name}.json"
                with open(out_path, "w", encoding="utf-8", newline="\n") as f:
                    f.write(json.dumps(tool_data, indent=2, ensure_ascii=False) + "\n")
            print(f"    - {name}.json (desc: {len(tool_data['description'])} car., {len(props)} props)")

    expected_total = EXPECTED_COUNTS[args.server]
    print(f"\n[OK] {total_tools}/{expected_total} outils vérifiés avec succès.")

if __name__ == "__main__":
    main()
