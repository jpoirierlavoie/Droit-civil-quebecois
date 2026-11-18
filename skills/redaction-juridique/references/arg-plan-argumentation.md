# Plan d'argumentation (simple ou détaillé) en première instance

Rédige les plans d'argumentation remis au juge de première instance — où les citations juridiques vérifiées soutiennent les conclusions déjà présentes dans l'acte de procédure.

## Destinataire et format

Document remis au **juge** (jamais substituable à une conclusion absente de la procédure : une conclusion oubliée exige un amendement, pas une plaidoirie). Consulter les règlements de pratique via `lois` (`c-25.01-r.0.2.1` C.S., `c-25.01-r.0.2.2`/`r.0.2.3`, `c-25.01-r.9` C.Q.) pour les limites de pages et délais de remise.

Choisir le niveau de détail selon l'audience et le palier :
* **Plan simple (sommaire d'audience / gestion / incident court) :** Titres synthétiques, puces factuelles avec cotes exactes, textes et arrêts clés cités en un paragraphe chacun, conclusions reprises mot pour mot.
* **Plan détaillé (instruction au fond / contestation complexe / injonction) :** Rédaction structurée par question en litige avec syllogisme complet, application détaillée aux cotes/témoignages et réponses aux prétentions adverses.

## Structure

| Contexte | Structure type |
|---|---|
| **Défaut / Au fond après enquête** | `RÉSUMÉ` (1–2 par., thème et demande claire dès le 1er par.) → `CADRE JURIDIQUE` (ordre civiliste : texte → jurisprudence → doctrine) → `APPLICATION AUX FAITS` (avec cotes/témoignages exacts) → `CONCLUSIONS RECHERCHÉES` (**mot pour mot** de la procédure) |
| **Variante pratique — Plaidoirie orale / Procès** | `TRAME FACTUELLE` (chronologie sourcée par cotes et tableau comparatif `Date \| Version / Événement \| Cote` si versions concurrentes multi-parties) → `DROIT APPLICABLE` → `APPLICATION` → `CONCLUSIONS` *(formule exacte `POUR CES MOTIFS, PLAISE AU TRIBUNAL :`)* |
| **Moyen préliminaire (`166–168`)** | Moyen soulevé → critère et source → application (faits allégués tenus pour avérés sur irrecevabilité) → conclusions |
| **Demande / Opposition injonction interlocutoire (`509–511`)** | Qualité pour agir / absence de droit apparent (échelle : question sérieuse c. apparence claire pour injonction obligatoire ou finale en fait) → préjudice sérieux ou irréparable (c. indemnisation monétaire adéquate) → urgence (exclure urgence auto-créée / inaction prolongée) → balance des inconvénients → mesure de sauvegarde alternative ou dépôt en fidéicommis → conclusions |
| **En défense** | Résumé → admis vs contesté → cadre juridique → conclusions en rejet |

## Discipline de citation

Appliquer strictement les règles de `arg-citations.md` :
* *Manuel canadien de la référence juridique* (citation neutre + `[par. X]` majoritaire).
* **Présentation des extraits jurisprudentiels :** Placer les extraits cités en **blocs indentés et en italique** sous l'intitulé complet (ou titre abrégé uniforme avec renvoi *précité* après première occurrence), avec renvoi exact aux paragraphes (`par. X` / `par. X à Y`).
* **En anglais civiliste :** Distinguer `article` (`C.C.Q.`, `C.C.P.`) et `section` (`CQLR` / lois statutaires).
* Au Palier 3, **aucune proposition décisive** ne repose sur un arrêt non lu intégralement (`Résumée`, `Rapportée` ou `Lue (extrait)` seul); maintenir `[RATIO / PAR. X À INSÉRER APRÈS LECTURE DE <citation + lien CanLII>]` en attendant le texte intégral officiel.

## Pièges

* **Ce qui ne franchit jamais la porte du tribunal (ni l'endos / plan remis au juge) :** Aveu de faiblesse formulé comme tel (« notre point faible est… » → reformuler : « la partie adverse soutiendra que…, mais… »), notes de préparation interne ou directives d'audience (`[NOTE INTERNE]`, aide-mémoire personnel à l'avocat), risque de recouvrement, objectifs secrets du client, plancher de règlement, provision/honoraires, évaluation interne d'un témoin.
* **Confidentialité (`108 C.p.c.`) et anonymisation cohérente :** Lorsque le tribunal ou une loi ordonne la non-identification d'une personne (ex. TAQ, dossier confidentiel), appliquer exactement les mêmes initiales (ex. `A. B.`) dans le corps, les tableaux comparatifs et l'endos, sans jamais réintroduire le nom complet dans une entête ou un tableau.
* **Conclusions nouvelles en plaidoirie :** Jamais demander une condamnation absente des conclusions de la procédure sans demande de modification préalable (`206 C.p.c.`).

## Contrôle

1. Correspondance 1:1 entre les autorités du plan et l'index du cahier des sources (`production-et-conformite` / `cahier-des-sources.md`).
2. Continuité stricte de numérotation (aucun doublon `8., 8.` ni saut), concordance titre/tribunal/date avec l'acte de procédure, formule exacte `POUR CES MOTIFS, PLAISE AU TRIBUNAL :` s'il comporte des conclusions, et unilinguisme strict (zéro bascule FR/EN en milieu de document ni discordance corps/endos).
3. Zéro citation décisive sous `Lue (intégrale) [par. X]` au Palier 3 sans marqueur `[RATIO / PAR. X ...]`.
4. Zéro copie des blocs F (faiblesses) ou H (plancher de règlement) de la théorie de la cause.
5. Contrôle `outils.terminologie_scan` exécuté avant remise.
