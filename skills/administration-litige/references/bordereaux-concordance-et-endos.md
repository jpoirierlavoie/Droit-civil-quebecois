# Bordereaux de pièces, matrice de concordance et endos de cour

Couvre les avis et bordereaux formels du C.p.c., le contrôle interne allégations-pièces-témoins et la confection de l'endos et du dossier de dépôt.

## 1. Préalable protection et caviardage (`art. 11, 12, 16, 108 C.p.c.`; `Loi 25`)

**Ne jamais inscrire à un bordereau externe une pièce non vérifiée quant au privilège et au caviardage.** Si les pièces n'ont pas encore été analysées sur ce plan, contrôler d'abord via `lois` (`cpc` `11, 12, 16, 108`, `p-39.1`) : signaler NAS, comptes bancaires, dossiers médicaux/psychosociaux, mineurs/victimes, secrets commerciaux (`12 C.p.c.`) et tout indice de renonciation au secret ou au privilège de règlement.

## 2. Les trois bordereaux du C.p.c. (`law="cpc"`: `145, 170, 174, 246, 247, 248, 250, 262`)

Préciser dès l'en-tête quel bordereau est dressé, car les exigences changent :
1. **Indication / liste jointe à l'acte (`145 al. 1`, `247`) :** Pièces invoquées au soutien de la demande ou de l'acte (puis communiquées dans les plus brefs délais ou selon le protocole `246`, ou dans les `20 jours` en régime simplifié `535.4` / `95 jours` en défense `535.6`).
2. **Inventaire de la déclaration de mise en état (`174 al. 1 (2°)`) :** Pièces et éléments de preuve effectivement communiqués aux autres parties (`248` : sanction d'exclusion sauf autorisation du tribunal).
3. **Production au greffe pour l'instruction (`250`) :** Au moins `15 jours` avant l'instruction (`3 jours` si fixée à `< 15 jours`).

* **Gabarit du bordereau (`en liasse` = *filed jointly* en anglais) :**
  `| Cote | Désignation précise (nature, parties, objet) | Date propre | Forme (original, copie, doc. tech., en liasse) | Communiquée (oui/non, date, mode) | Produite | Observations / caviardage |`

## 3. Matrice de concordance interne (`Allégation ↔ Pièce ↔ Témoin`) et audit à 5 contrôles

Document **interne de travail** (non déposé au greffe) reliant la procédure à la preuve et contrôlant l'intégrité des cotes :

`| Par. acte | Fait allégué | Cote | Pièce / Document | Statut (Établi / Rapporté / Absent) | Témoin / Fardeau | Lacune / Action |`

**Cinq anomalies à auditer systématiquement sur tout acte + bordereau :**
1. **Saut de numéro :** ex. `P-1, P-2, P-4` sans `P-3` (rappel : en acte modifié `206–208`, une pièce retirée garde sa place `[Pièce P-3 retirée]`).
2. **Invocation sans cote :** l'acte mentionne « le contrat du 4 mars » sans cote en gras `**Pièce P-X**`.
3. **Cote orpheline :** la liste porte `P-7` mais aucun paragraphe de l'acte ne l'invoque (ou le fichier manque).
4. **Ordre de première invocation inversé :** `P-5` invoquée au par. 8 avant `P-4` au par. 11 (les cotes suivent la première invocation continue).
5. **Doublon :** même document coté deux fois, ou documents hétérogènes groupés sans mention `en liasse` datée.

## 4. Endos de cour (backing) et vérification de dépôt

Vérifier les règles de forme et de dépôt du tribunal saisi via `lois` (`c-25.01-r.0.2.1` C.S. art. 3–14, `c-25.01-r.9` C.Q., `c-25.01-r.0.2.01` C.A.Q.) ainsi que les coordonnées du palais via `outils.greffe_parse_number` et `outils.palais_get`/`palais_list`. *(Avertissement obligatoire : les tables MJQ d'adresses datent du relevé local sans n° de téléphone et doivent être revérifiées auprès du Ministère avant signification ou dépôt.)*

* **Structure complète d'un endos québécois :**
  * `N° : [n° dossier de cour]` (ou décomposé via `greffe_parse_number`)
  * `COUR [SUPÉRIEURE / DU QUÉBEC]` · `PROVINCE DE QUÉBEC` · `DISTRICT DE [District]`
  * Parties : `[DEMANDEUR], c. [DÉFENDEUR]`
  * Intitulé exact de l'acte (`DEMANDE INTRODUCTIVE D'INSTANCE`, `BORDEREAU DES PIÈCES`, etc.) — avec mention `COPIE` / `ORIGINAL` et montant en litige le cas échéant
  * Mention `SOUS PLI CACHETÉ — ART. 12 C.P.C.` ou `CONFIDENTIEL — ART. 108 C.P.C.` s'il y a lieu
  * Bloc d'identification du cabinet / procureur(e) : nom, barreau/étude, adresse, courriel de notification (`art. 109–110 C.p.c.`), téléphone, `N/D : [référence interne]`
  * Espace réservé au timbre du greffe ou au procès-verbal de signification
* **Liste de contrôle avant dépôt :** US Letter (`8,5 × 11 po`), pagination vérifiée (`art. 535.3/535.6`), droits de greffe vérifiés (`t-16-r.10`), avis d'assignation (`145`) ou avis de présentation (`101`) joint, copie notifiée aux autres parties/avocats (`107`).
