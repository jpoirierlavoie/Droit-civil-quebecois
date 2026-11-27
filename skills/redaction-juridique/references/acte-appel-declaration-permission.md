# Déclaration d'appel et demande de permission d'appeler (`C.p.c.` & `c-25.01-r.0.2.01`)

À charger **avec `references/fondamentaux-actes.md`**. Encadre la rédaction de la déclaration d'appel (`352–353, 358 C.p.c.`), de la demande de permission d'appeler (`357 C.p.c.`) et de la déclaration d'appel incident (`359 C.p.c.`).

## Vecteur législatif

* `law="cpc"` : `numbers=["30", "31", "32", "352", "353", "354", "355", "357", "358", "359", "360", "361", "363", "365"]`
* `law="c-25.01-r.0.2.01"` (*Règlement de la Cour d'appel du Québec en matière civile*) : charger la structure (`get_structure`) pour vérifier pagination, polices et formalités exactes *(les directives C.A.Q. `QCCA` sont hors Vague 1 et se vérifient à la source)*.
* `law="t-15.01"` (*Loi sur le Tribunal administratif du logement*, `numbers=["91", "92", "93", "94"]`), `law="c-25.01-r.9"` et `qccq-daa-jurisprudence` (`fonction='directive'`, `fr`-only) pour la permission d'appeler devant la **Cour du Québec (Division administrative et d'appel)**.

## Conditions et préalables

1. Vérifier sans délai la date d'ancrage du jugement entrepris et sa nature (**final** vs **en cours d'instance / mesure de gestion**).
2. Déterminer s'il s'agit d'un **appel de plein droit (`30 al. 1`)** ou sur **permission (`30 al. 2`, `31`, `32`, `357`)** — valeur en litige, matière, rejet pour abus, jugement en cours d'instance causant un préjudice irréparable.
3. Contrôler le délai de rigueur (`360–361, 363 C.p.c.`) via `gestion-du-mandat` (`conformite-echeanciers-cpc.md` et `outils.calendrier_deadlines`).

## Forum et compétence

1. **Cour d'appel du Québec :** Division d'appel compétente (**Montréal** ou **Québec** selon le district d'origine du jugement entrepris, `c-25.01-r.0.2.01`).
2. **Cour du Québec — Division administrative et d'appel (`n° 500-80-...`, `91–94 LTAL`) :** Appel sur permission d'une décision du Tribunal administratif du logement (TAL) lorsque le recours est ouvert par la loi.

## Structure obligatoire

* **Déclaration d'appel (`352–353 C.p.c.`) :**
  1. Cartouche d'appel (Cour d'appel, division, district d'origine, numéro de 1re instance et place du numéro d'appel);
  2. Désignation complète des parties avec rôle en appel (`Appelant` / `Intimé` / `Mis en cause`) et mention de leur rôle en 1re instance;
  3. Tribunal, juge et date du jugement entrepris, nature du litige et valeur en litige;
  4. Voie d'appel (plein droit vs avec demande de permission jointe);
  5. **Énoncé concis des moyens d'erreur** (erreurs de droit — norme correcte — vs erreurs manifestes et déterminantes sur les faits ou mixtes);
  6. **Conclusions précises** recherchées en appel (infirmation, dispositif substitué ou renvoi);
  7. Mention du temps estimé de plaidoirie s'il y a lieu et liste des annexes/pièces jointes selon `c-25.01-r.0.2.01`.
