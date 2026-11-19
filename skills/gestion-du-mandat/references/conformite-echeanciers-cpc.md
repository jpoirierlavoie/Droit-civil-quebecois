# Échéanciers et computation des délais en procédure civile (C.p.c.)

Gouverne les délais de l'instance civile (ordinaire, Cour du Québec art. 535.1 s., appel) et leur qualification. **La prescription substantielle (art. 2875–2933 C.c.Q.) n'est pas ici : elle relève de `recherche-juridique`.**

## Déclencheurs

* Signification, notification (incluant technologique après `17 h 00`) ou avis du jugement reçu;
* Établissement d'un calendrier d'instance ordinaire, d'un échéancier en régime simplifié C.Q. (`535.1 s.`) ou d'un calendrier d'appel;
* Objection suspensive (`228 al. 2` — 5 jours), rétractation (`347`), opposition à modification (`207`) ou révision de frais (`344`);
* Calcul à rebours avant une instruction (`250` : production au greffe au moins `15 jours` avant l'instruction).

## Vecteur

Lire obligatoirement via `lois.get_articles` avant tout tableau formel :
* **Principes (`cpc` & `i-16`) :** `law="cpc"`, `numbers=["82", "83", "84", "107", "111"]` et `law="i-16"`, `numbers=["61"]`.
* **Instance ordinaire (`cpc`) :** `numbers=["101", "107", "145", "148", "149", "150", "152", "166", "168", "170", "173", "174", "175", "177", "178", "180", "186", "188", "207", "490"]`.
* **Régime simplifié C.Q. (`< 100 000 $`, `cpc`) :** `numbers=["535.1", "535.2", "535.4", "535.5", "535.6", "535.7", "535.8", "535.12", "535.13"]`.
* **Preuve & interrogatoires (`cpc`) :** `numbers=["223", "226", "228", "241", "243", "246", "248", "250", "262", "269", "293"]`.
* **Incidents, rétractation, appel & exécution (`cpc`) :** `numbers=["192", "194", "324", "338", "344", "347", "349", "355", "357", "358", "360", "361", "363", "365", "372", "373", "374", "376", "510", "521", "522", "656", "661"]`. Lire aussi `c-25.01-r.0.2.01` (règlement C.A.Q.), `r.0.2.1` (règlement C.S.), `r.9` (règlement C.Q.) et les directives C.S./C.Q. Vague 1 (`fonction='directive'`, `qccs-dist-mtl` `preseance-sur` `qccs-div-mtl`, `qccs-div-qc`, `qccq-regles-simplifiees`, `qccq-mtl-prat-civile`, `qccq-mtl-prat-admin`, `qccq-daa-jurisprudence`, en `par.`/`dir.`, `fr`-only) ; les directives C.A.Q. restent hors corpus.

## Obligations

### 1. Principes de computation (`art. 82–84, 107, 111 C.p.c.`, `art. 61 (23°) L.I.`)
* **Déplacement d'ancrage (`111 al. 2`) :** Une notification technologique faite **après 17 h 00**, un samedi ou un jour férié est réputée faite à **8 h 00 le jour ouvrable suivant** (le compte part donc du jour ouvrable suivant).
* **Déplacement du dépôt (`107 al. 4–5`) :** Un dépôt technologique hors heures d'ouverture du greffe est réputé déposé à la prochaine ouverture; acte reçu seulement avec paiement des droits (`107 al. 5`). Recommander le dépôt pendant les heures d'ouverture du dernier jour.
* **Compte (`83`) :** Le jour de départ ne compte pas, celui d'échéance compte (expire à 24 h 00). En **mois** : même quantième dans le dernier mois, sinon dernier jour du mois (ex. 31 janv. + 1 mois → 28/29 fév.).
* **Report (`83 al. 3`, `82 al. 1`, `61 (23°)`) :** Si l'échéance tombe un samedi, dimanche, férié québécois, **26 décembre** ou **2 janvier**, report au **premier jour ouvrable suivant** (en cascade si plusieurs jours suivent, ex. Noël 25 + 26 + dimanche → 28 déc.). En calcul **à rebours** (ex. `250 al. 1`), devancer au jour ouvrable précédent pour préserver le délai minimal.

### 2. Outillage déterministe obligatoire (jamais de compte mental)
Appeler `outils.calendrier_deadlines` (et `outils.calendrier_holidays` pour vérifier une année) ou, hors ligne sur poste local, exécuter `python scripts/calcul_delai.py <AAAA-MM-JJ> (--jours <N> | --mois <M>) [--a-rebours] [--technologique --heure HH:MM] [--fete-additionnelle AAAA-MM-JJ] --json` *(depuis le dossier de `gestion-du-mandat` ; si `outils` échoue et Python est absent en nuage, **s'arrêter sur le calcul** sans compter mentalement)*. Vérifier les directives de pratique C.S./C.Q. via `lois` (`qccs-dist-mtl` — `preseance-sur` `qccs-div-mtl` —, `qccs-div-qc`, `qccq-regles-simplifiees`, `qccq-mtl-prat-civile`, `qccq-mtl-prat-admin`, `qccq-daa-jurisprudence`, `fr`-only) et vérifier séparément les jours proclamés et directives de la Cour d'appel (absentes de la Vague 1).

### 3. Statuts et maillons clés C.p.c.
* **Statuts (`84, 150, 173, 177, 373`) :** **Rigueur** (`173`, `347 al. 3`, `363 al. 1` — prolongation uniquement si impossibilité **en fait** d'agir plus tôt); **Ordinaire** (`107 al. 3` péremption, `373` caducité d'appel à prolonger *avant* expiration); **Conventionnel** (`150 al. 2`) et **Judiciaire** (de rigueur si prolongation mise en état `173 al. 2`; motif impérieux après `177 al. 2`).
* **Instance ordinaire :** Signification `3 mois` (`107 al. 3`); Réponse `15 j` (`145`) ou **`30 j` hors Québec** (`490`); Protocole `45 j` / `3 mois` famille (`149 al. 2`) ou hors Québec (`490`); Présomption protocole `20 j` (`150`); Mise en état **de rigueur** `6 mois` / `1 an` famille (`173`); Demande écrite en cours d'instance `>= 3 j` avant présentation (`101 al. 1`, sous réserve des délais particuliers : `527` `5 j`, `166 al. 2` `10 j`, `308 al. 2` `10 j à 2 mois`, `530` `15 j`, `377` / `c-25.01-r.0.2.01` `10` / `5` / `2 jours ouvrables`, `510 al. 2` injonction provisoire `<= 10 j`); Opposition modification `10 j` (`207`); Préavis défaut `1 mois` P.G. (`180 al. 1`) / `5 j` instruction (`180 al. 2`).
* **Régime simplifié C.Q. (`< 100 000 $`) :** Aucun protocole (`535.2`). Depuis signification avis d'assignation : `20 j` pièces demandeur (`535.4`) → `45 j` moyens préliminaires (`535.5`, réplique `10 j`) → `95 j` exposé sommaire défense (`535.6`) → `110 j` conférence gestion (`535.8`) → `130–160 j` CRA (`535.12`) → `6 mois` max inscription (`535.13`).
* **Preuve & appel :** Interrogatoire oral `5 j` avant (`226`); réponse écrit `15 j–1 mois` (`223`); objection suspensive `5 j` (`228 al. 2`); communication `30 j` fixation (`248`); production greffe **à rebours** `15 j` ou `3 j` (`250`); rejet rapport expert `10 j` (`241`); mise en demeure nouvel avocat `10 j` (`192`); révision frais `10 j` (`344`); rétractation **de rigueur** `30 j` / max `6 mois` (`347`); appel **de rigueur** `30 j` (`360/363`, ou `10 j`/`5 j` `361`); mémoire appelant `3 mois` (`373`), intimé `+2 mois`.

### 4. Format du tableau livré
`| Date effective | Compte visible (ancrage → brut → report) | Ce qui doit être fait | Article | Statut | Conséquence du dépassement |`
Marquer les dates passées et poser `[DATE À CONFIRMER]` si l'ancrage manque.

## Silences et paires confondables

1. **Non-siège (`82 al. 2`) :** `30 juin au 1er septembre` et `20 décembre au 7 janvier` **ne suspendent aucun délai**. L'énoncer en toutes lettres si une échéance y tombe.
2. **30 septembre et 24/31 décembre :** Le `30 septembre` (férié fédéral) n'est **pas** férié au C.p.c. (`i-16 art. 61 (23°)`, `82 C.p.c.`). Les `24` et `31 décembre` ne sont pas fériés non plus.
3. **Ancrages d'appel trompeurs :** Jugement rendu à l'audience → jour même; jugement rectifié sur le dispositif (`338 al. 3`) → rectification; scission (`211 al. 2`) → avis du jugement final.
4. **Confusion `101 al. 1` (`3 j`) vs délais particuliers (`5 j` `527`, `10 j` `166 al. 2`, `15 j` `530`) :** Ne jamais attribuer `5 jours` à l'art. `101 C.p.c.`.
5. **Prescription substantielle (`2875–2933 C.c.Q.`) :** Hors C.p.c. — renvoyer à `recherche-juridique`.
