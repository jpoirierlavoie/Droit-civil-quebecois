# Cahier des procédures, cahier de procès et annexes d'appel

`[FICHE À RÉDIGER]` *(concernant les Annexes I, II et III d'appel `c-25.01-r.0.2.01` ; la structure des cahiers de procès et d'audience de première instance est documentée ci-dessous)*

Encadre l'assemblage du **cahier de procès** / **cahier d'audience interlocutoire** en première instance (`c-25.01-r.0.2.1`, `c-25.01-r.9`) ainsi que la confection des Annexes I, II et III du mémoire d'appel (`372–373 C.p.c.`, `c-25.01-r.0.2.01`).

## Règles applicables

* **Cahier de procès / Cahier d'audience de première instance (`c-25.01-r.0.2.1`, `c-25.01-r.9`) :** Assembler dans un volume unique (ou par volumes séparés si volumineux) selon l'ordre pratique de l'audience :
  1. Page couverture + **Table des matières** détaillée par onglet ;
  2. Plan de plaidoirie / plan d'argumentation (lorsque versé dans le cahier d'audience) ;
  3. Actes de procédure finaux déposés (demande introductive, défense/exposé sommaire, actes modifiés, protocole de l'instance, demandes incidentes) ;
  4. Liste/bordereau des pièces + pièces pertinentes (avec intercalaires/timbres `PIÈCE P-1`) ;
  5. Cahier des autorités (ou onglet dédié avec surlignement jaune) ;
  6. **Endos paysage (`11 × 8,5 po`)** conforme en clôture du cahier.
* **Annexes d'appel (`c-25.01-r.0.2.01`, `372–373 C.p.c.`) :** `[FICHE À RÉDIGER]` — Lire via `lois` les règles exactes du *Règlement de la Cour d'appel en matière civile* quant au format, à la pagination continue et au contenu obligatoire des Annexes I (jugement entrepris et avis), II (procédures et dispositions législatives) et III (extraits nécessaires de preuve et dépositions).

## Contrôles automatisés

1. Exécuter `python scripts/controler_document.py <cahier.pdf> --exiger-couche-texte --exiger-signets --json` pour vérifier pagination, couche texte OCR, signets (`/Outlines`) et format US Letter portrait/paysage sans verrou `/Encrypt`.
2. Exécuter `python scripts/verifier_cotes.py` sur l'ensemble des actes modifiés inclus pour confirmer l'intégrité des cotes gelées.

## Contrôles humains

* **Cahier de première instance :** Vérifier qu'aucun acte n'est un projet portant une mention `PROJET`, qu'aucune pièce jointe verrouillée par signature électronique n'empêche la fusion, et que chaque onglet correspond exactement à la Table des matières et aux signets PDF.
* **Annexes d'appel (`372–373 C.p.c.`) :** `[FICHE À RÉDIGER]` — Contrôler la sélectivité de l'Annexe III (seules les pièces et pages de dépositions nécessaires à l'argumentation, `c-25.01-r.0.2.01`) et la concordance exacte entre la table des matières, la pagination continue et les renvois du mémoire.

## Bon de travail

Produire le bon de travail ordonné pour l'outil PDF du cabinet :
1. Aplatir tout document chiffré (`/Encrypt`, formulaires XFA ou signatures Adobe) et exécuter l'OCR sur les pièces numérisées ;
2. Fusionner dans l'ordre exact de la Table des matières avec intercalaires/onglets numérotés et endos paysage final (`11 × 8,5 po`) ;
3. Générer les signets navigables (`/Outlines`) par section et par cote, puis contrôler le poids total pour dépôt électronique. *(Annexes I, II et III d'appel : `[FICHE À RÉDIGER]` — valider les gabarits spécifiques de pagination continue C.A.Q.)*
