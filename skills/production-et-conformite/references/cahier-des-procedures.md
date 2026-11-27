# Cahier des procédures (reflet du plumitif remis au tribunal)

Encadre l'assemblage du **cahier des procédures** remis au tribunal en première instance (`c-25.01-r.0.2.1`, `c-25.01-r.9`, directives `qccs-*` et `qccq-*`), en le distinguant strictement du **cahier de procès** personnel du plaideur, des cahiers de pièces/sources et du mémoire d'appel.

## Règles applicables

* **Définition et frontières étanches :**
  * **Le Cahier des procédures = le reflet fidèle du plumitif :** il regroupe **exclusivement les actes officiellement déposés au greffe** dans leur état procédural exact à la date de l'audience.
  * **Ce qui n'y entre jamais :** le **plan de plaidoirie / plan d'argumentation**, les **pièces** (`cahier-des-pieces-et-bordereaux.md`), les **autorités** (`cahier-des-sources.md`), tout `PROJET` non déposé, ainsi que les **mémoires ou exposés d'appel et leurs Annexes I à III** (lesquels constituent un acte unique propre à l'appel régi par `arg-memoire-et-expose-appel.md`).
  * **Ne jamais confondre avec le *Cahier de procès* :** le *cahier de procès* est le **cartable personnel et confidentiel du plaideur** pour sa conduite d'audience (plan de plaidoirie, frise chronologique, matrice, plans d'interrogatoire et de contre-interrogatoire, extraits annotés de jurisprudence, selon les souhaits de l'avocat et la complexité de la cause — voir `produit-fiche-preuve-et-temoins.md`). Il **ne se dépose jamais au greffe et ne se communique pas à la partie adverse**.
* **Contenu ordonné du Cahier des procédures (`c-25.01-r.0.2.1`, `c-25.01-r.9`, directives `qccs-*` / `qccq-*` en `fonction='directive'`, `fr`-only) :**
  1. Page couverture + **Table des matières** détaillée par onglet (et copie du **plumitif** à jour en tête si utile au juge) ;
  2. Demande introductive d'instance (et, s'il y a eu modification sous `206 C.p.c.`, la dernière version modifiée mettant en évidence les ajouts et `(…)`, accompagnée des versions antérieures pertinentes au plumitif) ;
  3. Réponse, **protocole(s) de l'instance** (`148`) ou avis C.Q. (`SJ-1273`, `SJ-1274`) et procès-verbaux / décisions de gestion pertinents (`159 C.p.c.`) ;
  4. Moyens préliminaires, demandes incidentes et jugements interlocutoires pertinents inscrits au plumitif ;
  5. Défense ou exposé sommaire, demande reconventionnelle, acte d'intervention ou appel en garantie et leurs réponses/défenses ;
  6. **Déclaration commune d'inscription** (`174 C.p.c.`, `SJ-1100` ou `SJ-1276`) ou *Déclaration commune pour fixation d'une audience* déposée au greffe ;
  7. **Endos paysage (`11 × 8,5 po`)** conforme en clôture du cahier.
* **Présentation matérielle et confidentialité (`qccs-div-mtl` par. 26–27, 30–31 ; `c-25.01-r.0.2.1 art. 3`) :**
  * **Recto seulement :** contrairement aux cahiers de pièces et de sources encouragés en recto verso (`qccs-div-mtl` par. 31), les actes de procédure se présentent **recto seulement** sur papier format lettre (`8,5 × 11 po`) ;
  * **Reliure sans cartable à anneaux :** paginer et relier avec onglets numérotés — **ne jamais utiliser de cartable à anneaux** pour un dépôt au greffe, ce format empêchant le classement des dossiers (`qccs-div-mtl` par. 30) ;
  * **Pli cacheté et caviardage (`12, 108 C.p.c.`, `qccs-div-mtl` par. 26–27) :** ne jamais intégrer dans le cahier ordinaire ni téléverser sur le **GNJQ** un acte déposé sous pli cacheté ou contenant des éléments d'identification confidentiels (dépôt physique au greffe sous enveloppe identifiée `CONFIDENTIEL` ou `SOUS SCELLÉ`).

## Contrôles automatisés

1. Exécuter `python scripts/controler_document.py <cahier-procedures.pdf> --exiger-couche-texte --exiger-signets --json` pour vérifier pagination, couche texte OCR, signets (`/Outlines`) et format US Letter portrait/paysage sans verrou `/Encrypt`.
2. Exécuter `python scripts/verifier_cotes.py` sur les actes de procédure (notamment tout acte modifié sous `206 C.p.c.`) afin de confirmer l'intégrité des cotes invoquées et gelées.
3. **Dégradation nuage sans Python (`claude.ai`, ChatGPT sans Python, Gemini App `/mcp/oauth`, Deep Research) :** si les scripts ne peuvent pas s'exécuter localement, **divulguer explicitement** que les vérifications scriptées octets/PDF/OCR/signets et cotes ont été **omises** et les inscrire en tête du bon de travail.

## Contrôles humains

* **Concordance 1:1 avec le plumitif :** Vérifier chaque numéro de séquence au plumitif afin qu'aucun acte déposé pertinent ne manque et qu'aucun projet non déposé (`PROJET`), note interne ou plan de plaidoirie ne s'y glisse.
* **Intégrité des actes déposés :** Vérifier la présence des timbres/preuves de dépôt ou dates de production, la mise en évidence réglementaire sur les actes modifiés (`art. 11 R.C.s.Q.m.c.`), l'absence de verrou de signature électronique empêchant la fusion, l'exclusion de tout document sous scellé (`12, 108 C.p.c.`) et la correspondance exacte entre la Table des matières, les onglets physiques et les signets PDF.

## Bon de travail

Produire le bon de travail ordonné pour l'outil PDF et la reprographie du cabinet :
1. Aplatir tout document chiffré (`/Encrypt`, formulaires XFA ou signatures numériques) et exécuter l'OCR sur les actes ou procès-verbaux numérisés ;
2. Assembler uniquement les actes déposés au plumitif dans l'ordre exact de la Table des matières, avec intercalaires à onglets numérotés, impression **recto seulement**, reliure conforme (**aucun cartable à anneaux**) et endos paysage final (`11 × 8,5 po`), en traitant à part sous enveloppe physique scellée tout acte visé par `12 / 108 C.p.c.` ;
3. Générer les signets navigables (`/Outlines`) par onglet et acte, puis contrôler la taille du fichier PDF *(en inscrivant en tête les contrôles PDF/cotes omis si les scripts locaux n'ont pas pu être exécutés)*.
