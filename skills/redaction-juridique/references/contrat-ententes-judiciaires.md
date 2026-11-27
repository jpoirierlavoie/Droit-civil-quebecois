# Formulaires de mise en état et de fixation d'audience (`173–174 C.p.c.`, `SJ-1100`, `SJ-1276`) et ententes accessoires

Encadre la préparation des **formulaires officiels prescrits pour la mise en état et la fixation d'une audience ou d'un procès** en Cour supérieure et en Cour du Québec — **sans jamais confectionner d'acte de mise en état à la main** —, ainsi que les seules conventions opérationnelles accessoires à l'instruction (confidentialité documentaire et instructions conjointes à l'expert commun).

## Objet et destinataire

* **Principe impératif :** Les déclarations communes de mise en état, les admissions de pièces/faits pour l'instruction et la fixation d'une audience reposent **exclusivement sur les formulaires obligatoires des tribunaux** :
  1. **Cour supérieure — Procès au fond (`173–174 C.p.c.`) :** *Demande d'inscription pour instruction et jugement par déclaration commune – matière civile* ;
  2. **Cour du Québec (Chambre civile) — Procès au fond :** formulaire obligatoire **`SJ-1100`** (*Demande d'inscription pour instruction et jugement (par déclaration commune ou d'une partie)*, `174 C.p.c.`) en instance ordinaire, ou formulaire obligatoire **`SJ-1276`** (*Formulaire de mise en état du dossier*, `535.13 C.p.c.`, directive `qccq-regles-simplifiees` par. 7) en règles simplifiées ;
  3. **Cour supérieure — Audience contestée / interlocutoire ou mise au rôle (`qccs-div-mtl` par. 53, 146, Annexe Division 4) :** *Déclaration commune pour fixation d'une audience* (*Sans enquête* ou *Avec enquête*).
* **Conventions purement accessoires :** Seules une **entente privée de confidentialité documentaire** (en appui d'un interrogatoire ou d'une communication de pièces) ou une **lettre d'instructions conjointes à l'expert commun** (`232–233, 535.15 C.p.c.`) se rédigent hors formulaire comme accessoires de l'instruction. Pour tout règlement mettant fin au litige (`2631 C.c.Q.`, `213, 217–220, 527–528 C.p.c.`), consulter `contrat-transaction-quittance.md`.
* **Destinataires :** Greffe et juge coordonnateur / greffier spécial du tribunal saisi (`outils.greffe_parse_number`), procureurs au dossier et parties (vérifier dénomination et `NEQ`/`LEI` via `outils.registre_search`/`registre_get_entity` et confirmer au REQ avant tout engagement corporatif).

## Mentions obligatoires

Charger `lois.get_articles(law="cpc", numbers=["12", "108", "173", "174", "224", "227", "232", "233", "235", "239", "240", "248", "292", "293", "294", "535.13", "535.15"])`, `lois.get_articles(law="c-25.01-r.0.2.1", numbers=["17"])` et, en C.Q. simplifiée, `lois.get_articles(law="qccq-regles-simplifiees", numbers=["7"])` :
* **Inscription au fond C.S. (*Déclaration commune – matière civile*, `173–174 C.p.c.`) :**
  * Initiative de l'ensemble des parties ou d'une seule partie (avec notification ouvrant un délai de **`15 jours`** aux autres parties pour indiquer ce qui doit être ajouté ou retranché sous peine de confirmation présumée, `174 al. 2 C.p.c.`) ;
  * Coordonnées complètes des parties et avocats responsables ; nature et valeur du litige (demande principale, demande reconventionnelle, interventions) ; **questions en litige obligatoirement communes** (+ questions supplémentaires proposées par une partie) ; **liste des faits admis (`174(4°)`)** et **liste des points à trancher par expertise (`174(5°)`)** ;
  * Attestations par partie : inventaire complet et à jour des pièces communiquées joint (`248 al. 1`), déclarations écrites produites (`292`), **seules pièces adverses dont l'authenticité est contestée** c. **pièces adverses dont le contenu est admis**, transcriptions d'interrogatoires invoquées (`224, 227`), rapports d'expertise invoqués (`239 al. 2, 293` : nom, date, domaine, cote) ;
  * Tableau des témoins par partie (`Fr./Angl.`, `Ord./Exp.`, durée interro., durée totale c.-interro., durée totale témoin), durée d'argumentation par partie, **durée totale de l'instruction (`1 jour = 5 heures`)**, services d'interprète ou moyens technologiques requis. *(En division de Montréal, `qccs-div-mtl` par. 146 : le dossier inscrit n'est porté au rôle au fond qu'à la réception de la Déclaration commune pour fixation d'une audience.)*
* **Inscription et mise en état C.Q. (**`SJ-1100`** sous `174 C.p.c.` ; **`SJ-1276`** sous `535.13 C.p.c.`) :**
  * Dans **`SJ-1100`** : motifs expliquant pourquoi la demande n'est pas commune le cas échéant (`174 in fine`, `15 jours`) et paiement des droits de greffe ; **Section 3.1 (grille tripartite des pièces dénoncées)** distinguant pour chaque cote : *(1) Admission : origine, intégrité et contenu*, *(2) Admission : origine et intégrité seulement (contenu nié)*, *(3) Aucune admission : témoin nécessaire pour le dépôt* ; **Section 4.1** témoins ordinaires (`1 jour = 5 heures`, et motifs justifiant de taire l'identité d'un témoin tout en prévoyant sa durée, `174(3°)`) ; **Section 4.2** preuve d'expert (commun c. partie, **admission de la qualification `Oui / Non` + motifs**, anticipation d'un interrogatoire de précision `293–294` ou d'un contre-interrogatoire `294`) ; **Section 4.4** frais d'interprète et autorisation/coordination/connexion Internet des moyens technologiques **à la charge de la partie qui les requiert**.
  * En règles simplifiées C.Q. (`< 100 000 $`) : remplir obligatoirement le formulaire de mise en état **`SJ-1276`** (`qccq-regles-simplifiees` par. 7).