* **Demande de permission d'appeler devant la Cour d'appel (`357 C.p.c.`) :** Démontrer l'intérêt de la justice et, s'il s'agit d'un jugement en cours d'instance (`31`) ou d'une mesure de gestion (`32`), que le jugement tranche déjà une question ou cause un préjudice irréparable.
* **Demande pour permission d'appeler d'une décision du TAL devant la C.Q. (`91–94 LTAL`) :**
  1. Cartouche Cour du Québec — **Division administrative et d'appel** (`500-80-...`), désignation `Requérant` / `Intimé` et mention du `Tribunal administratif du logement` / numéro de dossier TAL;
  2. Vérification préalable que la décision n'est pas visée par une exclusion d'appel (`91 LTAL` — p. ex. certaines demandes visées à l'art. `73` ou fixation de loyer) et identification d'une **question de droit** ou question de compétence/mixte justifiant l'intervention;
  3. Exposé chronologique bref, moyens d'erreur précis visant le décideur administratif, cotes de pièces attribuées en **`R-1..R-n`**, et structure des conclusions en deux volets distincts : (a) **« LES CONCLUSIONS RECHERCHÉES EN APPEL »** (révision/infirmation sur le fond), puis (b) **« POUR CES MOTIFS, PLAISE À LA COUR : »** couvrant permission d'appeler, **sursis provisoire d'exécution / d'expulsion (`94 al. 2 LTAL`)** uniquement sur preuve d'un **`préjudice grave`** (aucun sursis automatique au stade de la demande de permission sous `94 al. 1 LTAL`), et accueil au fond, avec avis de présentation en C.Q.

## Pièces jointes et formalités

* Joindre une copie du jugement entrepris et de l'avis du jugement (`355`, `358 C.p.c.`), ou, pour un appel du TAL en C.Q., la décision attaquée, la demande initiale et les pièces pertinentes sous bordereau **`R-1..R-n`**.
* **Signification et dépôt (`354`, `358 C.p.c.` ; `92 LTAL`) :** Signification à la partie intimée et aux autres parties avec attestation de signification, puis dépôt au greffe compétent dans le délai de rigueur ; en appel du TAL (`92 LTAL`), la demande de permission est signifiée à la partie adverse et déposée au greffe de la Cour du Québec dans les **`30 jours`** (le greffier de la Cour du Québec transmet ensuite sans délai le jugement accordant la permission au TAL). Vérifier tout avis ou copie de courtoisie prévu par la directive locale.
* Respecter la présentation matérielle et le format prescrits par `c-25.01-r.0.2.01` (Cour d'appel) ou `c-25.01-r.9` (Cour du Québec).

## Particularités et pièges

* **Délai de rigueur (`363 C.p.c.` et `92 LTAL`) :** L'expiration emporte déchéance; en appel C.A. (`363 al. 2`), la prolongation exige l'impossibilité en fait d'agir plus tôt. Pour l'appel du TAL en C.Q. (`92 LTAL`), le délai de **`30 jours`** court à compter de la **connaissance de la décision** — vérifier strictement l'avis de notification ou la preuve de réception.
* **Confusion plein droit vs permission (`30–32`) et exclusions `91 LTAL` :** Déposer une simple déclaration sans permission sur un jugement qui l'exige — ou tenter d'appeler d'une décision du TAL exclue par l'art. `91` au lieu d'évaluer la rétractation (`89 LTAL`) ou le contrôle judiciaire — expose au rejet immédiat (`365 C.p.c.`).
* **Sursis d'exécution / d'expulsion (`94 LTAL`) :** Aux termes de `94 al. 1 LTAL`, le dépôt d'une demande de permission d'appeler n'emporte **aucun sursis automatique** (contrairement à l'appel autorisé sur permission, sous réserve des exceptions légales). Lorsque l'exécution ou l'expulsion est imminente, conclure expressément au **sursis provisoire (`94 al. 2 LTAL`)** en démontrant un **`préjudice grave`** (critère statutaire propre à l'art. `94 al. 2`, distinct d'un simple inconvénient).

## Conclusions types

* *(Appel TAL en C.Q. `91–94 LTAL` — deux volets distincts)*
  * **`LES CONCLUSIONS RECHERCHÉES EN APPEL` :** `ACCUEILLIR l'appel ; INFIRMER la décision rendue le [date] par le Tribunal administratif du logement dans le dossier [numéro] ; [REJETER la demande initiale / ORDONNER ...] ; LE TOUT avec les frais de justice.`
  * **`POUR CES MOTIFS, PLAISE À LA COUR :`** `ACCORDER au requérant la permission d'appeler de la décision du Tribunal administratif du logement rendue le [date] ; [SURSEOIR provisoirement à l'exécution de ladite décision jusqu'à jugement final en vertu de l'article 94 al. 2 LTAL ;] ACCUEILLIR l'appel et RENDRE les conclusions recherchées ci-dessus ; LE TOUT avec les frais de justice.`
* *(Appel C.A.Q. ordinaire)* `ACCUEILLIR l'appel [et ACCORDER la permission d'appeler] ;`
* `INFIRMER le jugement rendu le [date] par [tribunal/juge] dans le dossier n° [numéro] ;`
* `RENDRE le jugement qui aurait dû être rendu et [CONDAMNER / REJETER ...] ;`
* `LE TOUT avec les frais de justice, tant en première instance qu'en appel.`

## Délais (renvoi)

Articles à vérifier et chiffrer via `gestion-du-mandat` (`conformite-echeanciers-cpc.md` et `outils.calendrier_deadlines`) : `360` (`30 jours`), `361` (`10 jours` ou `5 jours`), `363` (rigueur), `358` (signification/dépôt), `359` (appel incident `10 jours`), `373` (mémoire `3 mois`), ainsi que `92 LTAL` (`30 jours` de la connaissance devant la C.Q. `500-80`).
