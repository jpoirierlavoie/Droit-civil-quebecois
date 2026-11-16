# Échéanciers et computation des délais en procédure civile (C.p.c.)

Gouverne les délais de l'instance civile (ordinaire, Cour du Québec art. 535.1 s., appel) et leur qualification. **La prescription substantielle (art. 2875–2933 C.c.Q.) n'est pas ici : elle relève de `recherche-juridique`.**

## 1. Principes de computation (`art. 82–84, 107, 111 C.p.c.`, `art. 61 (23°) L.I.`)

Lire via `lois.get_articles(law="cpc", numbers=["82", "83", "84", "107", "111"])` et `law="i-16", numbers=["61"]` avant tout tableau formel.

* **Déplacement d'ancrage (`111 al. 2`) :** Une notification technologique faite **après 17 h 00**, un samedi ou un jour férié est réputée faite à **8 h 00 le jour ouvrable suivant** (le compte part donc du jour ouvrable suivant).
* **Déplacement du dépôt (`107 al. 4–5`) :** Un dépôt technologique hors heures d'ouverture du greffe est réputé déposé à la prochaine ouverture; acte reçu seulement avec paiement des droits (`107 al. 5`). Recommander le dépôt pendant les heures d'ouverture du dernier jour.
* **Compte (`83`) :** Le jour de départ ne compte pas, celui d'échéance compte (expire à 24 h 00). En **mois** : même quantième dans le dernier mois, sinon dernier jour du mois (ex. 31 janv. + 1 mois → 28/29 fév.).
* **Report (`83 al. 3`, `82 al. 1`, `61 (23°)`) :** Si l'échéance tombe un samedi, dimanche, férié québécois, **26 décembre** ou **2 janvier**, report au **premier jour ouvrable suivant** (en cascade si plusieurs jours suivent, ex. Noël 25 + 26 + dimanche → 28 déc.). En calcul **à rebours** (ex. `250 al. 1` : au moins 15 jours *avant* l'instruction), devancer au jour ouvrable précédent pour préserver le délai minimal.
* **Trois pièges critiques :**
  1. **Non-siège (`82 al. 2`) :** `30 juin au 1er septembre` et `20 décembre au 7 janvier` **ne suspendent aucun délai**. Énoncer cette règle en toutes lettres si une échéance y tombe.
  2. **30 septembre et 24/31 décembre :** Le 30 septembre (férié fédéral) n'est **pas** férié au C.p.c. (`i-16 art. 61 (23°)`, `82 C.p.c.`).
  3. **Ancrages d'appel trompeurs :** Jugement rendu à l'audience → jour même; jugement rectifié sur le dispositif (`338 al. 3`) → rectification; scission (`211 al. 2`) → avis du jugement final.

## 2. Outillage déterministe obligatoire (jamais de compte mental)

Appeler `outils.calendrier_deadlines` (et `outils.calendrier_holidays` pour vérifier une année) ou, hors ligne, exécuter `python skills/administration-litige/scripts/calcul_delai.py <AAAA-MM-JJ> --jours <N> [--mois <M>] [--rebours] [--technologique --heure HH:MM] --json`. Vérifier séparément les jours proclamés et directives de greffe.

## 3. Vecteurs d'articles C.p.c. (`law="cpc"`) et qualification des statuts

**Statuts (`84`, `150`, `173`, `177`, `373`) :**
* **Rigueur** (`173`, `347 al. 3`, `363 al. 1`) : prolongation uniquement si impossibilité **en fait** d'agir plus tôt.
* **Ordinaire** (tout autre délai du Code, dont `107 al. 3` péremption et `373` caducité d'appel à prolonger *avant* expiration) : prolongation/abrègement possible (`84`).
* **Conventionnel** (protocole `150 al. 2`) et **Judiciaire** (fixé par le juge — **de rigueur** si prolongation de mise en état `173 al. 2`; motif impérieux après `177 al. 2`).

| Régime / Phase | Vecteur `cpc` à charger via `lois.get_articles` | Maillons clés à contrôler |
|---|---|---|
| **Instance ordinaire (C.S. / C.Q.)** | `["101", "107", "145", "148", "149", "150", "152", "166", "168", "170", "173", "174", "175", "177", "178", "186", "188", "207"]` | Signification `3 mois` (107 al. 3 péremption); Réponse `15 j` (145); Protocole `45 j` / `3 mois` famille (149 al. 2); Présomption protocole `20 j` (150); Mise en état **de rigueur** `6 mois` / `1 an` famille (173); Moyens préliminaires `3 j` ou `10 j` irrecevabilité (166); Opposition à modification `10 j` (207). |
| **Régime simplifié C.Q. (`< 100 000 $`)** | `["535.1", "535.2", "535.4", "535.5", "535.6", "535.7", "535.8", "535.12", "535.13"]` | Aucun protocole (`535.2`). Depuis signification de l'avis d'assignation : `20 j` pièces demandeur (`535.4`) → `45 j` moyens préliminaires (`535.5`, réplique `10 j`) → `95 j` exposé sommaire défense (`535.6`) → `110 j` conférence gestion (`535.8`) → `130–160 j` CRA (`535.12`) → `6 mois` max inscription (`535.13`). |
| **Preuve & interrogatoires** | `["223", "226", "228", "241", "243", "246", "248", "250", "262", "269", "293"]` | Interrogatoire oral `5 j` avant (`226`); réponse écrit `15 j–1 mois` (`223`); objection suspensive `5 j` (`228 al. 2`); communication `30 j` fixation (`248`); production greffe **à rebours** `15 j` ou `3 j` (`250`); contestation pièce avant inscription (`262`); rejet rapport expert `10 j` (`241`). |
| **Incidents, rétractation, appel & exécution** | `["192", "194", "324", "338", "344", "347", "349", "355", "357", "358", "360", "361", "363", "365", "372", "373", "374", "376", "510", "521", "522", "656", "661"]` | Mise en demeure nouvel avocat `10 j` (`192`); révision frais `10 j` (`344`); rétractation **de rigueur** `30 j` / max `6 mois` (`347`); appel **de rigueur** `30 j` (`360/363`, ou `10 j`/`5 j` `361`); mémoire appelant `3 mois` (`373`, prolongation *avant* expiration); intimé `+2 mois`. Lire aussi `c-25.01-r.0.2.01`, `r.0.2.1` et `r.9`. |

## 4. Format du tableau livré

`| Date effective | Compte visible (ancrage → brut → report) | Ce qui doit être fait | Article | Statut | Conséquence du dépassement |`
Marquer les dates passées et mettre un crochet `[DATE À CONFIRMER]` si l'ancrage manque.
