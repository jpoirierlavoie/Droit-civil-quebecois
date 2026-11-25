# Demandes en cours d'instance, modifications (206–208) et ordonnance de sauvegarde

[NON VALIDÉ PAR LA PRATIQUE]

À charger **avec `references/fondamentaux-actes.md`**. Encadre les demandes incidentes en cours d'instance (`101 C.p.c.`), la modification d'acte de procédure (`206–208 C.p.c.`) et les demandes d'ordonnance de sauvegarde (`49, 158 C.p.c.`).

## Vecteur législatif

* `law="cpc"` : `numbers=["49", "84", "99", "101", "105", "158", "166", "173", "175", "176", "177", "192", "193", "194", "206", "207", "208", "213", "220", "227", "228", "246", "248", "527"]`
* Règlements et directives : `c-25.01-r.0.2.1` (C.S. art. 10 s.), `c-25.01-r.9` (C.Q. art. 47 s.), plus directives C.S./C.Q. Vague 1 (`fonction='directive'`, `par.`/`dir.`, `fr`-only : `qccs-dist-mtl` `preseance-sur` `qccs-div-mtl`, `qccs-div-qc`, `qccq-regles-simplifiees`, `qccq-mtl-prat-civile`, `qccq-mtl-prat-admin` ; directives C.A.Q. hors corpus).

## Conditions et préalables

1. Vérifier si la demande en cours d'instance doit être **écrite** ou présentée **oralement** en gestion (`101`, `158`).
2. **Déclaration sous serment (`101 al. 3`, `105 C.p.c.`) :** Requise **uniquement** si la demande repose sur des faits dont la preuve n'est pas déjà au dossier (ou si une disposition particulière l'exige — p. ex. sauvegarde urgente); jamais par automatisme lorsque toutes les pièces probantes sont déjà versées.
3. **Modification (`206–208 C.p.c.`) :** Vérifier si la modification intervient avant ou après réponse/inscription et si elle ajoute un nouveau fait ou remédie à un moyen préliminaire sans retarder inutilement l'instance.

## Forum et compétence

Mentionner sous le titre la disposition habilitante du C.p.c., du règlement du tribunal saisi (`c-25.01-r.0.2.1` art. 10 en C.S., `c-25.01-r.9` art. 47 en C.Q.) et de la directive de pratique applicable le cas échéant (`qccs-*`, `qccq-*`, textes non législatifs `fr`-only ; directives C.A.Q. hors corpus Vague 1), et diriger la présentation devant la chambre/salle appropriée (`outils.palais_get`).

## Structure obligatoire

### A. Demande écrite en cours d'instance (`101 C.p.c.`)
* Cartouche + Titre précisant l'article habilitant + Exposé factuel numéroté (`99`) + Conclusions précises + **Avis de présentation (`101`)** (date, heure, salle et palais; mention du préavis applicable).

### B. Acte de procédure modifié (`206–208 C.p.c.`)
* Intitulé exact portant **`… MODIFIÉE`** (ou **`MODIFIÉ`**);
* **Gel strict des cotes existantes :** ne jamais renuméroter `P-3` en `P-2` après retrait de `P-2` — inscrire **`[Pièce P-2 retirée]`** et attribuer **`P-(n+1)`** à toute nouvelle pièce;
* **Numérotation continue des paragraphes :** conserver les numéros existants (`14. [Retiré] ;`) et insérer les nouveaux faits par numérotation décimale (`12.1`, `12.2`);
* Marquer visuellement ajouts (soulignement) et suppressions (rature ou `[Retiré]`) selon les exigences réglementaires du tribunal.

### C. Ordonnance de sauvegarde (`49, 158 C.p.c.`) et incidents spécifiques
* **Ordonnance de sauvegarde (`49 al. 2`, `158(5°)(8°) C.p.c.`) :** Mesure conservatoire temporaire urgente destinée à préserver les droits des parties ou le *statu quo* pendant l'instance, sans trancher une demande complète d'injonction interlocutoire (`510 s.`). Lorsqu'elle est prononcée à titre de mesure de gestion (`158(8°)`), sa durée **ne peut excéder `6 mois`** (renouvelable ou modifiable sur demande). Démontrer l'urgence immédiate, l'apparence de droit, un préjudice sérieux ou irréparable et la prépondérance des inconvénients; joindre une **déclaration sous serment circonstanciée (`101 al. 3`, `105`)** et formuler des conclusions précises et directement exécutoires.
* **Mise en cause / intervention forcée en cours d'instance (`158(4°)`, `184 al. 3`, `188 C.p.c.`) :** Pour joindre un tiers nécessaire à la solution complète du litige, lui opposer le jugement ou l'appeler en garantie, signifier par huissier un acte d'intervention forcée exposant les motifs, accompagné de la demande en justice, proposant les modalités selon le protocole et indiquant le délai de réponse de **`15 jours`** (`188 al. 1`; les autres parties disposent de **`10 jours`** suivant la réponse du tiers pour notifier leur opposition, `188 al. 2`).
* **Présentation des objections suspensives (`228 al. 2–4 C.p.c.`) :** Lorsqu'un témoin s'abstient de répondre à l'interrogatoire sur un motif d'objection suspensive (non-contraignabilité, droits fondamentaux, faits présumés non pertinents en violence sexuelle/conjugale, ou intérêt légitime important, `228 al. 2`), soumettre la demande au tribunal **dans les `5 jours`** (décision possible sur le vu du dossier selon `228 al. 4`). Les objections de pertinence (`228 al. 3`) ne suspendent pas l'interrogatoire : le témoin répond sous réserve et elles sont tranchées à l'instruction (sauf soumission sur-le-champ).
* **Prolongation du délai de rigueur de mise en état (`173 al. 2–3 C.p.c.`) :** Présenter **avant l'expiration du délai de `6 mois`** en démontrant soit (1) le degré élevé de complexité ou des circonstances spéciales en conférence de gestion, soit (2) l'impossibilité d'évaluer adéquatement le délai lors de la conférence ou la survenance de faits alors imprévisibles (`173 al. 2`). Attention : si le protocole n'avait pas été déposé dans les `45 jours` / `3 mois`, le tribunal ne peut prolonger le délai calculé depuis la signification que sur preuve d'**impossibilité d'agir** (`173 al. 3`).

