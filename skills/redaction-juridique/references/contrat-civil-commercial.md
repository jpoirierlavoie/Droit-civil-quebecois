# Contrats civils et commerciaux (style civiliste et ordre public C.c.Q.)

[NON VALIDÉ PAR LA PRATIQUE]

Encadre la rédaction et la révision de contrats civils et commerciaux soumis au droit du Québec dans le respect du style civiliste et des dispositions impératives du C.c.Q.

## Objet et destinataire

* **Identification :** Vérifier la dénomination exacte et le NEQ des personnes morales via `outils.registre_search`/`registre_get_entity` (sans valeur de certificat : confirmer au REQ avant signature) et l'adresse civique via `outils.adresse_verify`.
* **Vecteur `law="ccq"` à lire via `lois.get_articles` :** `numbers=["1379", "1385", "1432", "1434", "1435", "1436", "1437", "1438", "1474", "1604", "1605", "1606", "1621", "1622", "1733", "3148"]`.

## Mentions obligatoires

* Parties exactement désignées et représentées;
* Objet déterminé ou déterminable (`1373 C.c.Q.`);
* Nature exacte des engagements (**obligation de moyens** vs **obligation de résultat** — jamais l'anglicisme flou « meilleurs efforts »);
* En contrat d'adhésion (`1379`) : mise en évidence des clauses externes (`1435`), lisibilité (`1436`) et équilibre au regard de `1437 C.c.Q.`.

## Structure

* **Style civiliste sobre :** Rédiger les obligations au **présent de l'indicatif** (« le Fournisseur livre… » plutôt que *shall*); éviter les définitions pléthoriques et redondances.
* **Règles d'interprétation (`1432 C.c.Q.`) :** L'ambiguïté s'interprète contre le stipulant et toujours en faveur de l'adhérent ou du consommateur.
* **Limites d'ordre public et mécanismes C.c.Q. :**
  * *Résolution vs résiliation (`1604, 1606`)* : restitution rétroactive (résolution) vs cessation pour l'avenir (résiliation); exclue si le défaut est de peu d'importance malgré toute clause contraire;
  * *Limitation de responsabilité (`1474`)* : inopérante pour faute intentionnelle ou lourde (préjudice matériel) et **totalement interdite** pour préjudice corporel ou moral;
  * *Vices cachés (`1733`)* : le vendeur professionnel ne peut s'exonérer à l'aveugle; « tel que vu » limité au vendeur non professionnel;
  * *Clause pénale (`1622`)* : remplace *liquidated damages*, soumise au pouvoir de réduction du tribunal si abusive (`1623`);
  * *Divisibilité (`1438`)* : supplétive par défaut (*severability* mal rédigée nuit souvent).

## Clauses ou formules à proscrire

* **Clause de *consideration* (« moyennant 1,00 $ »)** : le contrat se forme par le seul échange de consentement (`1385 C.c.Q.`).
* **Dommages punitifs contractuels (`1621 C.c.Q.`) :** Impossibles à créer par contrat sans loi habilitante expresse.
* **Doublets de common law et anglicismes :** *null and void*, *terms and conditions*, *indemnify and hold harmless* (→ garantir et prendre fait et cause), *best efforts*, *shall*, *time is of the essence* sans précision des conditions d'exigibilité/demeure (`1594 s.`), clause d'élection de for dans un contrat d'adhésion ou de consommation (`3149 C.c.Q.`, `41 al. 2 C.p.c.`).

## Contrôle

1. Vérifier chaque texte impératif du C.c.Q. (et L.p.c. s'il s'agit d'un contrat de consommation) via `lois`.
2. Vérifier dénomination, NEQ et adresse via `outils.registre_search` / `adresse_verify`.
3. Vérifier la cohérence interne (définitions utilisées, renvois d'articles, obligation de moyens vs de résultat).
4. Exécuter `outils.terminologie_scan`.
