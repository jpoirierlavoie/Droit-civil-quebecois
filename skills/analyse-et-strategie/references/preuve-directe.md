# Analyse de la preuve directe (écrits, courriels, photos, vidéos, enregistrements)

Encadre l'évaluation des éléments probatoires directs (contrats, lettres, courriels, photographies, vidéos, enregistrements audio) avec **honnêteté perceptuelle stricte** et **journal de garde**.

## Qualification

Identifier avec précision le moyen de preuve selon `lois.get_articles(law="ccq", numbers=["2811", "2813", "2826", "2827", "2831", "2832", "2837", "2854", "2855", "2874"])`, `law="c-1.1", numbers=["5", "6", "7", "12", "16", "17", "38", "39"]` et `law="cpc", numbers=["262"]` :
* **Acte écrit** (authentique, sous seing privé papier ou électronique, écrit d'entreprise, autre écrit / courriel / texto) ;
* **Document technologique** (`c-1.1`, incluant une copie issue d'un transfert de support sous `art. 17`) ;
* **Élément matériel ou déclaration enregistrée** (`2854–2855`, `2874 C.c.Q.` : photographie, vidéo, enregistrement sonore ou objet).

## Authentification et intégrité

### 1. Journal de garde à l'entrée (`inspecter_piece.py --journal`)
Exécuter obligatoirement `python scripts/inspecter_piece.py <fichier> --journal <dossier>/journal-garde.json --source "<origine>" --json` dès la prise en charge d'un média ou d'une pièce numérique originale afin de consigner de façon immuable :
* l'empreinte **SHA-256** et la taille exacte en octets ;
* la date système et les métadonnées internes extraites (EXIF appareil/GPS, `mvhd` vidéo, `ID3`/`INFO` audio, en-têtes `.eml`) ;
* l'origine déclarée (`--source`).
*(Dégradation nuage sans Python / disque non inscriptible — (`claude.ai`, Gemini App `/mcp/oauth`, Deep Research : divulguer explicitement que l'extraction scriptée octets/EXIF/conteneur/SHA-256 via `inspecter_piece.py` a été omise, livrer le journal de garde en bloc Markdown en ligne avec `[SHA-256 : À CALCULER LOCALEMENT]`, et inscrire le calcul d'empreinte et l'extraction des métadonnées au bon de travail.)*

### 2. Honnêteté perceptuelle stricte (règle absolue sur photos, vidéos et enregistrements)
* **Ne jamais décrire ni interpréter un contenu visuel ou sonore non effectivement perçu dans la session.**
* Si le modèle n'a pas accès au canal audio/vidéo/image ou ne perçoit pas les images clés : **refuser de décrire la scène ou les propos**, exiger une **transcription** ou une **série de captures fixes** fournies par l'avocat, et étiqueter explicitement toute analyse ultérieure **`support secondaire`**.
* **Avertissement sur les transcriptions IA :** Toute transcription générée par IA est une **aide de travail uniquement**, jamais un élément de preuve autonome (`[À VÉRIFIER SUR L'ENREGISTREMENT ORIGINAL]`).

## Recevabilité

* **Original, transfert de support et contestation d'intégrité (`2838–2840, 2860 C.c.Q.` ; `c-1.1 art. 5–7, 12, 16, 17` ; `262 C.p.c.`) :** Le procédé technologique bénéficie d'une présomption d'intégrité (`2840 C.c.Q.`, `c-1.1 art. 7`) à moins que le contestant n'établisse par prépondérance de preuve une atteinte à l'intégrité (recadrage, absence d'EXIF, fil de courriels tronqué, coupure audio, heure incohérente). Si un original papier a été détruit après numérisation, sa valeur juridique exige la **documentation du transfert (`c-1.1 art. 17`)**. Toute contestation de l'origine ou de l'intégrité d'un document doit être soulevée **au plus tard avant l'inscription pour instruction et jugement, appuyée d'une déclaration sous serment (`262 C.p.c.`)**.
* **Preuve distincte d'authenticité (`2855, 2874 C.c.Q.` ; `c-1.1 art. 5 al. 2 c. al. 3`) :** Pour un élément matériel ou un enregistrement sur support technologique dont l'intégrité est assurée (`c-1.1 art. 5 al. 2`, `art. 6–7`), la preuve distincte d'authenticité est dispensée ; en revanche, **elle demeure obligatoire dans le cas visé à `c-1.1 art. 5 al. 3`** (lorsque le support ou la technologie ne permet ni d'affirmer ni de dénier que l'intégrité est assurée, auquel cas le document ne peut être admis, selon les circonstances, qu'à titre de témoignage, d'élément matériel ou de commencement de preuve sous `2865 C.c.Q.`).
* **Captation clandestine, vie privée et secret professionnel (`35–36`, `2858 al. 1–2 C.c.Q.` ; `c-12 art. 5, 9`) :** Distinguer l'interception illicite d'une communication privée par un tiers (`36(2°) C.c.Q.`) de l'enregistrement réalisé à l'insu d'autrui par **un participant à la conversation** : ce dernier n'est pas exclu d'emblée, mais doit franchir le double test de **`2858 al. 1 C.c.Q.`** (atteinte à un droit fondamental tel le droit à la vie privée + utilisation susceptible de déconsidérer l'administration de la justice). En présence d'une **violation du secret professionnel (`2858 al. 2 C.c.Q.`, `c-12 art. 9`)**, le tribunal doit toutefois rejeter la pièce **d'office**, sans égard au second critère.

## Force probante

Évaluer le poids probatoire selon la nature du support et le fardeau (`2803–2804 C.c.Q.`) :

* **Contrat ou acte sous seing privé signé — papier ou technologique (`2826–2829 C.c.Q.`, `c-1.1 art. 38–39`, `262 C.p.c.`) :** Opposé à celui qui paraît l'avoir signé, il est **tenu pour reconnu** s'il n'est pas contesté par déclaration sous serment avant l'inscription (`262 C.p.c.`, `Établi`). Pour une signature technologique (`2827 C.c.Q.`, `c-1.1 art. 38–39`), vérifier que l'intégrité du document est assurée et que le **lien entre la personne, la signature et le document est maintenu sans rupture depuis la signature** (journal d'audit, certificat). Entre les parties, l'écrit valablement fait ne peut être contredit par témoignage (`2863`), sauf pour l'interpréter (`2864`) ou avec un commencement de preuve (`2865`).
* **Écrit d'entreprise non signé (`2831 C.c.Q.`) :** Fait preuve de son contenu s'il est **habituellement utilisé dans le cours des activités d'une entreprise pour constater un acte juridique** (factures séquentielles, bons de livraison, grand livre contemporain) ; distinguer nettement d'un chiffrier ou sommaire préparé pour les besoins du litige (`Rapporté` / à établir par témoin).
* **Échanges de courriels et messages texte (`2832, 2835, 2837–2840 C.c.Q.`, `c-1.1 art. 5, 7, 38`) :** Exigent d'établir le lien d'attribution à l'auteur (`2835`, `c-1.1 art. 38` : fichier `.eml` complet avec en-têtes `Message-ID`/`DKIM`, adresse ou numéro habituel, réponse ultérieure reconnaissant l'échange). Un fil chronologique complet et natif possède une force probante nettement supérieure à une capture d'écran isolée ou recadrée.
* **Photographies et vidéos (`2854–2856 C.c.Q.`, `c-1.1 art. 5 al. 2–3`) :** Permettent au tribunal de tirer ses propres conclusions (`2854, 2856`), moyennant une preuve d'authenticité par témoin (photographe ou personne présente attestant la date, le lieu et la fidélité) lorsque la pièce relève de `c-1.1 art. 5 al. 3` ou que son intégrité est contestée. Les métadonnées EXIF/`mvhd` corroborent la chronologie sans remplacer le témoin en cas de contestation sérieuse.
* **Enregistrement sonore entre parties (`2855, 2857, 2858, 2874, 35–36 C.c.Q.`) :** Exige la remise du fichier intégral non monté, l'identification fiable de chaque voix, la preuve d'authenticité lorsque requise sous `2874` / `c-1.1 art. 5 al. 3` et le contrôle sous `2858 C.c.Q.` ; toute transcription demeure une simple aide de travail subordonnée à l'écoute de l'original.

## Protection

* Contrôler la présence de tiers non parties, de données biométriques, médicales ou psychosociales ou d'éléments de vie privée (Loi 25, `art. 16` et `108 C.p.c.`) sur les écrits, photos, vidéos et enregistrements.
* Préserver les fichiers natifs originaux sans recompression ni altération des métadonnées.

## Ce que la pièce ne prouve pas

* Une photographie ou une vidéo d'un lieu, d'un bien ou d'un sinistre établit un état apparent à un instant précis, mais **ne prouve à elle seule ni la cause technique ou la faute** (qui exige souvent une expertise), **ni la nécessité ou le chiffrage des travaux correctifs**.
* Une capture d'écran isolée ne prouve ni l'intégrité du fil complet ni l'identité réelle du compte expéditeur sans vérification complémentaire.
* Une métadonnée EXIF ou un horodatage modifiable ne prouve pas à lui seul la date réelle sans corroboration, et son absence (`EXIF_ABSENT_OU_STRIPPE`) signale un retraitement possible (réseau social, messagerie).
* Une transcription non vérifiée mot à mot sur l'original ne prouve jamais les paroles exactes attribuées à un interlocuteur.
