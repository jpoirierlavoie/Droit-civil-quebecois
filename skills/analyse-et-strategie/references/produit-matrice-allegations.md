# Registre maître du dossier et matrice de concordance (`Procédure ↔ Preuve ↔ Interrogatoire`)

Référentiel interne de travail (non destiné au tribunal) regroupant l'**inventaire par onglets du dossier** (acteurs/témoins, correspondance, courriels, pièces cotées et documents en réserve, interrogatoires/engagements) et la **matrice de concordance intégrale** reliant actes de procédure, preuve et interrogatoires préalables.

## Finalité

Assurer tout au long du dossier — de la réception des pièces jusqu'à la mise en état — un repérage rapide de chaque document ou échange, aligner paragraphe par paragraphe la demande, la défense (`admis`, `nié`, `ignoré`), les pièces et les interrogatoires/engagements, repérer immédiatement les **allégations orphelines** ou lacunes de fardeau (`2803 C.c.Q.`), et vérifier l'intégrité continue des cotes avant toute communication ou production (`145, 170, 174, 247, 250 C.p.c.`).

## Gabarit

Document **strictement interne** (couvert par le secret professionnel et le privilège relatif au litige — **ne se dépose jamais au greffe et ne se communique pas à l'adversaire**) organisé en trois volets :

### A. Registre maître interne à onglets (inventaire de référence rapide du dossier)
Structurer un classeur interne à onglets (ou index Markdown à identifiants stables) couvrant **toutes** les sources du dossier, y compris celles qui ne sont pas (ou pas encore) destinées à l'instruction :
1. **Onglet 1 — Index des acteurs et témoins (`TEM-01..`) :** `| ID | Nom complet | Organisation & Rôle | Coordonnées | Représenté ? (b-1-r.3.1 art. 120) | Faits connus personnellement | Pièces / Courriels / Interro. liés |`
2. **Onglet 2 — Registre de la correspondance et des courriels (`CORR-001..`) :** `| ID | Date & heure propres | Type (Lettre / Mise en demeure / Courriel .eml / Texto) | Expéditeur → Destinataires (Cc / Bcc) | Résumé factuel neutre (1 ligne) | Pièces jointes | Statut (Coté P-X/D-X · En réserve non coté · Privilégié / Règlement) |`
3. **Onglet 3 — Inventaire des pièces cotées et documents en réserve (`DOC-001..`) :** `| ID | Cote officielle (P-X / D-X / En réserve non coté / [Pièce P-X retirée]) | Date propre | Nature & Auteur | SHA-256 court (journal de garde) | Protection / Caviardage (108 C.p.c., Loi 25) | Par. d'actes rattachés |`
4. **Onglet 4 — Registre des interrogatoires, engagements et admissions (`INT-01..` / `E-1..`) :** `| Réf. | Personne interrogée & Date | Extrait clé / Aveu (2852 C.c.Q.) (Page : Ligne) | Engagement (E-1..E-n) ou Objection (228 al. 2 vs al. 3) | Échéance & Statut (Reçu / En suspens) | Pièce reçue / Impact |`

### B. Matrice de concordance intégrale (`Demande ↔ Défense ↔ Preuve ↔ Interrogatoire ↔ Témoin`)

`| Par. Demande | Fait allégué / Élément constitutif | Position en Défense (Par. — Admis / Nié / Ignoré / S'en rapporte 170 al. 4) | Pièce cotée ou réf. interne (P-X / D-X / CORR-X / DOC-X) | Interrogatoire / Engagement (p.:l., E-X) | Témoin / Fardeau (2803 C.c.Q.) | Statut & Lacune / Action |`

* **Croisement Demande ↔ Défense (`170 C.p.c.`, `2803, 2851–2852 C.c.Q.`) :** Cartographier chaque paragraphe pour isoler ce qui est expressément admis (`2852 al. 1`), nié ou ignoré (sans présumer que le silence en défense équivaut toujours à une dénégation ni qu'il dispense de prouver positivement les faits constitutifs de la demande ; noter que s'en rapporter à la justice sous `170 al. 4 C.p.c.` ne vaut ni contestation ni acquiescement). Mettre en relief toute **allégation orpheline** dépourvue de pièce ou de témoin.

### C. Cinq anomalies de cotes à auditer systématiquement sur tout acte + bordereau
1. **Saut de numéro :** ex. `P-1, P-2, P-4` sans `P-3` (rappel : en acte modifié `206–208 C.p.c.`, une pièce retirée garde sa place gelée `[Pièce P-3 retirée]`).
2. **Invocation sans cote :** l'acte mentionne « le contrat du 4 mars » sans cote en gras `**Pièce P-X**`.
3. **Cote orpheline :** la liste porte `P-7` mais aucun paragraphe de l'acte ne l'invoque (ou le fichier manque).
4. **Ordre de première invocation inversé :** `P-5` invoquée au par. 8 avant `P-4` au par. 11 (les cotes suivent l'ordre continu de première invocation).
5. **Doublon :** même document coté deux fois, ou documents hétérogènes groupés sans mention `en liasse` datée.

*(Outillage : exécuter `verifier_cotes.py` de `production-et-conformite` sur l'acte, le bordereau et la matrice pour automatiser l'audit ; sur surface nuage sans Python local, divulguer explicitement que la vérification scriptée des cotes a été omise et l'inscrire au bon de travail manuel.)*

## Statut des faits

Chaque ligne indique explicitement si le fait repose sur un élément `Établi` (pièce probante vérifiée ou aveu judiciaire `2852 al. 1 C.c.Q.`), `Rapporté` (récit client ou témoignage à administrer), `Déduit` ou `[À CONFIRMER]` (allégation orpheline ou lacune à combler par pièce en réserve, engagement `E-n` ou admission).

## Mise à jour

Alimenter les onglets du registre maître dès chaque arrivée de documents ou de courriels, après la défense, après toute modification d'acte (`206–208 C.p.c.`), à la réception des transcriptions et réponses d'engagements (`221, 227 C.p.c.`), puis lors de la déclaration commune de mise en état (`174 C.p.c.`) et de la production au greffe (`250 C.p.c.`).
