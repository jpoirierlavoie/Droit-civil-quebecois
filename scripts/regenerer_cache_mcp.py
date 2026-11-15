"""
regenerer_cache_mcp.py
Regénère de façon déterministe les 26 fichiers JSON de schémas d'outils et les 3 instructions.md
dans ~/.gemini/antigravity/mcp/ à partir des descripteurs TypeScript faisant autorité.
Usage:
    python scripts/regenerer_cache_mcp.py          # validation / dry-run
    python scripts/regenerer_cache_mcp.py --apply  # écriture sur disque
"""
import os
import sys
import json
import subprocess
from pathlib import Path

BASE_CACHE = Path(os.environ.get("USERPROFILE", Path.home())) / ".gemini" / "antigravity" / "mcp"
REPO_LEGISLATION = Path(r"C:\Users\MeJasonPoirierLavoie\MCP-Legislation")
REPO_JURISPRUDENCE = Path(r"C:\Users\MeJasonPoirierLavoie\MCP-Jurisprudence")
REPO_OUTILS = Path(r"C:\Users\MeJasonPoirierLavoie\pratique-civile-outils")

def load_legislation():
    ref_path = REPO_LEGISLATION / "fixtures" / "tools-list.reference.json"
    with open(ref_path, "r", encoding="utf-8") as f:
        tools = json.load(f)
    
    script = "import { INSTRUCTIONS } from './src/serveur.ts'; console.log(JSON.stringify(INSTRUCTIONS));"
    res = subprocess.run(
        ["npx.cmd", "tsx", "-e", script],
        cwd=REPO_LEGISLATION,
        capture_output=True,
        text=True,
        encoding="utf-8"
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
    return "pratique-civile-quebecoise_legislation", tool_dict, instructions

def load_jurisprudence():
    script = "import { listToolDescriptors, INSTRUCTIONS } from './src/mcp/registry.ts'; console.log(JSON.stringify({ tools: listToolDescriptors(), instructions: INSTRUCTIONS }));"
    res = subprocess.run(
        ["npx.cmd", "tsx", "-e", script],
        cwd=REPO_JURISPRUDENCE,
        capture_output=True,
        text=True,
        encoding="utf-8"
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
    return "pratique-civile-quebecoise_jurisprudence", tool_dict, data["instructions"]

def load_outils():
    script = "import { listToolDescriptors, INSTRUCTIONS } from './src/mcp/server.ts'; console.log(JSON.stringify({ tools: listToolDescriptors(), instructions: INSTRUCTIONS }));"
    res = subprocess.run(
        ["npx.cmd", "tsx", "-e", script],
        cwd=REPO_OUTILS,
        capture_output=True,
        text=True,
        encoding="utf-8"
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
    return "pratique-civile-quebecoise_pratique-civile-outils", tool_dict, data["instructions"]

def main():
    apply_mode = "--apply" in sys.argv
    print(f"[*] Régénération du cache Antigravity MCP (mode: {'APPLY' if apply_mode else 'DRY-RUN'})...")
    
    servers = [load_legislation(), load_jurisprudence(), load_outils()]
    total_tools = 0
    
    for srv_folder, tools, instructions in servers:
        target_dir = BASE_CACHE / srv_folder
        print(f"\n[+] Serveur {srv_folder} : {len(tools)} outils")
        total_tools += len(tools)
        
        if apply_mode:
            target_dir.mkdir(parents=True, exist_ok=True)
            (target_dir / "instructions.md").write_text(instructions.strip() + "\n", encoding="utf-8")
            
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
                out_path.write_text(json.dumps(tool_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            print(f"    - {name}.json (desc: {len(tool_data['description'])} car., {len(props)} props)")

    print(f"\n[OK] {total_tools}/26 outils vérifiés avec succès.")

if __name__ == "__main__":
    main()
