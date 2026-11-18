# Réception, inspection technique et qualification d'une pièce brute

Couvre l'inspection technique des fichiers bruts, le tri rapide de lots, la distinction entre projet non déposé et acte officiel, ainsi que le contrôle des mentions formelles (C.p.c. / C.c.Q.).

## Qualification

### 1. Tri rapide d'un lot et détection d'anomalies
En mode **Tri**, produire une ligne par fichier sans répéter la prose inutilement (`Nom du fichier | Nature apparente | Date propre | Régime présumé | Signalement`), puis indiquer ce qui reste à lire.
* **Trois signalements systématiques :**
  1. Classement contradictoire avec le nom de fichier (ex. un fichier nommé `Defense_finale.docx` sans numéro de cour et portant des commentaires d'avocat est un **projet préparatoire**, jamais `PUBLIC`).
  2. Divergence avec les autres pièces ou un numéro de greffe incohérent (vérifiable par `outils.greffe_parse_number`).
  3. Jugement allégué avec citation neutre suspecte → authentifier via `juris.verify_citations`.

### 2. Contrôle des mentions exigées (discriminant projet vs déposé)
Appeler `lois.get_articles(law="cpc", numbers=["99", "101", "105", "107", "111", "119", "120", "145", "146", "148", "174", "247", "353", "389", "490"])` au besoin. Ne jamais déduire une mention manquante depuis le nom de fichier.

| Type de document | Mentions critiques à relever | Signal d'absence |
|---|---|---|
| **Acte de procédure** (`cpc` 99) | Tribunal, district, **numéro de dossier de cour**, parties, faits numérotés, conclusions, date, signature, indication des pièces (145, 247) | **Absence de n° de dossier = projet non déposé** (non `PUBLIC`); vérifier s'il s'agit d'une page isolée |
| **Avis d'assignation** (`145–146, 490`) | Modèle ministériel : pièces au soutien indiquées (`145 al. 1`), délai de réponse de `15 jours` (`30 jours` si défendeur sans domicile, résidence ni établissement au Québec, `490`), options et petites créances | Irrégularité formelle ou calcul de défaut prématuré hors Québec |
| **Avis de présentation** (`101`) | Date, heure, salle/palais, notification `>= 3 jours` à l'avance (sauf délai particulier ou urgence), serment joint **si** faits hors dossier (`101 al. 3`) | Présentation prématurée ou faits hors dossier non appuyés du serment |
| **Protocole** (`148`) | Les 9 rubriques obligatoires, modes PRD, temps/coûts, échéances | Incomplet (retour possible) |
| **Jugement / Arrêt** (`389`) | Tribunal, district, n° cour, parties, date, **dispositif**, signature juge (+ noms des juges/dissidences en appel) | Sans dispositif = extrait ou projet; sans motifs en 1re instance = non irrégulier |
| **Procès-verbal de signification** (`119`, `120`) | N° cour, parties, nature signifiée, lieu, **date et heure**, récipiendaire/qualité, refus/échec, frais, serment huissier (+ récépissé si personne désignée) | **Critique** : commande le point de départ et le déplacement `art. 111 al. 2`; signaler tout délai déclenché |
| **Mise en demeure** (`ccq` `1595`) | Sommation précise (objet, défaut, exigence, délai, sanction), date et mode d'envoi | Sans sommation ni délai = simple lettre |
| **Pièce / Facture / Photo** | **Cote (P-1, D-1)**, date propre, auteur, signature (sous seing privé) ou cours habituel des affaires, totaux/devise | **N° de cour / district = sans objet** hors procédure cotée; absence de cote = non encore cotée `PIECE` |

## Authentification et intégrité

**Sur fichiers locaux (`.docx`, `.xlsx`, `.eml`, `.pdf`, `.jpg`, `.png`, `.wav`, `.mp3`, `.mp4`/`.mov`) :** Exécuter d'abord `python scripts/inspecter_piece.py <fichier>... --json` *(avec `--journal` si prise en charge d'un dossier, depuis le dossier de `analyse-et-strategie`)* pour détecter :
* `.docx` : commentaires Word (`COMMENTAIRES_WORD`), marques de révision (`w:ins`/`w:del`), propriétés auteur;
* `.xlsx` : onglets cachés, formules, plages et commentaires;
* `.eml` : en-têtes complets (`From`, `To`, `Cc`, `Bcc`, `X-Unsent` d'un brouillon), pièces jointes (chacune qualifiée séparément);
* `.pdf` : couche texte vs numérisation sans texte (`AUCUNE_COUCHE_TEXTE_DETECTEE` → rasteriser/regarder les pages, ne jamais conclure sur page blanche);
* Images et médias : métadonnées EXIF/conteneur sans déduire la scène ni le son sans perception effective.

**Garde d'angle mort sur clients Web sans exécution Python :** Si `inspecter_piece.py` ne peut pas être exécuté (p. ex. interface web pure), **bloquer tout classement `PUBLIC`** sur un `.docx`, `.xlsx`, `.eml` ou PDF sans texte certain, et signaler explicitement que les commentaires, révisions, formules ou en-têtes cachés n'ont pas pu être inspectés mécaniquement.

## Recevabilité

Vérifier dès la réception si le document est un brouillon interne, une pièce destinée à la production (copie vs original, lisibilité, couche texte) ou un élément nécessitant une analyse approfondie de recevabilité (`preuve-directe.md` ou `preuve-recevabilite-force-probante.md`).

## Force probante

Distinguer d'entrée de jeu ce que la pièce porte par elle-même (date propre, auteur identifié, signature, dispositif) de ce qui reste une allégation ou une donnée non authentifiée. Renvoyer à `preuve-directe.md` ou `preuve-recevabilite-force-probante.md` selon la nature du support.

## Protection

Tout fichier non coté est présumé **`CONFIDENTIEL`**. Tout `.docx`/`.eml`/`.pdf` contenant commentaires internes, révisions non acceptées, `Bcc` ou mention de secret/règlement déclenche immédiatement le contrôle de protection (`preuve-privilege-confidentialite-caviardage.md`).

## Ce que la pièce ne prouve pas

* Le **nom de fichier** ne prouve ni le dépôt au greffe, ni la version finale, ni le caractère public.
* La **date système** du fichier ou de numérisation ne prouve pas la date propre de l'acte ou de l'événement.
* Un **projet non déposé** ou un **brouillon de courriel** (`X-Unsent: 1`) ne prouve ni transmission ni aveu définitif.