### D. Inscription par défaut (`175–177 C.p.c.`) et relevé du défaut (`84 C.p.c.`)
* **Inscription pour jugement par défaut (`175`):** Exposer la date de signification, l'expiration du délai de réponse/contestation, l'absence de réponse ou de défense, les pièces justificatives de la créance/préjudice et joindre une **déclaration sous serment** attestant les faits et le montant exact dû (ou demander l'enquête devant le greffier spécial/tribunal selon `175–176`).
* **Demande d'être relevé du défaut (`84 C.p.c.`):** Applicable **avant jugement** (si le jugement par défaut est déjà rendu, basculer vers la *demande en rétractation* `345–349 C.p.c.`). Agir avec diligence dès la connaissance du défaut en exposant : (1) le rappel chronologique de la signification et de l'échéance manquée, (2) une **cause valable** expliquant le défaut sans négligence grave ni abus (erreur administrative documentée, absence, malentendu procédural), (3) l'absence de préjudice irrémédiable pour la partie adverse, et (4) un **aperçu sérieux des moyens de défense au fond**, le tout appuyé d'une déclaration sous serment (`105`). Si possible, joindre la réponse ou l'exposé sommaire prêt à être déposé.

### E. Représentation, substitution, cessation d'occuper (`192–194`) et désistement (`213`)
* **Acte de représentation / substitution (`192`):** Dénoncer sans délai aux parties et au greffe la constitution d'un nouveau procureur (incluant coordonnées complètes et courriel de notification).
* **Avis d'intention de cesser d'occuper (`194 C.p.c.`):** Distinguer selon que la **date d'instruction est fixée ou non** — avant fixation, préavis de `10 jours` notifié au client et aux autres parties suivi du dépôt avec preuve de notification ; après fixation, autorisation préalable du tribunal requise.
* **Désistement (`213 C.p.c.`) et avis de règlement hors cour (`220 C.p.c.`) :** L'*Acte de désistement* (total ou partiel) précise la portée et le sort des frais de justice ; dès qu'un règlement intervient avant jugement, déposer sans délai un *Avis de règlement hors cour* (`220 C.p.c.`) précisant si le règlement est total ou partiel, si un jugement est requis pour lui donner effet et demandant au greffe de libérer la date d'audience / suspendre les échéances restantes.

### F. Avis de présentation et avis de dépôt (`101`, `227 al. 2`, `246`, `248 C.p.c.`)
* **Avis de présentation :** Mentionner avec précision la date, l'heure, la salle exacte (p. ex. salle de pratique / gestion), le district, le palais de justice et le mode de comparution (en personne ou virtuel).
* **Avis de dépôt (`227 al. 2, 246, 248`):** Identifier la nature exacte de l'élément déposé (notes sténographiques/transcription d'un interrogatoire hors cour, pièces additionnelles ou modifiées), sa date et sa cote.

## Pièces jointes et formalités

* Joindre l'avis de présentation (`101`), les pièces invoquées non déjà communiquées et la déclaration sous serment (`101 al. 3`, `105`) seulement si des faits nouveaux hors dossier l'exigent (obligatoire pour le défaut `175`, le relevé du défaut `84` ou la sauvegarde).
* Notifier selon le délai applicable (`101 al. 1` ou délai particulier : `166 al. 2`, `194`, `527`, `308`, `530`).

## Particularités et pièges

* **Renumérotation des pièces après modification :** faute grave créant des incohérences dans les transcriptions d'interrogatoires et bordereaux déjà communiqués.
* **Terme proscrit et formule introductive des conclusions :** jamais « requête » (terme antérieur à 2016) ni « motion » en français; employer `DEMANDE EN COURS D'INSTANCE` ou `DEMANDE DE ...`. En tête des conclusions, employer uniformément la formule exacte **`POUR CES MOTIFS, PLAISE AU TRIBUNAL :`** (jamais de tournure hybride).

## Conclusions types

* `ACCUEILLIR la présente demande en cours d'instance ;`
* *(Modification)* `AUTORISER le Demandeur à modifier sa demande introductive d'instance conformément à la Demande introductive d'instance modifiée ci-jointe ;`
* *(Sauvegarde)* `PRONONCER une ordonnance de sauvegarde enjoignant à [partie] de [mesure précise] jusqu'à [échéance] ;`
* *(Relevé du défaut `84`)* `ACCUEILLIR la présente demande ; RELEVER [le Défendeur] du défaut de [répondre / produire son exposé] ; AUTORISER le dépôt de [sa réponse / sa défense] dans un délai de [X] jours [ou PRENDRE ACTE de son dépôt déjà effectué] ; LE TOUT frais à suivre [ou sans frais] ;`
* `LE TOUT frais à suivre / avec les frais de justice.`

## Délais (renvoi)

Articles à vérifier et chiffrer via `gestion-du-mandat` (`conformite-echeanciers-cpc.md` et `outils.calendrier_deadlines`) : `101 al. 1` (préavis `>= 3 j` sous réserve des délais particuliers `527`, `166 al. 2`, `308`, `530`, `377`), `175–177` (défaut et radiation après `1 an`), `194` (cessation d'occuper), `207` (opposition à modification `10 j`), `228 al. 2` (objection suspensive `5 j`).
