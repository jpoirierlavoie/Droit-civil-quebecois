# Demandes en cours d'instance, modifications (206–208) et ordonnance de sauvegarde

À charger **avec `references/fondamentaux-actes.md`**. Encadre les demandes incidentes en cours d'instance (`101 C.p.c.`), la modification d'acte de procédure (`206–208 C.p.c.`) et les demandes d'ordonnance de sauvegarde (`49, 158 C.p.c.`).

## Vecteur législatif

* `law="cpc"` : `numbers=["49", "84", "99", "101", "105", "107", "158", "166", "173", "175", "176", "177", "180", "188", "192", "193", "194", "206", "207", "208", "213", "220", "227", "228", "246", "248", "251", "252", "527"]`
* Règlements et directives : `c-25.01-r.0.2.1` (C.S. art. 10–13), `c-25.01-r.9` (C.Q. art. 47 s.), plus directives C.S./C.Q. Vague 1 (`fonction='directive'`, `par.`/`dir.`, `fr`-only : `qccs-dist-mtl` `preseance-sur` `qccs-div-mtl` par. 33–35, `qccs-div-qc`, `qccq-regles-simplifiees`, `qccq-mtl-prat-civile`, `qccq-mtl-prat-admin` ; directives C.A.Q. hors corpus).

## Conditions et préalables

1. Vérifier si la demande en cours d'instance doit être **écrite** ou présentée **oralement** en gestion ou à l'audience (`101`, `158`).
2. **Déclaration sous serment (`101 al. 3`, `105 C.p.c.`) :** Requise **uniquement** si la demande repose sur des faits dont la preuve n'est pas déjà au dossier (ou si une disposition particulière l'exige — p. ex. défaut `175`, relevé du défaut `84`, sauvegarde urgente) ; jamais par automatisme lorsque toutes les pièces probantes sont déjà versées.
3. **Modification en deux temps (`206–208 C.p.c.`) :** Avant l'instruction, la modification s'opère **sans autorisation préalable du tribunal** si elle ne retarde pas l'instance, ne contrevient pas aux intérêts de la justice et ne crée pas une demande entièrement nouvelle sans rapport avec la demande initiale (`206`) : notifier d'abord l'acte modifié aux autres parties qui disposent de **`10 jours` pour notifier leur opposition (`207 al. 1`)**, et ne présenter une demande au tribunal **qu'en cas d'opposition** (ou demander l'autorisation sans formalités en présence des parties pendant l'instruction, `208 al. 1`).

## Forum et compétence

Mentionner sous le titre la disposition habilitante du C.p.c., du règlement du tribunal saisi (`c-25.01-r.0.2.1` art. 10 en C.S., `c-25.01-r.9` art. 47 en C.Q.) et de la directive de pratique applicable le cas échéant (`qccs-*`, `qccq-*`, textes non législatifs `fr`-only ; directives C.A.Q. hors corpus Vague 1), et diriger la présentation devant la chambre/salle appropriée (`outils.palais_get`, y compris compétence du greffier spécial `72 C.p.c.`).

## Structure obligatoire

### A. Demande écrite en cours d'instance (`101 C.p.c.`)
* Cartouche + Titre précisant l'article habilitant + Exposé factuel numéroté (`99`) + Conclusions précises + **Avis de présentation (`101`)** (date, heure, salle et palais ; préavis d'au moins **`3 jours`** sous `101 al. 1` sauf délai particulier).

### B. Acte de procédure modifié (`206–208 C.p.c.`, `c-25.01-r.0.2.1 art. 11`)
* Intitulé exact portant **`… MODIFIÉE`** (ou **`MODIFIÉ`**) ;
* **Gel strict des cotes existantes :** ne jamais renuméroter `P-3` en `P-2` après retrait de `P-2` — inscrire **`[Pièce P-2 retirée]`** et attribuer **`P-(n+1)`** à toute nouvelle pièce ;
* **Numérotation continue des paragraphes :** conserver les numéros existants (`14. (…)` / `[Retiré]`) et insérer les nouveaux faits par numérotation décimale (`12.1`, `12.2`) ;
* **Marquage réglementaire (`art. 11 R.C.s.Q.m.c.`) :** souligner les additions ou substitutions (ou les signaler en marge par un trait vertical) et indiquer les suppressions au moyen de **pointillés entre parenthèses `(…)`**.

