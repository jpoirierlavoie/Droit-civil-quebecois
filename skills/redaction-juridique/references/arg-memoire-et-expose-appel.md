# Mémoire d'appel, exposé et Annexes I à III en Cour d'appel (`C.p.c.` & `c-25.01-r.0.2.01`)

Encadre la rédaction et la confection matérielle indissociable du mémoire d'appel (`370–373 C.p.c.`), de l'exposé (`374 C.p.c.`) et de leurs **Annexes I, II et III** devant la Cour d'appel du Québec (`c-25.01-r.0.2.01`).

## Destinataire et format

**Appeler `lois.get_articles` avant toute rédaction :**
* `law="cpc"`, `numbers=["370", "371", "372", "373", "374", "376"]`
* `law="c-25.01-r.0.2.01"` (*Règlement de la Cour d'appel du Québec en matière civile*), `numbers=["13", "25", "47", "50", "51", "52", "53", "54", "55", "58", "60"]` *(les directives et avis du greffier de la Cour d'appel `QCCA` sont hors corpus de `134` textes et doivent être vérifiés directement à la source pour le dépôt technologique et d'éventuelles dispenses d'exemplaires papier)*.
* **Présentation réglementaire uniforme (`art. 50, 54, 58`) :**
  * **Couverture et volumes (`54 a)–b), h)–i)`) :** couverture **jaune** (appelant), **verte** (intimé) ou **grise** (autre partie) portant numéro d'appel, tribunal/district/juge/date/numéro de 1re instance, désignation selon l'art. `25`, titre selon la position et coordonnées des avocats ; papier format lettre (`21,5 × 28 cm`), max **`225 feuilles` par volume**, volumes et séquence de pages inscrits sur la couverture et la tranche inférieure ; table des matières générale au volume 1 et particulière à chaque volume suivant (`54 c)`) ; **pagination continue centrée en haut de page** (`54 d)`).
  * **Typographie, pages et impression (`50, 54 e)–g), 58`) :** les **parties I à IV** de l'argumentation n'excèdent pas **`30 pages`** en mémoire (`art. 50`) ou **`10 pages`** en exposé (`art. 58`), sauf décision contraire ; paragraphes numérotés, interligne `>= 1,5`, police `Arial 12` (`Arial 11` à interligne simple et en retrait pour les citations, `Arial 10` à interligne simple pour les notes infrapaginales), marges `>= 2,5 cm`. L'**argumentation et l'Annexe I** s'impriment sur les **pages de gauche** ; les **Annexes II et III** s'impriment **recto verso** (`54 g)`).

## Structure

* **Exposé (`374 C.p.c.`, `art. 58`) :** Pour appels régis par `374` ou sur décision de gestion ; mêmes règles de contenu et d'annexes (`art. 47, 48, 51–56`), plafond d'argumentation ramené à **`10 pages`** (parties I à IV).
* **Mémoire d'appel (`372–373 C.p.c.`, `art. 47–55`) :**
  1. **Partie I — Les faits** *(ou énoncé commun si déposé, `372 al. 2`, sobre et appuyé aux renvois exacts aux annexes)* ;
  2. **Partie II — Les questions en litige** *(avec identification explicite de la **norme d'intervention** applicable à chaque question)* ;
  3. **Partie III — L'argumentation** *(structurée question par question, démonstration précise des erreurs déterminantes du jugement entrepris ; en appel incident `art. 53`, 2 sections : réponse à l'appel principal puis argumentation d'appelant incident)* ;
  4. **Partie IV — Les conclusions** *(dispositif précis recherché, y compris les frais de justice)* ;
  5. **Partie V — Les sources** *(liste des autorités citées, classées selon le règlement)* ;
  6. **Mentions finales (`art. 52`, dernière page du mémoire/exposé) :** attestation de conformité au règlement et aux exigences technologiques, engagement à mettre sans frais les dépositions à la disposition des autres parties, temps de plaidoirie souhaité (incluant la réplique pour l'appelant) et signature ;
  7. **Annexes obligatoires de l'appelant (`art. 51, 54 j)–k)`) — complément non redondant seulement pour l'intimé ou l'appelant incident (`art. 47, 53`) :**
     * **Annexe I (`51 a)`) :** jugement porté en appel (avec motifs), avis de jugement le cas échéant, et décision antérieure en cause s'il statue sur un contrôle judiciaire ou un appel (avec transcription typographique si manuscrit) ;
     * **Annexe II (`51 b)`) :** déclaration d'appel (`352`), demande et jugement de permission d'appeler (`357`) le cas échéant, actes de procédure pertinents de 1re instance et procès-verbal de l'instruction (ainsi que la demande devant le tribunal inférieur en contrôle judiciaire/appel), plus les dispositions législatives et réglementaires invoquées **autres que le `C.c.Q.` et le `C.p.c.`** en français et en anglais si disponibles ;
     * **Annexe III (`51 c)`, `372 al. 1`) :** **uniquement les pièces et dépositions nécessaires** pour trancher les questions en litige. Chaque pièce débute sur une page nouvelle portant en titre la **cote, la date et la nature** (`54 j) iv`), avec transcription typographique si manuscrit illisible ou enregistrement de mauvaise qualité (`54 j) i–ii`). Chaque déposition débute sur une page nouvelle portant en titre **`NOM, Prénom`** suivi entre parenthèses et en abrégé de la position de la partie, du stade de l'instruction et du stade du témoignage, mentions reprises en titre de chaque page suivante (`54 k)`).

## Discipline de citation

Appliquer strictement `arg-citations.md` : citations neutres vérifiées via `juris.verify_citations`, paragraphes majoritaires vérifiés sur texte intégral lu en session, et marqueur `[RATIO / PAR. X À INSÉRER APRÈS LECTURE DE <citation + lien CanLII>]` si le texte complet manque.

## Pièges

* **Absence de norme d'intervention** ou confusion entre erreur de droit (décision correcte) et erreur de fait ou mixte (erreur manifeste et déterminante).
* **Annexe III non sélective, reproduction du `C.c.Q.`/`C.p.c.` à l'Annexe II (`51 b) iv`), ou doublons chez l'intimé (`47, 53`).**
* **Notification technologique seule sans consentement écrit exprès (`art. 55 al. 3`) :** par défaut, dépôt en `5 exemplaires` papier (sauf avis/décision contraire) + version technologique (`art. 13, 55`), et preuve de notification déposée au plus tard dans les **`3 jours ouvrables`** suivant l'expiration du délai `373` ; la notification par seul moyen technologique exige le **consentement écrit et exprès** du destinataire joint à la preuve de notification.

## Contrôle

1. Vérifier les paramètres typographiques, la pagination centrée en haut, le plafond de pages (`50, 58`), les volumes (`<= 225 feuilles`) et les signets/OCR PDF via `production-et-conformite` (`controle-pdf-et-metadonnees.md` et `controler_document.py` — ou, sans Python local en nuage, divulguer explicitement les vérifications octets/XML/PDF omises en tête du bon de travail manuel), ainsi que les dispenses de reproduction du cahier des sources d'appel (`cahier-des-sources.md`, `juris.check_exempt_cases(list_id="qcca-civil")` selon l'art. `60 al. 2 R.C.a.Q.m.civ.`).
2. Vérifier le délai de rigueur du mémoire (`373` : caducité de plein droit si expiré sans prolongation demandée *avant* échéance) et le dépôt de la preuve de notification (`3 jours ouvrables`, `art. 55`) via `gestion-du-mandat`.
3. Exécuter `outils.terminologie_scan`.
