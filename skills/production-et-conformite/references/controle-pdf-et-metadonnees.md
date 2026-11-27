# Contrôle PDF, OCR, signets, liens et fuite de métadonnées

Vérifie la conformité technique des fichiers `.pdf` et `.docx` destinés au greffe numérique ou à la partie adverse et produit un bon de travail exact pour les transformations effectuées dans les outils du cabinet.

## Règles applicables

Lire via `lois` les règles de dépôt technologique et de présentation du tribunal saisi :
* `law="cpc"` : `numbers=["107", "108", "109", "110", "250"]`;
* Règlements et directives applicables : `c-25.01-r.0.2.1` (C.S.), `c-25.01-r.9` (C.Q.), `c-25.01-r.0.2.01` (C.A.Q.) ainsi que les directives C.S./C.Q. Vague 1 (`fonction='directive'`, `fr`-only : `qccs-dist-mtl` avec `rel_type='preseance-sur'` `qccs-div-mtl`, `qccs-div-qc`, `qccq-regles-simplifiees`, `qccq-mtl-prat-civile`, `qccq-mtl-prat-admin`, `qccq-daa-jurisprudence`, incluant `articles.links` sur annexes `ps:*` ; directives C.A.Q. hors corpus à vérifier séparément) quant au format PDF/A ou OCR, signets, hyperliens et taille des fichiers au greffe numérique.

## Contrôles automatisés

Exécuter `python scripts/controler_document.py <fichier.pdf|docx> [--exiger-couche-texte] [--exiger-signets] --json` pour vérifier mécaniquement :
* **Couche texte (OCR) :** détecte l'absence de flux texte (`couche_texte == "absente"`, numérisation pure image);
* **Signets (`/Outlines`) :** détecte la présence ou l'absence de table de signets navigables;
* **Liens et URI (`/Subtype /Link`) :** inventorie les hyperliens internes ou externes présents;
* **Chiffrement (`/Encrypt`) et signatures verrouillées :** détecte tout PDF protégé par mot de passe, signature Adobe Sign verrouillant la modification (attention aussi aux pages *Rapport d'audit* contenant courriels/IP externes annexées automatiquement) ou formulaire XFA dynamique (ex. `SJ-1273`, `SJ-1302`), qui bloquent la fusion de cahiers — prescrire l'aplatissement (`Impression PDF` / réexport aplati) avant assemblage ;
* **Métadonnées et caviardage (`108 C.p.c.`) :** inspecter relevés bancaires, spécimens de chèque et autorisations de paiement (transit/institution/compte), NAS, cartes de crédit et en-têtes `Cci:` / `Bcc:` de courriels avant toute fusion, puis confirmer que les caviardages sont irréversiblement aplatis ;
* **Métadonnées & fuites (`.docx` / `.pdf`) :** relève `Author`, `Creator`, `Producer`, commentaires Word (`word/comments.xml`) et marques de révision (`w:ins` / `w:del`);
* **Format papier (`/MediaBox` / `w:pgSz`) :** accepte le format US Letter **portrait (`8,5 × 11 po`)** et **paysage (`11 × 8,5 po`)** employé pour l'*endos* (*backing*), tout en signalant les pages **A4 (`8,27 × 11,69 po`)** des portails administratifs (ex. reçus TAL), le format **Legal (`8,5 × 14 po`)** des pièces anciennes et les numérisations irrégulières à normaliser en US Letter avant dépôt.
* **Dégradation nuage sans Python (`claude.ai`, Gemini App `/mcp/oauth`, Deep Research) :** lorsque `controler_document.py` ne peut pas s'exécuter localement, **divulguer explicitement** que les vérifications automatisées sur octets, flux PDF (couche texte OCR, `/Outlines`, `/Encrypt`, `/Subtype /Link`, `/MediaBox`) et XML Word (`comments.xml`, révisions, propriétés) ont été **omises**, et les reporter intégralement au bon de travail manuel.

## Contrôles humains

* **Lisibilité et orientation des pages numérisées :** Vérifier qu'aucune page n'est tronquée, floue, à l'envers ou rognée sur les timbres/signatures.
* **Caviardage irréversible (`108 C.p.c.`, Loi 25) :** Confirmer qu'un caviardage a été **aplati** définitivement (jamais un simple rectangle noir posé au-dessus d'une couche texte extractible!).
* **Exactitude des signets et hyperliens :** Vérifier que chaque signet pointe vers la bonne cote (`P-1`, `Onglet 1`) et que les hyperliens CanLII/LégisQuébec fonctionnent.

## Bon de travail

Ne jamais modifier les fichiers binaires en place : produire un **bon de travail structuré** listant dans l'ordre chaque intervention requise dans les outils du cabinet (`Microsoft Word`, `Adobe Acrobat` / outil PDF du cabinet) — **en commençant par toute vérification octets/XML/PDF omise lorsque les scripts Python locaux n'ont pas pu être exécutés** :
1. Purge des commentaires, révisions et métadonnées personnelles avant export PDF;
2. Exécution de l'OCR sur les pièces numérisées;
3. Aplatissement définitif des zones caviardées;
4. Fusion des documents selon l'index et création des signets (`/Outlines`) par onglet/cote;
5. Vérification du poids total avant dépôt au greffe numérique.
