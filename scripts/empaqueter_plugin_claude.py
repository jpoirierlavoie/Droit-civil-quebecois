#!/usr/bin/env python3

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path
import tempfile

SRC_DIR = Path(os.environ.get("DCQ_PLUGIN_SRC_DIR", Path(__file__).resolve().parents[1])).resolve()
MAX_CLAUDE_FILES = 512
MAX_CLAUDE_FILE_BYTES = 262144
MAX_SKILL_IDENTITY_LEN = 64
_SKILL_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_BRANCH_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9._/-]{0,63}$")
_ROOT_DOCS = ("LICENSE", "NOTICE", "SECURITY.md", "README.md")
_REQUIRED_CLAUDE_FILES = (".claude-plugin/plugin.json", ".mcp.json", *_ROOT_DOCS)
_FORBIDDEN_NAMES = frozenset(
    {
        "AGENTS.md",
        "CLAUDE.md",
        "CLAUDE.local.md",
        "GEMINI.md",
        "marketplace.json",
        ".codex-plugin",
        ".antigravity-plugin",
        ".agents",
        ".github",
        "mcp_config.json",
        "gemini-extension.json",
        "verifier.py",
        "verifier_tout.py",
        "evals",
        "scripts",
    }
)
_FORBIDDEN_LOWER_BASENAMES = frozenset({"agents.md", "claude.md", "claude.local.md", "gemini.md"})


def _valider_nom_branche(branch: str) -> str:
    if (
        not _BRANCH_NAME_RE.match(branch)
        or branch == "main"
        or ".." in branch
        or "//" in branch
        or branch.startswith("/")
        or branch.endswith(("/", ".", ".lock"))
    ):
        raise ValueError(f"Nom de branche cible invalide : {branch!r}")
    return branch


