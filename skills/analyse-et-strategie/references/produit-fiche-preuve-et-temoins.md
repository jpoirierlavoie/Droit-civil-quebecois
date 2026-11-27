# Fiche de preuve, répertoire des témoins et cahier de procès

Organise le répertoire interne des témoins, leurs fiches de preuve individuelles croisées au registre maître du dossier (`produit-matrice-allegations.md`), l'alignement avec les formulaires officiels de mise en état (`174 C.p.c.`) et l'architecture du **cahier de procès** personnel du plaideur.

## Finalité

Structurer en interne la preuve testimoniale et d'expertise en vérifiant les vecteurs `lois.get_articles(law="ccq", numbers=["2803", "2843", "2862", "2863", "2865", "2869", "2870"])`, `law="cpc", numbers=["139", "174", "250", "269", "270", "273", "292", "293", "535.14"]` et `law="b-1-r.3.1", numbers=["120", "122", "123"]` :
* Relier chaque témoin (ordinaire ou expert) aux faits dont il a une **connaissance personnelle directe** (`2843 C.c.Q.`, en anticipant le ouï-dire `2869–2870` et la prohibition de contredire par témoignage un écrit valablement fait `2862–2863 C.c.Q.`), ainsi qu'aux pièces à authentifier ou commenter (`250 C.p.c.`) et aux extraits d'interrogatoire ;
* Préparer en amont les renseignements requis par les formulaires officiels de **mise en état (`174(3°) et (6°) C.p.c.`)** : identité et qualité des témoins, objet de chaque déposition, mode retenu (témoignage oral, déclaration écrite sur fait secondaire `292 C.p.c.`, déclaration `<= 5 pages` en procédure simplifiée C.Q. `535.14 C.p.c.`, ou rapport d'expertise tenant lieu de témoignage `293 C.p.c.`) et temps estimé ;
* Respecter les garde-fous déontologiques lors des entrevues préparatoires (`b-1-r.3.1 art. 120, 122, 123` : ne pas communiquer avec une personne représentée sans consentement ; déclarer ses intérêts au témoin non représenté ; aucune compensation conditionnelle au témoignage) et anticiper les citations par huissier avec avance réglementaire (`139(1°), 269, 270 al. 2, 273 C.p.c.`, min. `10 jours` avant comparution).

## Gabarit

Outil **strictement interne** : si la liste des témoins et le mode de déposition doivent être déclarés à la mise en état (`174(3°) C.p.c.`, sauf motifs valables), **les notes d'entrevue, déclarations préparatoires, fiches d'examen et le cahier de procès demeurent protégés par le privilège relatif au litige et le secret professionnel** et ne sont jamais communiqués d'office.

1. **Répertoire des témoins (arrimé au registre maître et au formulaire de mise en état `174 C.p.c.`) :**

| ID (`TEM-X`) & Nom | Qualité (Partie / Ordinaire / Expert) | Objet de la déposition & faits ciblés (par. actes) | Pièces à authentifier ou commenter (`250 C.p.c.` / `CORR-X`) | Interro. préalable / Engagements (`p.:l.`, `E-X`) | Mode (`Oral` / `292` / `535.14` / `Rapport 293`) & Temps estimé | Citation (`139(1°), 269, 273`) & Points de vigilance |
|---|---|---|---|---|---|---|
| [`TEM-01` — Nom] | [Ordinaire / Expert] | [par. 12–15] | [`P-3`, `P-8`] | [`INT-01 p. 24:8`, `E-2`] | [Oral — chef 30 min / contre 20 min] | [Signification `>= 10 j` + avance ; ouï-dire / lien d'emploi] |

2. **Fiche de preuve et d'entrevue par témoin (interrogatoire principal ou contre-interrogatoire) :**

| Ordre | Thème / Fait visé | Connaissance directe ou point à confronter | Pièce / Courriel lié (`P-X`, `D-X`, `CORR-X`) | Passage antérieur (`p.:l.` interro. / déclaration) | Règle de preuve / Risque (`2843, 2863 C.c.Q.`) |
|---|---|---|---|---|---|
| 1 | [Fait clé] | [Constat personnel / contradiction à relever] | [`P-3`] | [`p. X, l. Y`] | [Origine de l'écrit ; éviter le ouï-dire] |

3. **Cahier de procès (cartable personnel et confidentiel du plaideur) :**
   * Regroupe pour l'usage exclusif de l'avocat — selon ses préférences et la complexité du dossier — le plan de plaidoirie, la frise chronologique (`produit-chronologie.md`), la matrice de concordance (`produit-matrice-allegations.md`), les fiches par témoin, les extraits ciblés de jurisprudence annotés et l'aide-mémoire d'objections.
   * **Étanchéité stricte :** Ce cahier interne **ne se dépose jamais au greffe et ne se communique pas à l'adversaire** (ne jamais le confondre avec le *Cahier des procédures*, qui n'est que le reflet public du plumitif remis au tribunal).

## Statut des faits

Distinguer ce dont le témoin a une **connaissance personnelle directe** (`Établi` / témoignage direct recevable) des propos **rapportés** d'un tiers (`Rapporté` — risque d'objection de ouï-dire sous `2843 C.c.Q.`), des déductions (`Déduit`) et des points restant à vérifier en entrevue préparatoire (`[À CONFIRMER]`).

## Mise à jour

Actualiser au fil des entrevues de témoins et de la réception de nouveaux documents, à la clôture des interrogatoires préalables et des engagements, puis lors de la préparation de la déclaration commune de mise en état (`174 C.p.c.`) et de la vérification du bordereau des pièces (`250 C.p.c.`).