* **Fixation d'audience C.S. (*Déclaration commune pour fixation d'une audience*, `qccs-div-mtl` par. 53, 146, Annexe Division 4) :**
  * Cocher **`Sans enquête`** (remplir la **1re partie** seulement) ou **`Avec enquête`** (**1re et 2e parties**) :
    * *Première partie* : nature de la demande à fixer, **numéro de séquence au plumitif**, montant en litige, **temps de lecture pour le juge**, durée totale de la preuve testimoniale si enquête, durée d'argumentation par partie, durée totale (`1 jour = 5 heures`) et déclaration d'engagement *« prêt(e) à procéder sur la foi des représentations décrites aux présentes »* ;
    * *Deuxième partie (Audience avec enquête)* : *6. Admissions*, *7. Pièces communiquées* (éviter toute duplication de pièces entre parties ; case `OUI / NON` d'**admission de l'authenticité pour production sans témoignage** — origine et intégrité sans véracité du contenu), *8. Expertises pertinentes* (**conciliation des opinions `240 C.p.c.` `OUI / NON` + résultat** et attestation de communication du **CV, compte d'honoraires à jour et tarif actuel pour l'audience au fond** selon l'art. **`17 R.C.s.Q.m.c.`**), *9. Liste des témoins* (ordinaires et experts), *10. Déclarations écrites `292 C.p.c.`* (avec case *Présence requise*).
* **Accessoires hors formulaire (uniquement si requis par l'instruction) :**
  * *Entente privée de confidentialité documentaire* : pièces visées, usage restreint à l'instance, destinataires autorisés, retour/destruction en fin de dossier, **préavis avant dépôt au greffe** afin de permettre une demande selon `12 C.p.c.`, et réserve de `108 C.p.c.` ;
  * *Instructions conjointes à l'expert commun (`232–233`, `535.15` obligatoire sous `< 50 000 $` en C.Q. simplifiée sauf autorisation)* : questions précises, pièces accessibles, échéancier, plafond/partage des honoraires (rappelant qu'à défaut de dépôt au greffe exigé par l'expert sous `233 al. 2`, **toutes les parties demeurent tenues solidairement**), déclaration ministérielle `235 al. 3` jointe au rapport et **interdiction de toute communication *ex parte*** avec l'expert commun.

## Structure

1. **Sélectionner le formulaire officiel exact** selon le tribunal (`C.S.` ou `C.Q.`), le régime (ordinaire ou simplifié `535.1`) et l'étape (inscription au fond `174` / `SJ-1100` / `SJ-1276` c. fixation d'audience `Sans enquête` ou `Avec enquête`), en excluant tout formulaire de matière familiale.
2. **Restituer le contenu rubrique par rubrique** dans l'ordre exact des tableaux et cases à cocher du formulaire officiel, avec calculs d'heures cohérents sur la base **`1 jour = 5 heures`** et cotes exactes (`P-`, `D-`) vérifiées.
3. **Annexer séparément**, uniquement s'il y a lieu, le projet sobre d'entente accessoire de confidentialité documentaire ou de lettre conjointe d'instructions à l'expert commun (rédigé au présent de l'indicatif civiliste).

## Clauses ou formules à proscrire

* **Confectionner à la main un « acte d'admissions », un « contrat de mise en état » ou une demande d'inscription libre** au lieu de remplir le formulaire officiel de la Cour supérieure ou de la Cour du Québec (`SJ-1100`, `SJ-1276`, *Déclaration commune*).
* **Confondre admission d'authenticité et admission de véracité du contenu** dans les tableaux de pièces (`SJ-1100` section 3.1 ; *Fixation d'audience* section 7 ; *Déclaration commune C.S.*).
* **Croire qu'une entente privée de confidentialité lie le tribunal ou scelle le dossier public (`12 C.p.c.`)** : seule une ordonnance judiciaire rendue sous `12 C.p.c.` restreint la publicité du dossier de cour.
* **Omettre le CV, le compte d'honoraires à jour et le tarif d'audience de l'expert (`art. 17 R.C.s.Q.m.c.`)** ou communiquer unilatéralement (*ex parte*) avec un expert commun.

## Contrôle

1. Vérifier via `lois` les exigences de `173–174, 240, 248, 292–294, 535.13, 535.15 C.p.c.`, `art. 17 R.C.s.Q.m.c.` (`c-25.01-r.0.2.1`) et des directives applicables (`qccs-div-mtl`, `qccs-dist-mtl`, `qccs-div-qc`, `qccq-regles-simplifiees`).
2. Valider via `gestion-du-mandat` (`conformite-echeanciers-cpc.md` et `outils.calendrier_deadlines`) le respect du **délai de rigueur d'inscription (`173` ou `535.13`)**, le délai de **`15 jours`** sur déclaration unilatérale (`174 al. 2`) et les délais de production au greffe (`250`).
3. Vérifier la concordance 1:1 des cotes (`P-`, `D-`), du calcul **`1 jour = 5 heures`** et des témoins avec l'inventaire (`248 al. 1`).
4. Exécuter `outils.terminologie_scan` sur toute annexe ou entente accessoire rédigée.