def _charger_json_objet(chemin: Path, label: str) -> dict[str, object]:
    import json

    if not chemin.is_file():
        raise FileNotFoundError(f"Fichier requis introuvable : {chemin}")
    data = json.loads(chemin.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{label} doit contenir un objet JSON")
    return data


def collecter_fichiers_claude(src_dir: Path) -> tuple[list[tuple[str, Path]], dict[str, object], str]:
    manifest_path = src_dir / ".claude-plugin" / "plugin.json"
    manifest = _charger_json_objet(manifest_path, ".claude-plugin/plugin.json")

    icon_val = manifest.get("icon")
    if (
        not isinstance(icon_val, str)
        or not icon_val.startswith("./")
        or ".." in icon_val
        or "://" in icon_val
    ):
        raise ValueError(f".claude-plugin/plugin.json : 'icon' invalide ({icon_val!r})")
    icon_rel = icon_val[2:]
    if not icon_rel:
        raise ValueError(".claude-plugin/plugin.json : 'icon' vide")

    entrees: list[tuple[str, Path]] = []
    for rel in (*_REQUIRED_CLAUDE_FILES, icon_rel):
        chemin = src_dir / rel
        if not chemin.is_file():
            raise FileNotFoundError(f"Fichier requis introuvable : {chemin}")
        entrees.append((rel, chemin))

    agents_dir = src_dir / "agents"
    if not agents_dir.is_dir():
        raise FileNotFoundError(f"Répertoire requis manquant : {agents_dir}")
    for chemin in sorted(agents_dir.rglob("*")):
        if not chemin.is_file() or chemin.name.endswith(".pyc") or "__pycache__" in chemin.parts:
            continue
        entrees.append((chemin.relative_to(src_dir).as_posix(), chemin))

    skills_dir = src_dir / "skills"
    if not skills_dir.is_dir():
        raise FileNotFoundError(f"Répertoire requis manquant : {skills_dir}")
    for chemin in sorted(skills_dir.rglob("*")):
        if not chemin.is_file() or chemin.name.endswith(".pyc") or "__pycache__" in chemin.parts:
            continue
        rel_in_skills = chemin.relative_to(skills_dir)
        if len(rel_in_skills.parts) >= 2 and rel_in_skills.parts[1] == "scripts":
            continue
        entrees.append((chemin.relative_to(src_dir).as_posix(), chemin))

    entrees_triees = sorted(entrees, key=lambda item: item[0])
    return entrees_triees, manifest, icon_rel


def valider_bundle_claude(
    src_dir: Path,
    entrees: list[tuple[str, Path]],
    manifest: dict[str, object],
    icon_rel: str,
) -> None:
    if not (1 <= len(entrees) <= MAX_CLAUDE_FILES):
        raise ValueError(
            f"Nombre de fichiers invalide pour Claude Directory ({len(entrees)} > {MAX_CLAUDE_FILES})"
        )

    nom_plugin = manifest.get("name")
    if not isinstance(nom_plugin, str) or not _SKILL_NAME_RE.match(nom_plugin):
        raise ValueError(f".claude-plugin/plugin.json : 'name' invalide ({nom_plugin!r})")
    for req_str in ("displayName", "version", "license"):
        val = manifest.get(req_str)
        if not isinstance(val, str) or not val.strip():
            raise ValueError(f".claude-plugin/plugin.json : '{req_str}' requis et non vide")
    for req_url in ("privacyPolicyUrl", "termsOfServiceUrl"):
        val = manifest.get(req_url)
        if not isinstance(val, str) or not val.startswith("https://"):
            raise ValueError(f".claude-plugin/plugin.json : '{req_url}' doit être une URL HTTPS")
    for opt_url in ("documentationUrl", "supportUrl"):
        if opt_url in manifest:
            val = manifest.get(opt_url)
            if not isinstance(val, str) or not val.startswith("https://"):
                raise ValueError(f".claude-plugin/plugin.json : '{opt_url}' doit être une URL HTTPS")

    mcp_data = _charger_json_objet(src_dir / ".mcp.json", ".mcp.json")
    if set(mcp_data.keys()) != {"mcpServers"}:
        raise ValueError(
            f".mcp.json : clés racine inattendues ({sorted(set(mcp_data.keys()) - {'mcpServers'})})"
        )
    mcp_servers = mcp_data.get("mcpServers")
    if not isinstance(mcp_servers, dict) or not mcp_servers:
        raise ValueError(".mcp.json : 'mcpServers' doit être un objet JSON non vide")
    for srv_name, srv_cfg in mcp_servers.items():
        if not isinstance(srv_cfg, dict) or set(srv_cfg.keys()) != {"type", "url"}:
            raise ValueError(f".mcp.json : mcpServers.{srv_name} doit contenir uniquement 'type' et 'url'")
        if srv_cfg.get("type") != "http":
            raise ValueError(f".mcp.json : mcpServers.{srv_name}.type doit valoir 'http'")
        srv_url = srv_cfg.get("url")
        if not isinstance(srv_url, str) or not srv_url.startswith("https://"):
            raise ValueError(f".mcp.json : mcpServers.{srv_name}.url doit commencer par 'https://'")

    noms_set: set[str] = set()
    skill_dirs: set[str] = set()
    for rel_posix, chemin in entrees:
        if not rel_posix or rel_posix != rel_posix.strip():
            raise ValueError(f"Chemin d'entrée invalide : {rel_posix!r}")
        if "\\" in rel_posix or rel_posix.startswith("/"):
            raise ValueError(f"Chemin non POSIX ou absolu : {rel_posix}")
        segments = rel_posix.split("/")
        if any(seg in ("", ".", "..") for seg in segments):
            raise ValueError(f"Segment de chemin dangereux : {rel_posix}")
        if rel_posix == "plugin.json":
            raise ValueError("plugin.json racine interdit dans le paquet Claude Directory")
        if any(seg in _FORBIDDEN_NAMES for seg in segments) or segments[-1].lower() in _FORBIDDEN_LOWER_BASENAMES:
            raise ValueError(f"Fichier ou dossier exclu présent dans le paquet : {rel_posix}")
        if rel_posix.endswith(".py"):
            raise ValueError(f"Fichier Python interdit dans le paquet Claude Directory : {rel_posix}")
        if not (
            rel_posix.endswith(".md")
            or rel_posix.endswith(".json")
            or rel_posix in ("LICENSE", "NOTICE", icon_rel)
        ):
            raise ValueError(f"Type de fichier non autorisé : {rel_posix}")

        raw = chemin.read_bytes()
        if len(raw) > MAX_CLAUDE_FILE_BYTES:
            raise ValueError(f"{rel_posix} dépasse {MAX_CLAUDE_FILE_BYTES} octets ({len(raw)})")
        if raw.startswith(b"\xef\xbb\xbf"):
            raise ValueError(f"{rel_posix} contient un BOM UTF-8 interdit")
        if b"\x00" in raw:
            raise ValueError(f"{rel_posix} contient un octet NUL interdit")
        if b"\r" in raw:
            raise ValueError(f"{rel_posix} contient CR (fins de ligne LF requises)")
        if raw.startswith(b"#!"):
            raise ValueError(f"{rel_posix} commence par '#!' interdit")
        try:
            raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError(f"{rel_posix} n'est pas en UTF-8 valide") from exc

        if segments[0] == "skills":
            if len(segments) < 2:
                raise ValueError(f"Entrée skills/ invalide : {rel_posix}")
            skill_dirs.add(segments[1])
        elif segments[0] == "agents":
            if len(segments) != 2 or not segments[1].endswith(".md"):
                raise ValueError(f"Entrée agents/ invalide : {rel_posix}")
            agent_id = f"{nom_plugin}:{segments[1][:-3]}"
            if len(agent_id) > MAX_SKILL_IDENTITY_LEN:
                raise ValueError(
                    f"Identifiant persona trop long ({len(agent_id)} > {MAX_SKILL_IDENTITY_LEN}) : {agent_id}"
                )

        if rel_posix in noms_set:
            raise ValueError(f"Entrée en double : {rel_posix}")
        noms_set.add(rel_posix)

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


def synchroniser_vers_dossier(dst_dir: Path, entrees: list[tuple[str, Path]]) -> tuple[int, int]:
    dst_dir.mkdir(parents=True, exist_ok=True)
    ecrit = 0
    retires = 0
    attendus = {rel for rel, _ in entrees}

    for rel_posix, chemin in entrees:
        cible = dst_dir / rel_posix
        raw = chemin.read_bytes()
        if cible.is_file() and cible.read_bytes() == raw:
            continue
        cible.parent.mkdir(parents=True, exist_ok=True)
        tmp = cible.parent / f".{cible.name}.tmp"
        try:
            tmp.write_bytes(raw)
            os.replace(tmp, cible)
        except Exception:
            tmp.unlink(missing_ok=True)
            raise
        ecrit += 1

    for existant in sorted(dst_dir.rglob("*")):
        if not existant.is_file():
            continue
        rel = existant.relative_to(dst_dir).as_posix()
        if rel not in attendus:
            existant.unlink()
            retires += 1

    for dossier in sorted((p for p in dst_dir.rglob("*") if p.is_dir()), reverse=True):
        try:
            dossier.rmdir()
        except OSError:
            continue

    return ecrit, retires


def mettre_a_jour_branche(
    src_dir: Path, branch: str, version: str, entrees: list[tuple[str, Path]]
) -> tuple[bool, str]:
    repo_check = subprocess.run(
        ["git", "rev-parse", "--is-inside-work-tree"],
        cwd=src_dir,
        capture_output=True,
        text=True,
    )
    if repo_check.returncode != 0 or repo_check.stdout.strip() != "true":
        raise RuntimeError(f"Répertoire non suivi par Git : {src_dir}")

    with tempfile.TemporaryDirectory() as tmp:
        idx_path = Path(tmp) / "index"
        git_env = {**os.environ, "GIT_INDEX_FILE": str(idx_path)}
        index_lines: list[str] = []

        for rel_posix, chemin in entrees:
            hash_res = subprocess.run(
                ["git", "hash-object", "-w", "--stdin"],
                cwd=src_dir,
                input=chemin.read_bytes(),
                capture_output=True,
                check=True,
            )
            blob_sha = hash_res.stdout.decode("ascii").strip()
            index_lines.append(f"100644 blob {blob_sha}\t{rel_posix}\n")

        subprocess.run(
            ["git", "update-index", "--index-info"],
            cwd=src_dir,
            env=git_env,
            input="".join(index_lines).encode("utf-8"),
            capture_output=True,
            check=True,
        )
        tree_res = subprocess.run(
            ["git", "write-tree"],
            cwd=src_dir,
            env=git_env,
            capture_output=True,
            text=True,
            check=True,
        )
        tree_sha = tree_res.stdout.strip()

    ref_name = f"refs/heads/{branch}"
    rev_res = subprocess.run(
        ["git", "rev-parse", "--verify", "--quiet", ref_name],
        cwd=src_dir,
        capture_output=True,
        text=True,
    )
    parent_sha = rev_res.stdout.strip() if rev_res.returncode == 0 else ""

    if parent_sha:
        prev_tree = subprocess.run(
            ["git", "rev-parse", f"{parent_sha}^{{tree}}"],
            cwd=src_dir,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        if prev_tree == tree_sha:
            return False, parent_sha

    commit_cmd = ["git", "commit-tree", tree_sha]
    if parent_sha:
        commit_cmd.extend(["-p", parent_sha])
    commit_cmd.extend(["-m", f"chore({branch}): publish clean bundle v{version}"])
    commit_sha = subprocess.run(
        commit_cmd,
        cwd=src_dir,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()

    update_cmd = ["git", "update-ref", ref_name, commit_sha]
    if parent_sha:
        update_cmd.append(parent_sha)
    else:
        update_cmd.append("0" * 40)
    subprocess.run(update_cmd, cwd=src_dir, capture_output=True, text=True, check=True)
    return True, commit_sha


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--update-branch", action="store_true")
    parser.add_argument("--branch", default="claude-directory")
    args = parser.parse_args(argv)

    if args.update_branch and not args.apply:
        raise ValueError("--update-branch requiert --apply")

    branch = _valider_nom_branche(args.branch)
    entrees, manifest, icon_rel = collecter_fichiers_claude(SRC_DIR)
    valider_bundle_claude(SRC_DIR, entrees, manifest, icon_rel)
    version = str(manifest["version"])
    dst_dir = SRC_DIR / "dist" / "claude-directory"

    mode = "APPLY" if args.apply else "DRY-RUN"
    print(f"[*] Empaquetage Claude Directory ({mode}) : {len(entrees)} fichier(s) (v{version})")
    print(f"    Source : {SRC_DIR}")
    print(f"    Cible  : {dst_dir}")

    if not args.apply:
        print("[OK] Validation à sec réussie.")
        return 0

    ecrit, retires = synchroniser_vers_dossier(dst_dir, entrees)
    print(
        f"[OK] Dossier généré : {dst_dir} "
        f"({ecrit} écrit(s), {retires} retiré(s), {len(entrees)} au total)"
    )

    if args.update_branch:
        modifie, commit_sha = mettre_a_jour_branche(SRC_DIR, branch, version, entrees)
        etat = "mise à jour" if modifie else "déjà à jour"
        print(f"[OK] Branche locale '{branch}' {etat} : {commit_sha[:12]}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
