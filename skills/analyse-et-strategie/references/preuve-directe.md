# Analyse de la preuve directe (écrits, courriels, photos, vidéos, enregistrements)

[NON VALIDÉ PAR LA PRATIQUE]

Encadre l'évaluation des éléments probatoires directs (contrats, lettres, courriels, photographies, vidéos, enregistrements audio) avec **honnêteté perceptuelle stricte** et **journal de garde**.

## Qualification

Identifier avec précision le moyen de preuve selon `lois.get_articles(law="ccq", numbers=["2811", "2813", "2826", "2831", "2832", "2837", "2854", "2855"])` et `law="c-1.1", numbers=["5", "7", "12", "16"]` :
* **Acte écrit** (authentique, sous seing privé, écrit d'entreprise, autre écrit / courriel / texto);
* **Document technologique** (`c-1.1`);
* **Élément matériel** (`2854–2855 C.c.Q.` : photographie, vidéo, enregistrement sonore ou objet).

## Authentification et intégrité

### 1. Journal de garde à l'entrée (`inspecter_piece.py --journal`)
Exécuter obligatoirement `python scripts/inspecter_piece.py <fichier> --journal <dossier>/journal-garde.json --source "<origine>" --json` dès la prise en charge d'un média ou d'une pièce numérique originale afin de consigner de façon immuable :
* l'empreinte **SHA-256** et la taille exacte en octets;
* la date système et les métadonnées internes extraites (EXIF appareil/GPS, `mvhd` vidéo, `ID3`/`INFO` audio, en-têtes `.eml`);
* l'origine déclarée (`--source`).
*(Dégradation nuage sans Python / disque non inscriptible — `claude.ai`, ChatGPT sans Python, Gemini App `/mcp/oauth`, Deep Research : divulguer explicitement que l'extraction scriptée octets/EXIF/conteneur/SHA-256 via `inspecter_piece.py` a été omise, livrer le journal de garde en bloc Markdown en ligne avec `[SHA-256 : À CALCULER LOCALEMENT]`, et inscrire le calcul d'empreinte et l'extraction des métadonnées au bon de travail.)*

### 2. Honnêteté perceptuelle stricte (règle absolue sur photos, vidéos et enregistrements)
* **Ne jamais décrire ni interpréter un contenu visuel ou sonore non effectivement perçu dans la session.**
* Si le modèle n'a pas accès au canal audio/vidéo/image ou ne perçoit pas les images clés : **refuser de décrire la scène ou les propos**, exiger une **transcription** ou une **série de captures fixes** fournies par l'avocat, et étiqueter explicitement toute analyse ultérieure **`support secondaire`**.
* **Avertissement sur les transcriptions IA :** Toute transcription générée par IA est une **aide de travail uniquement**, jamais un élément de preuve autonome (`[À VÉRIFIER SUR L'ENREGISTREMENT ORIGINAL]`).

## Recevabilité

* **Original et intégrité technologique (`2838–2840, 2860 C.c.Q.`; `c-1.1 art. 5, 7, 12, 16`) :** relever tout indice d'altération (recadrage, absence d'EXIF, fil de courriels tronqué, coupure audio, heure incohérente).
* **Preuve d'authenticité distincte (`2855 C.c.Q.`) :** rappeler qu'une photo, vidéo ou bande audio exige la preuve distincte de son authenticité par témoin (auteur ou personne présente) à moins d'être un document technologique présentant les garanties d'intégrité requises.
* **Captation illicite / vie privée (`2858 C.c.Q.`, `35–36 C.c.Q.`, `c-12 art. 5, 9`) :** signaler tout enregistrement clandestin ou obtenu en violation d'un droit fondamental ou du secret professionnel.

## Force probante

Évaluer le poids probatoire selon la nature du support et le fardeau (`2803–2804 C.c.Q.`) :

* **Contrat ou acte sous seing privé signé (`2826–2829 C.c.Q.`, `262 C.p.c.`) :** Opposé à celui qui paraît l'avoir signé, il est **tenu pour reconnu** s'il n'est pas contesté par déclaration sous serment dans les conditions prévues avant l'inscription (`Établi`). Entre les parties, l'écrit valablement fait ne peut être contredit par témoignage (`2863`), sauf pour l'interpréter (`2864`) ou avec un commencement de preuve (`2865`).
* **Écrit d'entreprise non signé (`2831 C.c.Q.`) :** Fait preuve contre l'entreprise ou entre commerçants s'il a été **habituellement utilisé dans le cours des activités** (factures séquentielles, bons de livraison, grand livre contemporain); distinguer nettement d'un chiffrier ou sommaire reconstitué pour les besoins du litige (`Rapporté` / à établir par le préparateur).
* **Échanges de courriels et messages texte (`2832, 2835, 2837–2840 C.c.Q.`, `c-1.1 art. 5, 7`) :** Exigent d'établir l'attribution à l'auteur (`2835` : fichier `.eml` complet avec en-têtes `Message-ID`/`DKIM`, adresse ou numéro habituel, réponse ultérieure reconnaissant l'échange). Un fil chronologique complet et natif possède une force probante nettement supérieure à une capture d'écran isolée ou recadrée.
* **Photographies et vidéos (`2854–2855 C.c.Q.`, `c-1.1 art. 5 al. 3`) :** Permettent au tribunal de faire ses constatations directes (`2854`) sous réserve d'une **preuve distincte d'authenticité** (`2855` : témoignage du photographe ou d'une personne présente attestant la date, le lieu et l'absence d'altération, sauf garanties d'intégrité technologique sous `c-1.1 art. 5 al. 3`). Les métadonnées EXIF/`mvhd` corroborent la chronologie sans suppléer à elles seules au témoin si l'intégrité est contestée.
* **Enregistrement sonore entre parties (`2855, 2857, 2858, 35–36 C.c.Q.`) :** Exige l'identification fiable de chaque voix, la remise du fichier intégral non édité et le contrôle de licéité sous `2858 C.c.Q.` (atteinte à la vie privée ou au secret professionnel); toute transcription reste une simple aide de travail subordonnée à l'audition de l'original.

## Protection

* Contrôler la présence de tiers non parties, de données biométriques/médicales ou de vie privée (Loi 25, `108 C.p.c.`, `16 C.p.c.`) sur les photos, vidéos et enregistrements.
* Preserver les fichiers natifs originaux sans recompression ni altération des métadonnées.

## Ce que la pièce ne prouve pas

* Une capture d'écran isolée ne prouve ni l'intégrité du fil complet ni l'identité réelle du compte expéditeur sans vérification complémentaire.
* Une métadonnée EXIF ou horodatage modifiable ne prouve pas à lui seul la date réelle sans témoignage corroborant, et son absence (`EXIF_ABSENT_OU_STRIPPE`) signale un retraitement possible (réseau social, messagerie).
* Une transcription non vérifiée mot à mot sur l'original ne prouve jamais les paroles exactes attribuées à un interlocuteur.
