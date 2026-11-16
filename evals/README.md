# Suite d'évaluation comportementale (`evals/`)

Dix-neuf scénarios de régression couvrant les cinq compétences de **Droit civil québécois** (`v2.0.1`) et leurs paliers de rigueur : recherche législative/jurisprudentielle et statut de lecture, analyse stratégique et probante (commentaires Word cachés, caviardage Loi 25, interrogatoires), rédaction judiciaire complète vs mode bloc pour gabarit et cahier des sources, administration du litige (délais C.p.c., concordance, endos, état des frais) et déontologie/pratique (feuilles de temps, art. 110, fidéicommis).

## Fichiers

- `evals/scenarios.json` — les dix-neuf scénarios de référence, critères d'évaluation et assertions déterministes d'outillage.
- `evals/executer_evals.py` — utilitaire autonome en bibliothèque standard Python pour lister les scénarios, valider les utilitaires locaux et noter des réponses produites hors ligne.

## Commandes

```powershell
python evals/executer_evals.py --liste
python evals/executer_evals.py --auto-test
python evals/executer_evals.py --reponses chemin/vers/reponses.json
```

L'exécution `--auto-test` est sans effet secondaire (répertoire temporaire détruit aussitôt) et est vérifiée par l'intégration continue après `python verifier.py`.
