# Contrats civils et commerciaux (style civiliste et ordre public C.c.Q.)

[NON VALIDÉ PAR LA PRATIQUE]

Encadre la rédaction et la révision de contrats civils et commerciaux soumis au droit du Québec dans le respect du style civiliste et des dispositions impératives du C.c.Q.

## Objet et destinataire

* **Identification :** Vérifier la dénomination exacte, le NEQ et la chaîne corporative via `outils.registre_search`/`registre_get_entity` (`lei` / `portails_officiels` `req`, `corporations_canada`, `isc_pisc` ; la consolidation comptable GLEIF `REGISTRE_GLEIF_DECLARATIF_CONSOLIDATION` n'établit ni contrôle juridique ni pouvoir de signature — confirmer au REQ avant signature) et l'adresse civique ou les lots indicatifs via `outils.adresse_verify` (vérifier au Registre foncier avant toute clause immobilière, art. `3030 al. 2, 3032 C.c.Q.`).
* **Vecteur `law="ccq"` à lire via `lois.get_articles` :** `numbers=["1379", "1385", "1432", "1434", "1435", "1436", "1437", "1438", "1474", "1561", "1604", "1605", "1606", "1620", "1621", "1622", "1733", "1942", "1955", "3030", "3032", "3148", "3161"]`.

## Mentions obligatoires

* Parties exactement désignées et représentées;
* Objet déterminé ou déterminable (`1373 C.c.Q.`);
* Nature exacte des engagements (**obligation de moyens** vs **obligation de résultat** — jamais l'anglicisme flou « meilleurs efforts »);
* En contrat d'adhésion (`1379`) : mise en évidence des clauses externes (`1435`), lisibilité (`1436`) et équilibre au regard de `1437 C.c.Q.`.
* **Clauses financières, d'indexation et de devises (déterminisme) :**
  * *Indexation IPC (`outils.indice_ipc`) :* stipuler explicitement territoire (`quebec`/`montreal_rmr`/`canada`), composante (`all_items`/`shelter`), année de base (`2002=100`, ne jamais mélanger avec `1992=100` sans facteur StatCan), période de référence, plancher/plafond (`floor_bps`/`cap_bps`) et règle d'arrondi (`half_away_from_zero`/`half_up`) — **rappel d'ordre public :** l'indexation automatique à l'IPC est inopérante en bail résidentiel (`1942 C.c.Q.` et `RLRQ, c. T-15.01, r. 2`, `outils.loyer_tal`) ;
  * *Taux préférentiel + marge (`outils.interets_1619`, `V80691311`) :* nommer la banque prêteuse, la date de prise d'effet des variations, le plancher éventuel, la convention de décompte de jours et préciser si intérêt simple (`1620 C.c.Q.`) ou composé ;
  * *Conversion de devises (`outils.taux_boc_rates`) :* viser la moyenne quotidienne de 16 h 30 HE de la Banque du Canada (`post-2017-05-01`) et la règle de report au jour ouvrable précédent (`art. 12 Loi sur la monnaie`, `1561, 3161 C.c.Q.`).

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
2. Vérifier dénomination, NEQ/LEI (`portails_officiels`) et adresse/lots (`lot_source`) via `outils.registre_search` / `registre_get_entity` / `adresse_verify` ; valider calculs d'indexation, intérêts ou taux via `outils.indice_ipc` / `interets_1619` / `taux_boc_rates` / `loyer_tal`.
3. Vérifier la cohérence interne (définitions utilisées, renvois d'articles, obligation de moyens vs de résultat).
4. Exécuter `outils.terminologie_scan`.
