# Matrice de concordance interne (`Allégation ↔ Pièce ↔ Témoin`)

Document interne de travail reliant chaque allégation de la procédure à la preuve disponible et vérifiant l'intégrité des cotes avant communication ou instruction.

## Finalité

Garantir qu'aucune allégation essentielle ne manque d'appui probatoire, qu'aucun témoin n'est oublié et que l'ensemble des cotes de pièces est continu et cohérent avant dépôt ou préparation d'audience.

## Gabarit

Document **strictement interne** (non déposé au greffe) :

`| Par. acte | Fait allégué | Cote | Pièce / Document | Statut (Établi / Rapporté / Absent) | Témoin / Fardeau | Lacune / Action |`

**Cinq anomalies à auditer systématiquement sur tout acte + bordereau :**
1. **Saut de numéro :** ex. `P-1, P-2, P-4` sans `P-3` (rappel : en acte modifié `206–208 C.p.c.`, une pièce retirée garde sa place `[Pièce P-3 retirée]`).
2. **Invocation sans cote :** l'acte mentionne « le contrat du 4 mars » sans cote en gras `**Pièce P-X**`.
3. **Cote orpheline :** la liste porte `P-7` mais aucun paragraphe de l'acte ne l'invoque (ou le fichier manque).
4. **Ordre de première invocation inversé :** `P-5` invoquée au par. 8 avant `P-4` au par. 11 (les cotes suivent la première invocation continue).
5. **Doublon :** même document coté deux fois, ou documents hétérogènes groupés sans mention `en liasse` datée.

*(Outillage : utiliser l'outil `verifier_cotes.py` de `production-et-conformite` sur l'acte, le bordereau et la matrice pour automatiser l'audit.)*

## Statut des faits

Chaque ligne indique si l'allégation repose sur un fait `Établi` (pièce probante disponible et vérifiée), `Rapporté` (témoignage à l'instruction requis), `Déduit` ou `Absent` (`[À CONFIRMER]` — lacune à combler par pièce, engagement ou admission).

## Mise à jour

Actualiser après toute modification d'acte (`206–208`), après réception de pièces ou réponses à des engagements (`221`), et avant l'inventaire de mise en état (`174 C.p.c.`) ainsi que la production au greffe (`250 C.p.c.`).
