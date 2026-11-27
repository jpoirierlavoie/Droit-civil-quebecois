# Demande introductive d'instance et avis d'assignation (ordinaire et régime simplifié C.Q.)

À charger **avec `references/fondamentaux-actes.md`**. Encadre la demande introductive en instance ordinaire et sa variante sous le régime simplifié de la Cour du Québec (`535.1 s. C.p.c.`), ainsi que l'avis d'assignation ministériel (`145–146, 490 C.p.c.`).

## Vecteur législatif

* `law="cpc"` : `numbers=["33", "35", "41", "42", "43", "99", "100", "141", "142", "145", "146", "148", "180", "229", "490", "535.1", "535.2", "535.3", "535.4", "535.5", "535.6", "535.7", "535.8", "535.9", "535.15"]`
* Règlements et directives : `c-25.01-r.0.2.1` (C.S.), `c-25.01-r.9` (C.Q.), modèle d'avis d'assignation établi par le ministre de la Justice (`146 al. 1 C.p.c.`), `t-16-r.10` (droits de greffe), plus directives C.S./C.Q. Vague 1 (`fonction='directive'`, `fr`-only : `qccs-dist-mtl` `preseance-sur` `qccs-div-mtl`, `qccs-div-qc`, `qccq-regles-simplifiees`, `qccq-mtl-prat-civile`, `qccq-mtl-prat-admin`).

## Conditions et préalables

