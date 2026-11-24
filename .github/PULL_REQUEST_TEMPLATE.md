## Résumé / Summary

<!-- Décrire brièvement l'objet de la PR / Briefly describe the purpose of this PR -->

## Vérifications locales / Local Verification

- [ ] `python verifier.py` (sortie strictement muette, code 0)
- [ ] `python evals/executer_evals.py --auto-test`
- [ ] `python verifier_tout.py --mode mock`
- [ ] `python scripts/empaqueter_plugin_chatgpt.py`
- [ ] Fins de ligne LF uniquement et encodage UTF-8 sans BOM sur tous les fichiers modifiés

## Évaluation d'impact obligatoire (4 axes — `AGENTS.md` / `CLAUDE.md` / `GEMINI.md`)

1. **Compétences (`skills/`), scripts et `evals/` :**
2. **`README.md`, `CONTRIBUTING.md`, `CHANGELOG.md`, `SECURITY.md`, licence et les 9 manifestes :**
3. **Page publique HTML (`GET /`) et `/mcp/server-card` (ce dépôt ou serveurs aval) :**
4. **Impacts inter-dépôts (`droit-civil-quebecois`, `MCP-Socle`, `MCP-Acces`, `MCP-Legislation`, `MCP-Jurisprudence`, `MCP-Outils`) :**

## Confidentialité et sécurité

- [ ] Aucun secret (`MCP_*`, `Bearer`, SHA/clé API), aucun chemin local personnel et aucune donnée client confidentielle ou privilégiée dans les commits ni dans cette PR.
