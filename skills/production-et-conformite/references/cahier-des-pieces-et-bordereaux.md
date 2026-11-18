# Bordereaux de pièces (`145, 174, 247, 250 C.p.c.`) et cahier des pièces

Dresse les listes et bordereaux formels exigés par le C.p.c., applique le contrôle préalable de privilège/caviardage et coordonne la confection du cahier des pièces pour la communication et l'instruction.

## Règles applicables

**Préalable protection et caviardage (`art. 11, 12, 16, 108 C.p.c.`; `Loi 25 p-39.1`) :** **Ne jamais inscrire à un bordereau externe une pièce non vérifiée quant au privilège et au caviardage.** Si les pièces n'ont pas encore été analysées sur ce plan, contrôler d'abord via `lois` (`cpc` `11, 12, 16, 108`, `p-39.1`) : signaler NAS, comptes bancaires, dossiers médicaux/psychosociaux, mineurs/victimes, secrets commerciaux (`12 C.p.c.`) et tout indice de renonciation au secret ou au privilège de règlement.

**Les trois bordereaux du C.p.c. (`law="cpc"` : `145, 170, 174, 246, 247, 248, 250, 262, 535.4, 535.6`) :** préciser dès l'en-tête quel bordereau est dressé :
1. **Indication / liste jointe à l'acte (`145 al. 1`, `247`) :** Pièces invoquées au soutien de la demande ou de l'acte (puis communiquées dans les plus brefs délais ou selon le protocole `246`, ou dans les `20 jours` en régime simplifié `535.4` / `95 jours` en défense `535.6`).
2. **Inventaire de la déclaration de mise en état (`174 al. 1 (2°)`) :** Pièces et éléments de preuve effectivement communiqués aux autres parties (`248` : sanction d'exclusion sauf autorisation du tribunal).
3. **Production au greffe pour l'instruction (`250`) :** Au moins `15 jours` avant l'instruction (`3 jours` si fixée à `< 15 jours` — calcul à rebours à faire chiffrer via `gestion-du-mandat`).

* **Gabarit du bordereau (`en liasse` = *filed jointly* en anglais) :**
  `| Cote | Désignation précise (nature, parties, objet) | Date propre | Forme (original, copie, doc. tech., en liasse) | Communiquée (oui/non, date, mode) | Produite | Observations / caviardage |`

## Contrôles automatisés

1. Exécuter `python scripts/verifier_cotes.py --acte <acte> --bordereau <bordereau> [--matrice <matrice>] [--modifie] --json` pour vérifier la continuité des cotes (`P-1..P-n`, `P-01..P-n`, `D-1..D-n`, `R-1..R-n`, `I-`, `A-`, `MC-`), le gel des cotes retirées (`206–208`) et la concordance exacte avec l'acte.
2. Exécuter `python scripts/controler_document.py <cahier_pieces.pdf> --exiger-couche-texte --exiger-signets --json` sur le cahier PDF assemblé.

## Contrôles humains

* **Préfixes et bordereaux modifiés :** Respecter le préfixe approprié (`P-` en demande, `D-` ou codéfendeur identifié par initiales ex. `DA-` en défense — contrôlable via `verifier_cotes.py --prefixe DA`, `R-` pour requérant notamment en appel du TAL `500-80`, `I-` intervention, `A-` appel en garantie, `MC-` mise en cause) ; dans un *Bordereau des pièces modifié*, mettre en évidence les nouvelles pièces en **gras et souligné** et conserver les cotes retranchées avec la mention `[Pièce P-X retirée]`.
* **Désignation précise et date propre :** Éviter les libellés vagues (« Document », « Facture »); indiquer date propre, auteur, destinataire et mention `en liasse` datée le cas échéant.
* **Caviardage effectif et aplati (`108 C.p.c.`) :** Contrôler manuellement relevés bancaires, numéros de compte/transit sur spécimens de chèque ou autorisations de paiement, numéros de carte de crédit, NAS, en-têtes `Cci:` / `Bcc:`, dossiers médicaux ou secrets commerciaux protégés, maintenir l'anonymisation par initiales (ex. `A. B.`) lorsque requise, et confirmer l'aplatissement irréversible.
* **Disponibilité de l'original (`2860 C.c.Q.`, `250 C.p.c.`)** pour l'instruction si seule une copie circule.

## Bon de travail

Émettre le bon de travail pour l'assemblage du cahier des pièces dans les outils du cabinet : ordre continu des cotes, insertion des pages intercalaires ou timbrage visible de chaque cote (`PIÈCE P-1`, `PIÈCE P-2`), aplatissement des caviardages (`108 C.p.c.`), normalisation US Letter et OCR sur chaque pièce numérisée, création des signets par cote et préparation de l'endos paysage (`controle-endos-depot-signification.md`).