1. Vérifier la prescription (`2892 C.c.Q.` : signification requise dans les 60 jours suivant l'expiration si dépôt proche de la limite) et tout avis préalable de déchéance (renvoi à `recherche-juridique` / `grille-prealables`).
2. Vérifier le seuil de compétence (`33`, `35 C.p.c.`) : sous le plafond indexé de la Cour du Québec (`< 100 000 $` `[À VÉRIFIER À LA G.O.Q. — SEUIL INDEXÉ]`, l'indexation prévue à `35 al. 4` paraissant à la *Gazette officielle* avant de toucher le texte consolidé de `lois`), le **régime simplifié particulier (`535.1–535.15`)** s'applique de plein droit (attention : seuils distincts sous **`< 50 000 $`** `[À VÉRIFIER VIA LOIS]` pour l'interdiction d'interrogatoire oral préalable sous `229 al. 1` / `535.9` et pour l'**expertise commune obligatoire de `535.15 C.p.c.`**).
3. Confirmer l'exactitude des personnes morales (`outils.registre_search` / `registre_get_entity`, y compris `lei` et les liens `portails_officiels` `req`, `corporations_canada`, `isc_pisc`) et adresses ou lots indicatifs (`outils.adresse_verify` avec `lot_source` et `ambiguites_cadastrales` — consulter le Registre foncier pour toute action réelle immobilière), en rappelant de valider au REQ avant signification (incluant la vérification du *fondé de pouvoir* exigé par la *Loi sur la publicité légale des entreprises* `art. 26–28` lorsqu'une personne morale n'a ni domicile ni établissement au Québec).

## Forum et compétence

* Distinguer `41` (domicile du défendeur; clause d'élection nulle en contrat d'adhésion) et `42` (fors additionnels : lieu du contrat, fait générateur/préjudice, immeuble).
* Vérifier la compétence exclusive (`< 75 000 $`) vs concurrente (`75 000 $` à `< 100 000 $` `[À VÉRIFIER À LA G.O.Q. — SEUIL INDEXÉ]`) de la Cour du Québec (`35 C.p.c.`).

## Structure obligatoire

* **Instance ordinaire (`141 s.`) :** Cartouche + Désignation des parties + Titre `(Articles 141 et suivants du Code de procédure civile)` + `LES PARTIES` + `LES FAITS` + caractérisation + `LES DOMMAGES` + `LA COMPÉTENCE DU TRIBUNAL` + `POUR CES MOTIFS, PLAISE AU TRIBUNAL :` + signature/coordonnées `[À COMPLÉTER]`.
* **Variante régime simplifié C.Q. (`535.1–535.15`) :**
  * **Aucun protocole de l'instance (`535.2`)**;
  * **Plafond strict de `5 pages` maximum (`535.3`)** : rédaction resserrée (avertir expressément qu'un texte non paginé exige vérification du nombre de pages final dans Word ou via `production-et-conformite` / `controler_document.py`, ou inscription explicite de ce contrôle au bon de travail manuel si les scripts locaux ne peuvent pas s'exécuter).

## Pièces jointes et formalités

* **Avis d'assignation (`145–146, 490 C.p.c.`, modèle établi par le ministre de la Justice) :** Annexé obligatoirement à **toutes** les demandes introductives d'instance (Cour supérieure comme Cour du Québec). Doit énoncer côte à côte :
  1. Le délai de réponse de **`15 jours`** suivant la signification **et** celui de **`30 jours`** lorsque le défendeur n'a ni domicile, ni résidence, ni établissement au Québec dans un litige comportant un élément d'extranéité (`490 C.p.c.`);
  2. L'avertissement de jugement par défaut possible sans autre avis avec frais de justice (noter le préavis d'au moins `1 mois` contre le procureur général, `180 al. 1`);
  3. Les options du défendeur : régler, ou contester en déposant une réponse et en collaborant au protocole (`148`, en `45 jours` ou `3 mois` si `490`) — ou, en **régime simplifié C.Q. (`535.1 s.`)**, sans protocole (`15 j` réponse `145`, `20 j` pièces et avis du demandeur `535.4`, `45 j` moyens préliminaires/intervention `535.5`, `95 j` exposé sommaire et avis du défendeur `535.6` et `110 j` conférence de gestion `535.8`);
  4. Le renvoi territorial (`43`, `146 al. 4`) et le transfert aux petites créances (`146 al. 5`);
  5. L'**indication des pièces** au soutien (`145 al. 1`), le district/greffe, les coordonnées complètes du procureur (incluant courriel de notification) et le renvoi à l'aide juridique / Centres de justice de proximité.
* **En sus devant la Cour du Québec, Chambre civile (`535.1–535.8 C.p.c.`) :** Annexer **en sus** de l'Avis d'assignation l'*Avis requis par le Code de procédure civile* énonçant les règles et délais particuliers du régime simplifié (`15 j` réponse sous `145` ou `30 j` sous `490` ; `20 j` communication des pièces et avis du **demandeur** sous `535.4` ; `45 j` moyens préliminaires / appel en garantie sous `535.5` ; `95 j` exposé sommaire et avis du défendeur sous `535.6` et du tiers sous `535.7` — `45 j` si notifié `> 50 j` après l'acte ; `110 j` conférence de gestion `535.8`). Aux échéances `535.4`, `535.6` et `535.7`, chaque partie dépose le formulaire obligatoire **`SJ-1273`** (*Avis requis par les articles 535.4, 535.6 et 535.7 C.p.c.*, directive `qccq-regles-simplifiees` par. 4 ; case `CHEM*CON` réservée au greffier).
* **Bordereau et endos :** Dresser selon les gabarits de `production-et-conformite` (`cahier-des-pieces-et-bordereaux.md` et `controle-endos-depot-signification.md`).

## Particularités et pièges

* **Zéro « requête introductive d'instance » ni « assignation » seule (terme français)** : le titre est `DEMANDE INTRODUCTIVE D'INSTANCE` et l'acte joint est l'`AVIS D'ASSIGNATION` ; vérifier l'orthographe exacte du tribunal (`COUR DU QUÉBEC`, jamais `COUR DE QUÉBEC` ; `Chambre civile`, jamais `Chambre civil`).
* **Zéro article ni jurisprudence dans le récit des faits** (`fondamentaux-actes.md`), sauf énoncé bref du fondement juridique ou du régime applicable sans plaidoirie.
* **Omission du `30 jours` hors Québec (`490 C.p.c.`) et du fondé de pouvoir :** Dans l'avis d'assignation à une partie résidant ou située hors Québec, mentionner le délai prolongé (`30 jours` pour répondre / `3 mois` pour faire valoir les exceptions selon `490–491 C.p.c.`) et prévoir l'adresse de signification au fondé de pouvoir au Québec (`LPLE`) ou la notification internationale applicable.
* **Acte modifié (`art. 206 C.p.c.`, `c-25.01-r.0.2.1 art. 11`) :** Toute modification à une demande introductive exige la mise en évidence des ajouts (soulignement — et gras au besoin pour lisibilité — ou trait vertical en marge) et la marque `(…)` aux passages retranchés, avec gel des cotes retirées.
* **Client initialement non représenté ou mandat de rédaction ponctuelle :** Lorsqu'un projet est préparé pour une partie qui signe elle-même sans représentation au dossier, adapter le bloc signature, retirer la mention de procureur au dossier et baliser les limites de l'assistance juridique.

## Conclusions types

* `ACCUEILLIR la présente demande introductive d'instance ;`
* `CONDAMNER [la Défenderesse] à payer [au Demandeur] la somme de [montant] $, avec intérêts au taux légal et l'indemnité additionnelle prévue à l'article 1619 du Code civil du Québec [ou au taux contractuel convenu] à compter du [date de la mise en demeure / de la demande] ;` *(utiliser `outils.interets_1619`, y compris `mode="prime_plus_margin"`, et convertir toute créance en devise étrangère en CAD selon art. 12 Loi sur la monnaie / `1561, 3161 C.c.Q.` via `outils.taux_boc_rates`)*
* *(Si justifié et allégué)* `ORDONNER l'exécution provisoire du jugement à intervenir nonobstant appel ;` (`661 C.p.c.`)
* `LE TOUT avec les frais de justice.`

## Délais (renvoi)

Articles à vérifier et chiffrer via `gestion-du-mandat` (`conformite-echeanciers-cpc.md` et `outils.calendrier_deadlines`) : `107 al. 3` (signification / péremption), `145` / `490` (réponse), `149 al. 2` (protocole), `173` (mise en état de rigueur), `535.4` / `535.6` (régime simplifié C.Q.).
