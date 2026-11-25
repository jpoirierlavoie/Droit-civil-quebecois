# Cahier des procédures, cahier de procès et annexes d'appel

[NON VALIDÉ PAR LA PRATIQUE]

Encadre l'assemblage du **cahier de procès** / **cahier d'audience interlocutoire** en première instance (`c-25.01-r.0.2.1`, `c-25.01-r.9`) ainsi que la confection des Annexes I, II et III du mémoire ou de l'exposé d'appel (`370–374 C.p.c.`, `c-25.01-r.0.2.01` `art. 47–58`).

## Règles applicables

* **Cahier de procès / Cahier d'audience de première instance (`c-25.01-r.0.2.1`, `c-25.01-r.9`, directives Vague 1 `qccs-*` / `qccq-*` en `fonction='directive'`, `fr`-only) :** Assembler dans un volume unique (ou par volumes séparés si volumineux) selon l'ordre pratique de l'audience :
  1. Page couverture + **Table des matières** détaillée par onglet ;
  2. Plan de plaidoirie / plan d'argumentation (lorsque versé dans le cahier d'audience) ;
  3. Actes de procédure finaux déposés (demande introductive, défense/exposé sommaire, actes modifiés, protocole de l'instance, demandes incidentes) ;
  4. Liste/bordereau des pièces + pièces pertinentes (avec intercalaires/timbres `PIÈCE P-1`) ;
  5. Cahier des autorités (ou onglet dédié avec surlignement jaune) ;
  6. **Endos paysage (`11 × 8,5 po`)** conforme en clôture du cahier.
* **Annexes d'appel (`370–374 C.p.c.`, `c-25.01-r.0.2.01 art. 47, 50–55, 58`, lire via `lois.get_articles` — les directives du greffe C.A.Q. restent hors corpus Vague 1) :**
  * **Présentation uniforme (`art. 54`) :** Couverture **jaune** (appelant), **verte** (intimé) ou **grise** (autre partie) mentionnant numéro d'appel, juridiction/district/juge/date/numéro de 1re instance, désignation selon l'art. `25`, titre selon la position et coordonnées des procureurs (`54 a)–b)`); papier format lettre (`21,5 × 28 cm`), max **`225 feuilles` par volume** avec numérotation des volumes et séquence des pages sur la couverture et la tranche inférieure (`54 h)–i)`); table des matières générale au volume 1 et particulière à chaque volume (`54 c)`); **pagination continue placée en haut de page et centrée** (`54 d)`). L'argumentation (max `30 p.` en mémoire `art. 50` / `10 p.` en exposé `art. 58`, en `Arial 12`, citations `Arial 11` simple interligne en retrait, notes `Arial 10`, marges `>= 2,5 cm` `art. 54 e)`) et l'**Annexe I** s'impriment sur les **pages de gauche**; les **Annexes II et III** s'impriment **recto verso** (`54 g)`).
  * **Annexe I (`art. 51 a)`) :** Jugement porté en appel (avec motifs), avis de jugement le cas échéant, et décision antérieure en cause s'il statue sur un contrôle judiciaire ou un appel (avec transcription typographique si manuscrit).
  * **Annexe II (`art. 51 b)`) :** Déclaration d'appel (`352`) et demande/jugement de permission d'appeler (`357`), actes de procédure pertinents de 1re instance et procès-verbal de l'instruction (ainsi que la demande devant le tribunal inférieur en contrôle judiciaire/appel), plus les dispositions législatives et réglementaires invoquées **autres que le `C.c.Q.` et le `C.p.c.`** en français et en anglais si disponibles.
  * **Annexe III (`art. 51 c)`, `372 al. 1`) :** Uniquement les **pièces et dépositions nécessaires** pour permettre à la Cour de trancher les questions en litige. Pièces reproduites dans l'ordre des cotes en débutant chacune sur une page nouvelle titrée avec la **cote, la date et la nature** (`54 j) iv`); transcription typographique obligatoire si manuscrit illisible ou audio/vidéo de mauvaise qualité `54 j) i–ii`). Dépositions débutant sur une page nouvelle portant en titre **`NOM, Prénom` + position + stade de l'instruction + stade du témoignage** en abrégé entre parenthèses, repris sur chaque page suivante (`54 k)`).
  * **Complément d'intimé / appelant incident (`art. 47, 53`) :** L'intimé ou l'appelant incident ne reproduit jamais ce qui figure déjà aux annexes de l'appelant (complément ciblé seulement).
  * **Mentions finales (`art. 52`) et notification (`art. 55`) :** Sur la dernière page du mémoire/exposé, inclure l'attestation de conformité réglementaire et technologique, l'engagement à mettre les dépositions à la disposition des autres parties sans frais, le temps de plaidoirie souhaité (incluant la réplique pour l'appelant) et la signature. Dépôt papier (`5 exemplaires` sauf décision contraire) + version technologique (`art. 13`); preuve de notification déposée au greffe au plus tard dans les **`3 jours ouvrables`** suivant l'expiration du délai `373` (notification technologique seule possible uniquement avec **consentement écrit et exprès** du destinataire joint à la preuve `art. 55 al. 3`).

## Contrôles automatisés

1. Exécuter `python scripts/controler_document.py <cahier.pdf> --exiger-couche-texte --exiger-signets --json` pour vérifier pagination, couche texte OCR, signets (`/Outlines`) et format US Letter portrait/paysage sans verrou `/Encrypt`.
2. Exécuter `python scripts/verifier_cotes.py` sur l'ensemble des actes modifiés inclus pour confirmer l'intégrité des cotes gelées.
3. **Dégradation nuage sans Python (`claude.ai`, ChatGPT sans Python, Gemini App `/mcp/oauth`, Deep Research) :** si les scripts ne peuvent pas s'exécuter localement, **divulguer explicitement** que les vérifications scriptées octets/PDF/OCR/signets et cotes ont été **omises** et les inscrire en tête du bon de travail.

## Contrôles humains

* **Cahier de première instance :** Vérifier qu'aucun acte n'est un projet portant une mention `PROJET`, qu'aucune pièce jointe verrouillée par signature électronique n'empêche la fusion, et que chaque onglet correspond exactement à la Table des matières et aux signets PDF.
* **Annexes d'appel (`372–373 C.p.c.`, `c-25.01-r.0.2.01`) :** Contrôler la sélectivité stricte de l'Annexe III (seules les pièces et pages de dépositions nécessaires aux questions en litige), l'exclusion du `C.c.Q.`/`C.p.c.` hors Annexe II (`51 b) iv`), l'impression pages de gauche (Argumentation + Annexe I) vs recto verso (Annexes II–III), la pagination continue centrée en haut de page, les en-têtes `NOM, Prénom` sur chaque page de déposition, le plafond de `225 feuilles` par volume, l'attestation `art. 52`, et la concordance 1:1 avec les renvois de l'argumentation.

## Bon de travail

Produire le bon de travail ordonné pour l'outil PDF du cabinet :
1. Aplatir tout document chiffré (`/Encrypt`, formulaires XFA ou signatures Adobe) et exécuter l'OCR sur les pièces numérisées ;
2. Fusionner dans l'ordre exact de la Table des matières avec intercalaires/onglets numérotés et endos paysage final (`11 × 8,5 po`) — ou, en appel, monter les volumes séparés Argumentation + Annexe I (pages de gauche) et Annexes II–III (recto verso, `<= 225 feuilles`/vol.) avec couverture couleur réglementaire (`jaune`/`vert`/`gris`), pagination continue centrée en haut de page et titres de dépositions `54 k)` ;
3. Générer les signets navigables (`/Outlines`) par section, annexe et cote, contrôler la taille totale du fichier pour dépôt électronique (et obtenir le consentement écrit `art. 55 al. 3` si notification technologique seule en appel), *(en listant explicitement les contrôles PDF/cotes omis si les scripts locaux n'ont pas pu être exécutés)*.
