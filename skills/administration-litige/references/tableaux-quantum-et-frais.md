# Tableaux de quantum, intérêts (art. 1619 C.c.Q.) et état des frais

Produit des tableaux structurés (Markdown et export `.csv` UTF-8 avec BOM `utf-8-sig` compatible Excel `fr-CA`) pour les réclamations pécuniaires, intérêts légaux, tableaux *Scott* et mémoires de frais de justice.

## 1. Décompte des intérêts légaux et indemnité additionnelle (`art. 1617–1620 C.c.Q.`)

**Ne jamais calculer les intérêts à la main ni extrapoler un trimestre futur non publié.**
* Lire au besoin `lois.get_articles(law="ccq", numbers=["1617", "1618", "1619", "1620"])` et `law="cpc", numbers=["339", "340", "341", "342", "343", "344"]`.
* Exécuter obligatoirement `outils.interets_1619(end_date, tranches=[...], mode=...)` : calcule au jour exact (`Exact/Exact`, intérêt simple `1620 C.c.Q.`) l'intérêt légal (`5 %`) et l'indemnité additionnelle (`art. 28 L.A.F.`) sur une ou plusieurs tranches de capital datées (ex. mise en demeure, débours successifs, paiements partiels).
* **Piège du point de départ :** En matière contractuelle et extracontractuelle, distinguer la date de la demeure (`1594–1595`, `1617`) de la date du préjudice ou de l'assignation (`1618` en préjudice corporel/moral, ou date de la demande si aucune mise en demeure préalable). Signaler tout trimestre postérieur au dernier taux publié par Revenu Québec.

## 2. Tableaux de dommages et tableaux comparatifs (construction / commercial / Scott)

Structurer tout tableau de quantum de manière auditable pour l'adversaire et le juge :
* **Ventilation des dommages :** `| Poste / Chef de réclamation | Période / Date | Base contractuelle ou factuelle | Pièce(s) au soutien | Montant réclamé ($) | Point de départ intérêts | Notes / risque de preuve |`
* **Tableau de type *Scott* (défauts / vices de construction / réclamations multi-postes) :**
  `| # | Poste / Élément allégué | Pièce / Photo / Rapport | Position du Demandeur ($) | Position du Défendeur ($) | Écart ($) | Évaluation / Note au tribunal |`
* **Formatage Excel (`utf-8-sig`) :** Lorsque l'utilisateur demande un tableur ouvrable dans Excel, fournir un fichier `.csv` encodé en UTF-8 avec BOM (`utf-8-sig`, délimiteur `;` ou `,` indiqué) avec formules `=SOMME(...)` / `=SUM(...)` simples et colonnes de dates ISO (`AAAA-MM-JJ`).

## 3. État des frais de justice / Bill of Costs (`art. 339–344 C.p.c.` et `t-16-r.10`)

**Lire obligatoirement les textes courants via `lois` avant d'inscrire un seul montant tarifaire :**
* `lois.get_articles(law="cpc", numbers=["339", "340", "341", "342", "343", "344"])`
* `lois.get_structure(law="t-16-r.10")` puis `lois.get_articles(law="t-16-r.10", numbers=[...])` (*Tarif judiciaire en matière civile*, vérifier la date de consolidation et l'indexation annuelle des droits de greffe!).

* **Distinction essentielle (`339 C.p.c.`) :** Les **frais de justice** comprennent les droits et frais de greffe, les frais de signification/notification, les frais de sténographie/transcription, les indemnités des témoins, les honoraires et débours d'experts (soumis à la réserve de proportionnalité `339 al. 2`) et certains frais d'interprète ou de publicité — **jamais les honoraires extrajudiciaires de l'avocat** (sauf condamnation exceptionnelle pour abus de procédure sous `54 C.p.c.`).
* **Gabarit d'état des frais (`344 C.p.c.`) :**
  `| Poste | Date | Description & référence C.p.c. / t-16-r.10 | Pièce justificative (reçu / mémoire huissier) | Montant demandé ($) | Taxe / Remarque greffier |`
* **Délais de vérification et révision (`344`) :** Notifier l'état des frais à la partie qui les doit; **10 jours** pour notifier une opposition (sinon vérification par le greffier sans audience ou sur dossier), et **10 jours** de la décision du greffier pour demander la révision au tribunal (`344 al. 3` — renvoyer le calcul exact à `echeanciers-cpc.md`).