### C. Ordonnance de sauvegarde (`49, 158 C.p.c.`), communication par un tiers (`251`) et incidents spécifiques
* **Ordonnance de sauvegarde (`49 al. 2`, `158(5°)(8°) C.p.c.`) :** Mesure conservatoire temporaire urgente destinée à préserver les droits des parties ou le *statu quo* pendant l'instance, sans trancher une demande complète d'injonction interlocutoire (`510 s.`). Lorsqu'elle est prononcée à titre de mesure de gestion (`158(8°)`), sa durée **ne peut excéder `6 mois`** (renouvelable ou modifiable sur demande). Démontrer l'urgence immédiate, l'apparence de droit, un préjudice sérieux ou irréparable et la prépondérance des inconvénients ; joindre une **déclaration sous serment circonstanciée (`101 al. 3`, `105`)** et formuler des conclusions précises et directement exécutoires.
* **Communication ou préservation d'un document détenu par un tiers (`251 al. 2 C.p.c.`) :** Demande écrite visant à enjoindre à un tiers de communiquer, présenter, soumettre à expertise ou préserver un document ou élément matériel se rapportant au litige, **notifiée obligatoirement au tiers visé** ainsi qu'aux parties.
* **Mise en cause / intervention forcée en cours d'instance (`158(4°)`, `184 al. 3`, `188 C.p.c.`) :** Signifier par huissier un acte d'intervention forcée exposant les motifs, accompagné de la demande en justice, proposant les modalités selon le protocole et indiquant le délai de réponse de **`15 jours`** (`188 al. 1` ; les autres parties disposent de **`10 jours`** suivant la réponse du tiers pour notifier leur opposition, `188 al. 2`).
* **Présentation des objections suspensives (`228 al. 2–4 C.p.c.`) :** Lorsqu'un témoin s'abstient de répondre à l'interrogatoire sur un motif d'objection suspensive (non-contraignabilité, droits fondamentaux, faits présumés non pertinents en violence sexuelle/conjugale, ou intérêt légitime important, `228 al. 2`), soumettre la demande au tribunal **dans les `5 jours`** (décision possible sur le vu du dossier selon `228 al. 4`). Les objections de pertinence (`228 al. 3`) ne suspendent pas l'interrogatoire : le témoin répond sous réserve et elles sont tranchées à l'instruction (sauf soumission sur-le-champ).
* **Prolongation du délai de rigueur de mise en état (`173 al. 2–3 C.p.c.`) et relèvement de la présomption de désistement (`177 C.p.c.`) :** Présenter la prolongation **avant l'expiration du délai de `6 mois`** (`173 al. 2`). Si le 1er protocole n'avait pas été déposé à temps (`173 al. 3`) ou si le délai de rigueur est expiré — emportant **présomption de désistement** à moins qu'une autre partie n'ait demandé l'inscription dans les **`30 jours`** (`177 al. 1`) —, le relèvement exige la preuve d'une **impossibilité d'agir de fait** (`173 al. 3`, `177 al. 2`).

### D. Inscription par défaut (`175–180 C.p.c.`) et relevé du défaut (`84 C.p.c.`)
* **Inscription pour jugement par défaut (`175, 180 C.p.c.`) :** Exposer la date de signification, l'expiration du délai, les pièces justificatives et déposer la **déclaration sous serment du demandeur** (`175 al. 2`). Distinguer impérativement selon `180 C.p.c.` :
  * *Défaut de répondre à l'assignation (`180 al. 1`)* : jugement possible **sans autre avis ni délai** (sauf avis d'au moins **`1 mois`** au procureur général) ;
  * *Défaut de participer à la conférence de gestion ou de contester dans le délai après réponse (`180 al. 2`)* : donner obligatoirement au défendeur un **préavis d'au moins `5 jours`** avant qu'il soit procédé à l'instruction par défaut.
* **Demande d'être relevé du défaut (`84 C.p.c.`) :** Applicable **avant jugement** (si le jugement par défaut est déjà rendu, basculer vers la *demande en rétractation* `345–349 C.p.c.`). Agir avec diligence dès la connaissance du défaut en exposant : (1) la chronologie, (2) une **cause valable** sans négligence grave ni abus, (3) l'absence de préjudice irrémédiable et (4) un **aperçu sérieux des moyens de défense au fond**, appuyé d'une déclaration sous serment (`105`), en joignant la réponse ou l'exposé sommaire prêt à être déposé.

### E. Représentation, substitution, cessation d'occuper (`192–194`) et désistement (`213`)
* **Acte de représentation / substitution (`192 al. 3`) et mise en demeure de constituer nouveau procureur (`192 al. 1`) :** L'avocat substitué notifie sans délai son acte de représentation aux parties et au greffier (avec autorisation du tribunal si la date d'instruction est déjà fixée, `194 al. 2`). Lorsqu'un avocat se retire, meurt ou devient inhabile avant le délibéré, la partie adverse met en demeure la partie de désigner un nouvel avocat ou d'indiquer qu'elle agit seule dans un délai suspensif de **`10 jours`** (`192 al. 1` : aucun acte ni jugement pendant ce délai).
* **Cessation d'occuper (`194 C.p.c.`) et secret professionnel :**
  * *Avant que la date de l'instruction ne soit fixée (`194 al. 1`)* : notifier l'avis d'intention de cesser d'occuper au client, aux autres parties et au greffier (dans le respect du préavis raisonnable déontologique) ;
  * *Lorsque la date de l'instruction est fixée (`194 al. 2`)* : présenter une demande d'**autorisation préalable au tribunal** — **sans jamais divulguer dans l'acte ni dans la déclaration sous serment de faits ou confidences protégés par le secret professionnel** (invoquer sobrement un motif déontologique neutre tel la rupture du lien de confiance).
