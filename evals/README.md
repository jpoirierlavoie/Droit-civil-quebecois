# Suite d'évaluation comportementale (`evals/`)

Suite de régression de **Droit civil québécois (`v3.5.0`)** couvrant les **10 compétences** (5 orchestrateurs de phase + 5 compétences de service), les **60 feuilles de référence** (incluant `produit-contre-epreuve-banc.md`), les **6 personas sans contexte** (`agents/*.md`), les **4 scripts locaux** (`calcul_delai.py`, `inspecter_piece.py` avec `--extraire-texte`, `controler_document.py`, `verifier_cotes.py`), la quarantaine par domaine et le corpus élargi Vagues 1–3 (`134` textes, `50` matières), le protocole OAuth 2.1 / BYOK CanLII (`acces.poirierlavoie.ca`), la dégradation gracieuse nuage, les portes bloquantes de phase, l'honnêteté perceptuelle, les précédents internes dé-identifiés et les **10 déclencheurs négatifs hors champ** (`122` scénarios au total).

## Fichiers

- `evals/scenarios.json` — scénarios de référence (`feuilles_attendues`, `enchainement_attendu`, `declencheur_negatif`), critères d'évaluation et assertions déterministes d'outillage.
- `evals/executer_evals.py` — utilitaire autonome en bibliothèque standard Python pour lister les scénarios, valider les 4 utilitaires locaux, exécuter les tests du vérificateur et noter des réponses produites hors ligne.
- `evals/test_verifier.py` — tests unitaires sur fixtures des invariants v3 de `verifier.py`.

## Commandes

```powershell
python evals/executer_evals.py --liste
python evals/executer_evals.py --auto-test
python -m unittest evals/test_verifier.py -v
python evals/executer_evals.py --reponses chemin/vers/reponses.json
```

L'exécution `--auto-test` est sans effet secondaire (répertoire temporaire détruit aussitôt) et est vérifiée par l'intégration continue après `python verifier.py`.
