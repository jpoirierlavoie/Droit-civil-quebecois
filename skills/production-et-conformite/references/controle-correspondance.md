# Contrôle de la correspondance avant envoi (légendes, destinataires, pièces jointes)

Vérifie la forme, les mentions de protection, l'exactitude des destinataires/copies et l'innocuité des pièces jointes avant toute transmission d'une lettre ou mise en demeure.

## Règles applicables

Charger selon le cas `lois.get_articles` sur :
* `b-1-r.3.1` (*Code de déontologie des avocats*) : `art. 60–63` (secret professionnel et confidentialité), `art. 120` (interdiction de communiquer directement avec une partie représentée sans consentement de son avocat) et `art. 121` (interdiction de communiquer avec le tribunal hors audience sans copie conforme simultanée aux autres parties/procureurs) ;
* `ccq` : `art. 1594–1597` (mise en demeure, délai raisonnable et demeure de plein droit) ;
* `cpc` : `art. 4` (coopération), `art. 51` (abus), `art. 108` (protection des renseignements), `art. 109–111` (notification et heure limite), `art. 206` (avis de modification).

## Contrôles automatisés

1. Exécuter `python scripts/controler_document.py <piece_jointe.docx|pdf> --json` (ou `inspecter_piece.py` dans `analyse-et-strategie`) sur toute pièce jointe afin d'exclure commentaires cachés, marques de révision ou métadonnées compromises. *(Sur surface nuage sans Python — `claude.ai`, Gemini App `/mcp/oauth`, Deep Research — divulguer explicitement que les contrôles octets/XML/PDF par script ont été omis et les reporter au bon de travail.)*
2. Exécuter `outils.terminologie_scan` sur le texte de la correspondance (vérification FR/EN, `UNDER ALL RESERVES` vs `WITHOUT PREJUDICE`).

## Contrôles humains

* **Légendes exactes et séparation des envois :**
  * `CONFIDENTIEL ET PRIVILÉGIÉ` (correspondance et avis au client exclusivement) ;
  * `SOUS TOUTES RÉSERVES` / `WITHOUT PREJUDICE` réservé **strictement aux pourparlers et offres de règlement** — **jamais** sur une mise en demeure (`1595 C.c.Q.`), une demande de remise, un **avis formel d'intention de modifier (`206 C.p.c.`)** ou une dénonciation écrite d'abus (`51 C.p.c.`) appelés à être produits devant le tribunal ; ne jamais mêler dans une même lettre éléments ouverts et propositions de règlement ;
* **Destinataires et `c. c.` :** Aucune communication directe à une partie représentée (`Code 120 al. 1`), copie conforme intégrale et simultanée à tous les procureurs pour toute lettre au tribunal, au TAL ou au greffe (`Code 121`), vérification rigoureuse des champs `À` / `Cc` / `Cci` ;
* **Pièces jointes annoncées et concordance :** Chaque pièce annoncée dans la lettre est effectivement jointe dans sa version finale (jamais un projet interne ou brouillon), lisible, caviardée (`108 C.p.c.`) et cohérente quant à la date, aux montants et à l'accord singulier/pluriel des parties.

## Bon de travail

Produire un bon de travail court avant l'envoi :
1. Vérifier ou corriger la légende en tête de lettre (`CONFIDENTIEL`, `SOUS TOUTES RÉSERVES` / `WITHOUT PREJUDICE` ou lettre ouverte) ;
2. Valider la liste des destinataires et des copies conformes (`Code 120–121`) ;
3. Purger les métadonnées, commentaires et révisions des pièces jointes et confirmer l'aplatissement des caviardages (`108 C.p.c.`) avant expédition *(en listant explicitement les vérifications XML/PDF omises si `controler_document.py` n'a pas pu s'exécuter)*.
