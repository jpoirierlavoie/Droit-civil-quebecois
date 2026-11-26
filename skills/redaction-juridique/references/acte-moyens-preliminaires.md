# Demandes en moyens préliminaires (déclinatoire, irrecevabilité, précisions, abus)

À charger **avec `references/fondamentaux-actes.md`**. Encadre la rédaction des moyens préliminaires (`166–169`, `51–54`, `535.5`, `622 C.p.c.`) : moyen déclinatoire, renvoi à l'arbitrage, irrecevabilité, précisions, radiation d'allégations et rejet pour abus de procédure.

## Vecteur législatif

* `law="cpc"` : `numbers=["41", "43", "51", "52", "53", "54", "85", "101", "105", "107", "146", "166", "167", "168", "169", "206", "535.5", "535.11", "622"]`
* Règlements et directives (`fonction='directive'`, `fr`-only) : `c-25.01-r.0.2.1` (C.S.), `c-25.01-r.9` (C.Q.), `qccs-dist-mtl` (`preseance-sur` `qccs-div-mtl` par. 33, 112), `qccs-div-qc`, `qccq-regles-simplifiees` (`par. 5–6`, formulaire obligatoire **`SJ-1274`**).

## Conditions et préalables

1. **Dénonciation, fenêtres et formulaire obligatoire (`166 al. 2`, `52 al. 2`, `535.5`, `622 al. 2`) :**
   * En instance ordinaire (`166 al. 2`), dénoncer par écrit et déposer avant la date du protocole, à la date prévue au protocole ou au plus tard `3 jours` avant la conférence de gestion sur le protocole (ou `>= 3 jours` avant présentation si aucun protocole; **`>= 10 jours` si irrecevabilité invoquée**; idem **`>= 10 jours`** pour une demande en rejet pour abus avant l'instruction selon `52 al. 2`).
   * **Convention d'arbitrage (`622 al. 2 C.p.c.`, `3148 al. 2 C.c.Q.`) :** soulever impérativement la demande de renvoi à l'arbitrage dans les **`45 jours`** de la signification de la demande introductive (**`90 jours`** si élément d'extranéité), avant toute défense au fond ou reconnaissance tacite de la compétence judiciaire.
   * En **régime simplifié C.Q. (`535.5`)**, dénoncer par écrit et déposer au greffe dans les **`45 jours` de la signification de l'avis d'assignation**, accompagné obligatoirement en tête d'acte du formulaire **`SJ-1274`** (*Avis de dénonciation de moyens préliminaires et incidents*, `qccq-regles-simplifiees` par. 5–6, sous peine de **refus de dépôt par le greffier**) ; observations écrites adverses dans les **`10 jours`** et décision possible sur le vu du dossier (`535.5 al. 3`).
2. **Couverture c. survie des moyens :** L'incompétence d'attribution (`167 al. 2` — même d'office) et l'irrecevabilité d'une demande (`168 al. 5`) ne sont pas couvertes par le silence initial ; en revanche, **l'incompétence territoriale se couvre** faute d'être dénoncée à temps sous `166` (noter la demande simplifiée adressée au greffier spécial sous `43, 146 al. 4 C.p.c.` pour le salarié, le consommateur, l'assuré ou le débiteur hypothécaire résidentiel).
3. **Qualification précise du moyen :**
   * *Déclinatoire (`167`, `622`)* : incompétence d'attribution, territoriale (`41–43`, élection de for nulle en adhésion `41 al. 3`) ou internationale (`3148–3149 C.c.Q.`), ou renvoi à l'arbitrage (`622`) ; demander le renvoi au tribunal compétent / à l'arbitrage ou, à défaut, le rejet.
   * *Irrecevabilité (`168`)* : (`al. 1`) litispendance ou chose jugée (`2848 C.c.Q.`, triple identité), incapacité/défaut de qualité (`85`), absence manifeste d'intérêt ; ou (`al. 2`) absence de fondement en droit quoique les faits allégués puissent être vrais (total ou partiel).
   * *Mesures de déroulement / précisions / radiation (`169`, `535.11`)* : précisions sur allégations vagues, communication d'un document ou radiation d'allégations non pertinentes (sous peine de rejet/radiation à l'expiration du délai imparti) — **en régime simplifié C.Q. (`535.11`), les précisions ou radiations ne sont ordonnées qu'exceptionnellement, si des motifs sérieux le commandent**.
   * *Abus de procédure (`51–54`)* : demande ou acte manifestement mal fondé, frivole, dilatoire, quérulent ou excessif (incluant SLAPP / débat public traité en priorité selon `52 al. 5`). Établir sommairement l'abus renverse le fardeau sur l'auteur de l'acte (`52 al. 1`).

## Forum et compétence

Vérifier en priorité le moyen déclinatoire ou d'arbitrage (`167`, `622`, `41–43 C.p.c.`, `3148 C.c.Q.`) avant tout moyen supposant la compétence du tribunal saisi, et soumettre devant la chambre / juge gestionnaire du tribunal déjà saisi (`c-25.01-r.0.2.1` C.S., `c-25.01-r.9` C.Q.; `outils.palais_get`). Note : le tribunal peut refuser une demande en rejet sous `168 al. 3`, `52 al. 2` ou `535.5 al. 3` **sur le vu du dossier** faute de chance raisonnable de succès.

## Structure obligatoire

1. Cartouche + Désignation + Titre ciblé : **`DEMANDE EN [MOYEN DÉCLINATOIRE / RENVOI À L'ARBITRAGE / IRRECEVABILITÉ / PRÉCISIONS ET RADIATION / REJET POUR ABUS DE PROCÉDURE]`** `(Articles ... du Code de procédure civile)` ;
2. Rappel chronologique sobre des actes en cause (date de dépôt/signification de la demande attaquée, état du protocole ou échéancier `535.5`);
3. Exposé des motifs par paragraphes numérotés (`99`) : pour `168 al. 2`, énoncer expressément que les faits allégués dans la demande sont **tenus pour avérés aux seules fins du moyen** ; pour `168 al. 1`, `622` ou `51–54`, exposer les faits extrinsèques établissant la litispendance, la chose jugée, la convention d'arbitrage ou le caractère sommaire de l'abus ; pour `169` (`art. 12 R.C.s.Q.m.c.`), cibler précisément chaque paragraphe visé en reprenant son numéro et la lacune concrète ;
4. Conclusions graduées (renvoi vs rejet total/partiel vs cure `168 al. 4` vs provision pour frais `53 al. 2(5°)` et honoraires/dommages punitifs `54`) + Signature + Avis de présentation (`101`, `166 al. 2`, `52 al. 2`).

## Pièces jointes et formalités

* **Avis de présentation et dépôt au rôle (`101 al. 1`, `107 al. 2`, `qccs-div-mtl` par. 33, 112) :** Respecter **`>= 10 jours`** pour l'irrecevabilité (`166 al. 2`) et l'abus avant l'instruction (`52 al. 2`), ou **`>= 3 jours`** (`>= 3 jours ouvrables` à Montréal, `qccs-div-mtl` par. 33) pour `167` / `169` seuls, et **déposer la demande accompagnée de la preuve de notification au greffe au moins `2 jours ouvrables` avant la présentation** pour inscription au rôle (`107 al. 2`, `par. 33`). Si des représentations écrites sont produites, vérifier le plafond de la directive applicable (p. ex. `<= 10 pages` sous `qccs-div-mtl` par. 112). En C.Q. simplifiée (`535.5`), agrafer/placer **`SJ-1274`** devant l'acte.
* **Déclaration sous serment (`101 al. 3`, `105`) et pièces admissibles :** Déclaration sous serment exigée **uniquement** pour les moyens reposant sur des faits hors dossier (litispendance, jugement établissant chose jugée `2848 C.c.Q.`, transaction/quittance, convention d'arbitrage `622`, faits sommaires d'abus). **Sur un moyen pur d'irrecevabilité en droit (`168 al. 2`), ne joindre aucune déclaration sous serment ni aucune pièce extrinsèque du défendeur** : seuls l'acte attaqué et les pièces alléguées à son soutien sont examinables.
* **Contestation :** La demande avant l'instruction en abus (`52 al. 2`) est contestée **oralement** sur le vu des actes, pièces au dossier et transcriptions d'interrogatoires préalables (autre preuve seulement si le tribunal l'estime nécessaire, `52 al. 4`).

## Particularités et pièges

* **Contredire les faits ou verser des pièces extrinsèques sous `168 al. 2` :** Faute stratégique classique causant le refus immédiat du moyen — sur défaut de fondement en droit, tenir temporairement pour avérés les faits allégués (et les seules pièces invoquées au soutien de la demande) pour démontrer l'absence de cause d'action ou la prescription apparente.
* **Irrégularité corrigible (`168 al. 4`, `206`) :** Anticiper que le tribunal peut accorder un délai de correction au lieu de rejeter d'emblée un vice remédiable (qualité, autorisation, précision).
* **Omettre `SJ-1274` ou méconnaître `535.11` en régime simplifié C.Q. :** Sans le formulaire `SJ-1274` joint à l'acte dénoncé dans les `45 jours` (`535.5`), le greffier refuse le dépôt (`qccq-regles-simplifiees` par. 6) ; et éviter les demandes routinières de précisions/radiation qui échouent faute de motifs sérieux (`535.11`).

## Conclusions types

* *(Déclinatoire `167` / Arbitrage `622`)* `ACCUEILLIR le moyen déclinatoire ; RENVOYER le présent dossier devant [la Cour supérieure / la Cour du Québec] du district de [District] [ou RENVOYER les parties à l'arbitrage / à défaut, REJETER la demande introductive d'instance] ;`
* *(Irrecevabilité `168`)* `ACCUEILLIR la demande en irrecevabilité ; REJETER [en totalité / quant aux paragraphes X à Y et à la conclusion Z] la demande introductive d'instance ;`
* *(Abus `51–54`)* `DÉCLARER la demande introductive d'instance [ou l'acte de procédure] abusive ; REJETER la demande introductive d'instance ; CONDAMNER [le Demandeur] à payer à [la Défenderesse] la somme de [...] $ à titre de dommages-intérêts compensant les honoraires et débours engagés [et (...) $ en dommages-intérêts punitifs] ;`
* *(Frais)* `LE TOUT avec les frais de justice.`

## Délais (renvoi)

Articles à vérifier et chiffrer via `gestion-du-mandat` (`conformite-echeanciers-cpc.md` et `outils.calendrier_deadlines`) : `166 al. 2` (irrecevabilité `10 j`, autres moyens `3 j`), `52 al. 2` (abus pré-instruction `10 j`), `107 al. 2` / `qccs-div-mtl par. 33` (dépôt au greffe `>= 2 j ouvrables`), `622 al. 2` (arbitrage `45 j` / `90 j` extranéité), `535.5` (dénonciation C.Q. simplifiée avec `SJ-1274` `45 j`, observations `10 j`).
