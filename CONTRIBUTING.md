# Contribuer à `droit-civil-quebecois` / Contributing

Les contributions de juristes, de développeurs et de chercheuses/chercheurs du Québec sont les bienvenues (sous licence [`Apache-2.0`](LICENSE) et [`NOTICE`](NOTICE)).

> **In English:** Contributions from Québec legal practitioners and developers are welcome under [`Apache-2.0`](LICENSE). Read the strict privilege rule below before opening an issue or pull request.

---

## 1. Confidentialité et secret professionnel (règle absolue) / Confidentiality & Privilege

**Ne jamais soumettre** de noms de clients, numéros de dossier réels, faits confidentiels ou protégés par le secret professionnel, pièces non anonymisées, chemins locaux personnels ni jetons/clés API (`MCP_*`, `Bearer`, clé CanLII) dans une issue, une *pull request*, un commit ou `evals/scenarios.json`.

- Tout exemple ou scénario d'évaluation doit être **entièrement synthétique**.
- Toute vulnérabilité de sécurité ou fuite potentielle doit être signalée en privé selon [`SECURITY.md`](SECURITY.md) — jamais en issue publique.

---

## 2. Contribuer au contenu juridique / Contributing Legal Content

Les 10 compétences et 60 feuilles de référence du dépôt passent intégralement le contrôle de publication `python verifier.py --release` (`0` marqueur `[FICHE À RÉDIGER]` ou `[NON VALIDÉ PAR LA PRATIQUE]`). Les marqueurs `[FICHE À RÉDIGER]` et `[NON VALIDÉ PAR LA PRATIQUE]` demeurent pris en charge sur une branche de travail en cours, mais doivent être levés avant fusion vers `main`. Pour bonifier une fiche existante ou proposer une nouvelle feuille :

1. Respecter les titres `##` exigés pour la famille de la fiche (`acte-`, `arg-`, `corr-`, `contrat-`, `preuve-`, `piece-`, `produit-`, `recherche-`, `controle-`, `cahier-`, `conformite-` — gabarits détaillés dans [`AGENTS.md`](AGENTS.md)).
2. Privilégier les **vecteurs de recherche** (`lois.get_articles`, paires confondables, silences) plutôt que de copier le texte intégral des lois dans le dépôt.
3. Ajouter ou mettre à jour au moins **2 scénarios synthétiques** dans [`evals/scenarios.json`](evals/scenarios.json) pour toute nouvelle fiche afin de préserver la conformité `python verifier.py --release`.
4. Respecter strictement la séparation hors droit familial et droit criminel ainsi que l'étanchéité bijuridique (droit civil québécois uniquement).

---

## 3. Contrôles techniques avant PR / Pre-PR Verification

Prérequis : **Python `>= 3.10`** (bibliothèque standard uniquement). Avant toute soumission, exécuter ces contrôles depuis la racine du dépôt (encodage **UTF-8 sans BOM** et fins de ligne **LF** obligatoires sur tous les fichiers ; aucun fichier hors `ROOT_ALLOWLIST` / `EVALS_ALLOWLIST` dans [`verifier.py`](verifier.py)) :

```bash
# Linux / macOS
PYTHONUTF8=1 python3 verifier.py
PYTHONUTF8=1 python3 evals/executer_evals.py --auto-test
PYTHONUTF8=1 python3 verifier_tout.py --mode mock
PYTHONUTF8=1 python3 scripts/empaqueter_plugin_chatgpt.py
```

```powershell
# Windows PowerShell
$env:PYTHONUTF8 = "1"
python verifier.py
python evals/executer_evals.py --auto-test
python verifier_tout.py --mode mock
python scripts/empaqueter_plugin_chatgpt.py
```

Toute PR doit aussi renseigner l'évaluation d'impact à 4 axes demandée dans le gabarit de PR (et garder `AGENTS.md`, `CLAUDE.md` et `GEMINI.md` identiques octet pour octet et sous `24 000` octets).

---

## 4. Rôle des scripts (`scripts/`) et auto-hébergement (Forks)

| Script | Public cible | Rôle |
|---|---|---|
| [`scripts/empaqueter_plugin_chatgpt.py`](scripts/empaqueter_plugin_chatgpt.py) | Utilisateurs / CI | Valide et produit l'archive universelle `dist/droit-civil-quebecois-chatgpt-universal.zip` |
| [`scripts/synchroniser_plugin_gemini.py`](scripts/synchroniser_plugin_gemini.py) | Utilisateurs Antigravity | Copie le greffon vers `~/.gemini/config/plugins/droit-civil-quebecois` (en promouvant `.antigravity-plugin/plugin.json` à la racine) |
| [`scripts/regenerer_cache_mcp.py`](scripts/regenerer_cache_mcp.py) | Mainteneur uniquement | Reconstruit le cache local d'outils depuis les clones locaux de `MCP-Legislation`, `MCP-Jurisprudence` et `MCP-Outils` + Node.js (`npx tsx`) |

Si vous créez un *fork* pour pointer vers vos propres instances MCP, mettez à jour `EXPECTED_REPO_URL` et les URLs de serveurs dans [`verifier.py`](verifier.py), [`verifier_tout.py`](verifier_tout.py) et les manifestes (`.mcp.json`, `mcp_config.json`, `gemini-extension.json`, `.antigravity-plugin/plugin.json`, `plugin.json`, `.claude-plugin/*.json`, `.codex-plugin/plugin.json`).