* **Désistement (`213 C.p.c.`) et avis de règlement hors cour (`220 C.p.c.`) :** L'*Acte de désistement* précise sa portée et le sort des frais (`213` : à la charge du demandeur sauf entente contraire) ; en cas de transaction hors cour, déposer sans délai un *Avis de règlement hors cour* (`220`) pour libérer le rôle (voir `contrat-transaction-quittance.md`).

### F. Avis de présentation et avis de dépôt (`101`, `227 al. 2`, `246`, `248 C.p.c.`)
* **Avis de présentation :** Mentionner avec précision la date, l'heure, la salle exacte (p. ex. salle de pratique / gestion), le district, le palais de justice et le mode de comparution (en personne ou virtuel).
* **Avis de dépôt (`227 al. 2, 246, 248`) :** Identifier la nature exacte de l'élément déposé (notes sténographiques/transcription d'un interrogatoire hors cour, pièces additionnelles ou modifiées), sa date et sa cote.

## Pièces jointes et formalités

* Joindre l'avis de présentation (`101`), les pièces invoquées communiquées dès que possible (`252`) et la déclaration sous serment (`101 al. 3`, `105`) seulement si des faits hors dossier l'exigent.
* **Inscription au rôle et opposition en pratique (`107 al. 2`, `qccs-div-mtl` par. 33–35) :** Notifier dans le délai applicable (`101 al. 1` `>= 3 j`, ou `>= 3 j ouvrables` à Montréal `par. 33`, sous réserve des délais particuliers `166 al. 2`, `180 al. 2`, `207`, `228 al. 2`, `527`) et déposer au greffe avec preuve de notification au moins **`2 jours ouvrables`** avant la présentation (`107 al. 2`, `par. 33`). À Montréal, la partie qui s'oppose et invoque des déclarations sous serment ou pièces les notifie et les dépose au plus tard à **12 h le jour ouvrable qui précède la présentation** (`par. 35`).

## Particularités et pièges

* **Renumérotation des pièces après modification :** faute grave créant des incohérences dans les transcriptions d'interrogatoires et bordereaux déjà communiqués.
* **Violation du secret professionnel sous `194 al. 2` :** ne jamais détailler dans la demande pour cesser d'occuper les différends d'honoraires confidentiels, la stratégie ou les déclarations privées du client.
* **Terme proscrit et formule introductive des conclusions :** jamais « requête » (terme antérieur à 2016) ni « motion » en français ; employer `DEMANDE EN COURS D'INSTANCE` ou `DEMANDE DE ...`. En tête des conclusions, employer uniformément la formule exacte **`POUR CES MOTIFS, PLAISE AU TRIBUNAL :`**.

## Conclusions types

* `ACCUEILLIR la présente demande en cours d'instance ;`
* *(Modification — uniquement en cas d'opposition notifiée sous `207 al. 1` ou à l'instruction `208`)* `AUTORISER le Demandeur à modifier sa demande introductive d'instance conformément à la Demande introductive d'instance modifiée ci-jointe ;`
* *(Sauvegarde)* `PRONONCER une ordonnance de sauvegarde enjoignant à [partie] de [mesure précise] jusqu'à [échéance <= 6 mois en gestion] ;`
* *(Relevé du défaut `84`)* `ACCUEILLIR la présente demande ; RELEVER [le Défendeur] du défaut de [répondre / produire son exposé] ; AUTORISER le dépôt de [sa réponse / sa défense] dans un délai de [X] jours [ou PRENDRE ACTE de son dépôt déjà effectué] ; LE TOUT frais à suivre [ou sans frais] ;`
* `LE TOUT frais à suivre / avec les frais de justice.`

## Délais (renvoi)

Articles à vérifier et chiffrer via `gestion-du-mandat` (`conformite-echeanciers-cpc.md` et `outils.calendrier_deadlines`) : `101 al. 1` (préavis `>= 3 j` sous réserve des délais particuliers), `107 al. 2` / `qccs-div-mtl par. 33–35` (dépôt `>= 2 j ouvrables`, pièces d'opposition `12 h` la veille ouvrable), `177 al. 1` (présomption de désistement à l'échéance de `6 mois`, sauf inscription par une autre partie sous `30 j`), `180 al. 2` (préavis `>= 5 j` avant instruction par défaut après réponse), `192 al. 1` (mise en demeure de désigner avocat `10 j`), `207 al. 1` (opposition à modification `10 j`), `228 al. 2` (objection suspensive `5 j`).
