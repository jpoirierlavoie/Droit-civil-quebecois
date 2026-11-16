"""
regenerer_cache_mcp.py
Regénère de façon déterministe les 32 fichiers JSON de schémas d'outils et les 3 instructions.md
dans ~/.gemini/antigravity/mcp/ à partir des descripteurs TypeScript faisant autorité.
Usage:
    python scripts/regenerer_cache_mcp.py          # validation / dry-run
    python scripts/regenerer_cache_mcp.py --apply  # écriture sur disque
"""
import os
import sys
import json
import shutil
import subprocess
from pathlib import Path

BASE_CACHE = Path(
    os.environ.get(
        "ANTIGRAVITY_MCP_CACHE_DIR",
        Path(os.environ.get("USERPROFILE", Path.home())) / ".gemini" / "antigravity" / "mcp",
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

def main():
    apply_mode = "--apply" in sys.argv
    print(f"[*] Régénération du cache Antigravity MCP (mode: {'APPLY' if apply_mode else 'DRY-RUN'})...")
    
    servers = [load_legislation(), load_jurisprudence(), load_outils()]
    total_tools = 0

    if apply_mode and BASE_CACHE.is_dir():
        active_folders = {srv_folder for srv_folder, _, _ in servers}
        for existing in sorted(BASE_CACHE.iterdir()):
            if (
                existing.is_dir()
                and (
                    existing.name.startswith("droit-civil-quebecois_")
                    or existing.name.startswith("pratique-civile-quebecoise_")
                )
                and existing.name not in active_folders
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
            assert len(tool_data["description"]) > 50, f"Description tronquée pour {name}"
            params = tool_data["parameters"]
            assert params.get("type") == "object", f"Parameters non-object pour {name}"
            assert params.get("additionalProperties") is False, f"additionalProperties non-false pour {name}"
            props = params.get("properties", {})
            for p_name, p_schema in props.items():
                assert bool(p_schema.get("description")), f"{name}.{p_name} sans description"
                if p_schema.get("type") == "array":
                    assert bool(p_schema.get("items")), f"{name}.{p_name} array sans items"
            
            if apply_mode:
                out_path = target_dir / f"{name}.json"
                with open(out_path, "w", encoding="utf-8", newline="\n") as f:
                    f.write(json.dumps(tool_data, indent=2, ensure_ascii=False) + "\n")
            print(f"    - {name}.json (desc: {len(tool_data['description'])} car., {len(props)} props)")

    print(f"\n[OK] {total_tools}/32 outils vérifiés avec succès.")

if __name__ == "__main__":
    main()
