# Contrôle formel et concordance d'un acte de procédure

Vérifie la conformité matérielle, la pagination, la typographie et l'intégrité des cotes d'un acte de procédure avant signification ou dépôt, et génère un bon de travail exact pour les outils du cabinet.

## Règles applicables

**Ne jamais coder de seuils de cour en dur : lire d'abord le texte applicable via `lois.get_articles` et `lois.get_structure` :**
* `law="cpc"` : `numbers=["99", "100", "101", "105", "107", "145", "206", "207", "208", "247", "535.3", "535.6"]`;
* **Cour supérieure (`law="c-25.01-r.0.2.1"`) :** `art. 3` (format papier `21,25 × 28 cm` / `8,5 × 11 po`, recto seulement, mentions complètes d'endos incluant courriel de notification et code informatique d'avocat) et `art. 11` (mise en évidence des ajouts par soulignement ou trait vertical en marge et des retraits par `(…)`), complétés par les *Directives de pratique* du corpus Vague 1 (`fonction='directive'`, `unit='paragraphe'`, `par.`/`dir.`, `fr`-only : `qccs-dist-mtl` qui a `rel_type='preseance-sur'` `qccs-div-mtl`, et `qccs-div-qc`, avec `links` sur les annexes `ps:*` — toujours vérifier police Arial 12, interligne, marges et plafonds de pages locaux) ;
* **Cour du Québec (`law="c-25.01-r.9"`) :** `art. 9` (format lettre `21,5 × 28 cm`, un seul côté, Arial 12), `art. 10` (mentions d'endos dont le montant en litige), `art. 38, 47, 78`, plafonds légaux (`535.3`, `535.6 C.p.c.`) et directives Vague 1 (`qccq-regles-simplifiees`, `qccq-mtl-prat-civile`, `qccq-mtl-prat-admin`, `qccq-daa-jurisprudence`, `fonction='directive'`, `fr`-only) ;
* **Cour d'appel (`law="c-25.01-r.0.2.01"`) :** `art. 24` et `51` (format lettre, marges `>= 2,5 cm`, Arial 12 corps / Arial 11 citations à simple interligne / Arial 10 notes, interligne `>= 1,5`). Les directives C.A.Q. (`QCCA`) sont absentes du corpus (`134` textes) et doivent être vérifiées séparément à la source.

## Contrôles automatisés

1. **Contrôle formel du `.docx` ou `.pdf` (`scripts/controler_document.py`) :**
   Exécuter `python scripts/controler_document.py <acte.docx|pdf> [--regles <regles.json>] [--max-pages N] [--police-attendue "..."] [--taille-min-pt X] [--marge-min-po Y] [--interligne-min Z] --json` avec les seuils lus via `lois` pour vérifier :
   * le nombre de pages déclaré (`docProps/app.xml` ou `/Type /Page`), notamment pour `535.3` (`<= 5 pages`) et `535.6` (`<= 2` / `7 pages`);
   * les polices, tailles en points, marges (`>=`), interlignes et format papier US Letter (`8,5 × 11 po`);
   * l'absence de commentaires Word (`word/comments.xml`), de marques de révision (`w:ins`/`w:del`) et de fuite de métadonnées auteur.
2. **Continuité et concordance des cotes (`scripts/verifier_cotes.py`) :**
   Exécuter `python scripts/verifier_cotes.py --acte <acte.docx|md> --bordereau <bordereau> [--matrice <matrice>] [--prefixe D|R|DA] [--modifie] --json` pour détecter sauts de numérotation, ordre de première invocation inversé, invocations sans cote, cotes orphelines et gel des cotes sur acte modifié (`206–208 C.p.c.`). Passer `--prefixe` lorsqu'un acte défendeur/requérant/codéfendeur emploie des cotes distinctes (`D-1..D-n`, `R-1..R-n`, `DA-1..DA-n`, etc.).
3. **Purge linguistique (`outils.terminologie_scan`) :** Exécuter sur le texte de l'acte fini.
4. **Dégradation nuage sans Python (`claude.ai`, Gemini App `/mcp/oauth`, Deep Research) :** Si `controler_document.py` ou `verifier_cotes.py` ne peuvent pas être exécutés localement, **divulguer explicitement** que les contrôles scriptés sur octets, XML Word (`comments.xml`, révisions, polices, marges, `<Pages>`), PDF (couche texte OCR, signets, `/Encrypt`) et continuité automatisée des cotes ont été **omis**, puis inscrire ces vérifications en tête du bon de travail.

## Contrôles humains

* **Adéquation conclusions ↔ allégations :** Chaque conclusion (`CONDAMNER`, `DÉCLARER`, `ORDONNER`) s'appuie sur des faits expressément allégués au corps de l'acte (`99 C.p.c.`).
* **Caviardage et secret (`108, 12, 16 C.p.c.`):** Vérifier qu'aucun NAS, numéro de compte bancaire/carte de crédit ou renseignement protégé non autorisé n'apparaît dans l'acte ou le bordereau.
* **Défauts formels fréquents issus de gabarits réutilisés :** Vérifier l'intitulé du tribunal (`COUR DU QUÉBEC`, jamais `COUR DE QUÉBEC` ; `Chambre civile`, jamais `Chambre civil`), la graphie exacte `cote` (sans accent circonflexe) et l'anglais canadien (`Defence`, jamais `Defense`), les parenthèses `(ci-après, …)` en minuscules sans point-virgule parasite, l'accord singulier/pluriel (`par son avocat` c. `par leurs avocats`), la formule exacte `POUR CES MOTIFS, PLAISE AU TRIBUNAL :`, la continuité des paragraphes (aucun doublon `8., 8.`), l'absence de chiffre tronqué dans le numéro de dossier en pied de page, les cotes de codéfendeurs (`DA-1..DA-n`, etc.) sans collision avec `P-`, l'absence totale de note interne d'audience dans un plan remis au juge, la concordance de date entre `.docx` et `.pdf`, le retrait de toute mention `PROJET`, et la parité langue/tribunal/adresse entre corps et endos (zéro bascule FR/EN en milieu de document).
* **Pagination visuelle réelle dans Word :** Lorsqu'un `.docx` ne contient pas `<Pages>` dans `app.xml` ou approche la limite (`535.3`/`535.6`), ouvrir le document dans Word avant export PDF.

## Bon de travail

Présenter systématiquement le résultat sous forme de **bon de travail numéroté** indiquant l'outil du cabinet (`Microsoft Word`, `Adobe Acrobat` / outil PDF) et chaque correction exacte à appliquer avant le dépôt (suppression de commentaires/révisions, ajustement de police/marges/pagination, correction d'une cote inversée, réexport PDF avec OCR) — **en incluant explicitement toute vérification scriptée omise lorsque les scripts Python locaux n'ont pas pu être exécutés**.
