# Tableaux de quantum, intérêts (art. 1619 C.c.Q.) et état des frais

Produit des tableaux structurés (Markdown et export `.csv` UTF-8 avec BOM `utf-8-sig` compatible Excel `fr-CA`) pour les réclamations pécuniaires, intérêts légaux, tableaux *Scott* et mémoires de frais de justice.

## Déclencheurs

* Calcul d'intérêts légaux (`5 %`) et d'indemnité additionnelle (`art. 1619 C.c.Q.`);
* Préparation d'un tableau comparatif de dommages ou d'un tableau *Scott* (construction / commercial);
* Confection, vérification ou contestation d'un état des frais de justice après jugement (`339–344 C.p.c.`, `t-16-r.10`).

## Vecteur

* `law="ccq"` : `numbers=["1617", "1618", "1619", "1620"]`
* `law="cpc"` : `numbers=["54", "339", "340", "341", "342", "343", "344"]`
* `law="t-16-r.10"` (*Tarif judiciaire en matière civile*, texte plat sans divisions) : appeler directement `lois.get_articles(law="t-16-r.10", from="1", to="25")` (éviter `get_structure` qui est vide) en relevant la **date de consolidation** et l'indexation annuelle des droits de greffe!

## Obligations

### 1. Décompte des intérêts légaux et indemnité additionnelle (`art. 1617–1620 C.c.Q.`)
**Ne jamais calculer les intérêts à la main ni extrapoler un trimestre futur non publié.**
* Exécuter obligatoirement `outils.interets_1619(end_date, tranches=[...], mode=...)` : calcule au jour exact (`Exact/Exact`, intérêt simple `1620 C.c.Q.`) l'intérêt légal (`5 %`) et l'indemnité additionnelle (`art. 28 L.A.F.`) sur une ou plusieurs tranches de capital datées (ex. mise en demeure, débours successifs, paiements partiels).
* **Usage strictement restreint de `rate_overrides` :** `rate_overrides` est **interdit** sur tout trimestre déjà publié dans la table embarquée du serveur (l'outil rejette l'appel). Il ne sert qu'à injecter un taux art. 28 L.A.F. nouvellement publié par Revenu Québec / *Gazette officielle du Québec* pour un trimestre postérieur à `laf_table_last_quarter` avant la mise à jour du connecteur, et exige alors une vérification humaine sur la source officielle.

### 2. Tableaux de dommages et tableaux comparatifs (construction / commercial / *Scott*)
* **Ventilation des dommages :** `| Poste / Chef de réclamation | Période / Date | Base contractuelle ou factuelle | Pièce(s) au soutien | Montant réclamé ($) | Point de départ intérêts | Notes / risque de preuve |`
* **Tableau de type *Scott* :** `| # | Poste / Élément allégué | Pièce / Photo / Rapport | Position du Demandeur ($) | Position du Défendeur ($) | Écart ($) | Évaluation / Note au tribunal |`
* **Formatage Excel (`utf-8-sig`) :** Fournir un fichier `.csv` encodé en UTF-8 avec BOM (`utf-8-sig`, délimiteur `;` ou `,` indiqué) avec formules `=SOMME(...)` / `=SUM(...)` simples et colonnes de dates ISO (`AAAA-MM-JJ`).

### 3. État des frais de justice / *Bill of Costs* (`art. 339–344 C.p.c.` et `t-16-r.10`)
* **Gabarit d'état des frais (`344 C.p.c.`) :** `| Poste | Date | Description & référence C.p.c. / t-16-r.10 | Pièce justificative (reçu / mémoire huissier) | Montant demandé ($) | Taxe / Remarque greffier |`
* **Délais de vérification et révision (`344`) :** Notifier l'état des frais à la partie qui les doit; **`10 jours`** pour notifier une opposition (sinon vérification par le greffier sans audience ou sur dossier), et **`10 jours`** de la décision du greffier pour demander la révision au tribunal (`344 al. 3` — calcul exact via `conformite-echeanciers-cpc.md` / `outils.calendrier_deadlines`).

## Silences et paires confondables

* **Frais de justice (`339`) vs honoraires extrajudiciaires :** Les frais de justice comprennent droits/frais de greffe, signification/notification, sténographie/transcription, indemnités des témoins, honoraires/débours d'experts (soumis à proportionnalité `339 al. 2`) et certains frais d'interprète/publicité — **jamais les honoraires extrajudiciaires de l'avocat** (sauf condamnation exceptionnelle pour abus de procédure sous `54 C.p.c.`).
* **Point de départ `1617` vs `1618 C.c.Q.` :** Distinguer la date de la demeure (`1594–1595`, `1617`, ou assignation si aucune mise en demeure préalable) de la date du préjudice ou de l'assignation (`1618` en préjudice corporel ou moral).
* **Trimestres futurs :** Signaler tout trimestre postérieur au dernier taux publié par Revenu Québec sans jamais l'extrapoler.
