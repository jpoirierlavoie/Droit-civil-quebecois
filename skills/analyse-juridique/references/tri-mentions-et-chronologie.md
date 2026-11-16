# Inspection technique, tri rapide, mentions et chronologie

Couvre l'inspection technique des fichiers bruts, le tri rapide de lots, la vérification des mentions formelles (C.p.c. / C.c.Q.) et l'extraction de chronologies factuelles fiables.

## 1. Inspection technique obligatoire avant toute conclusion

**Sur fichiers locaux (`.docx`, `.xlsx`, `.eml`, `.pdf`, `.jpg`, `.png`) :** Exécuter d'abord `python skills/analyse-juridique/scripts/inspecter_piece.py <fichier>... --json` pour détecter :
* `.docx` : commentaires Word (`COMMENTAIRES_WORD`), marques de révision (`w:ins`/`w:del`), propriétés auteur;
* `.xlsx` : onglets cachés, formules, plages et commentaires;
* `.eml` : en-têtes complets (`From`, `To`, `Cc`, `Bcc`, `X-Unsent` d'un brouillon), pièces jointes (chacune qualifiée séparément);
* `.pdf` : couche texte vs numérisation sans texte (`AUCUNE_COUCHE_TEXTE_DETECTEE` → rasteriser/regarder les pages, ne jamais conclure sur page blanche);
* Images : métadonnées EXIF, sans déduire la date/auteur de la scène au-delà de ce qui est visible.

**Garde d'angle mort sur clients Web sans exécution Python :** Si `inspecter_piece.py` ne peut pas être exécuté (p. ex. interface web pure), **bloquer tout classement `PUBLIC`** sur un `.docx`, `.xlsx`, `.eml` ou PDF sans texte certain, et signaler explicitement que les commentaires, révisions, formules ou en-têtes cachés n'ont pas pu être inspectés mécaniquement.

## 2. Tri rapide d'un lot et détection d'anomalies

En mode **Tri**, produire une ligne par fichier sans répéter la prose inutilement (ex. `Nom du fichier | Nature apparente | Date propre | Régime présumé | Signalement`), puis indiquer ce qui reste à lire.
* **Trois signalements systématiques :**
  1. Classement contradictoire avec le nom de fichier (ex. un fichier nommé `Defense_finale.docx` sans numéro de cour et portant des commentaires d'avocat est un **projet préparatoire**, jamais `PUBLIC`).
  2. Divergence avec les autres pièces ou un numéro de greffe incohérent (vérifiable par `outils.greffe_parse_number`).
  3. Jugement allégué avec citation neutre suspecte → authentifier via `juris.verify_citations`.

## 3. Contrôle des mentions exigées (le discriminant du projet vs déposé)

Appeler `lois.get_articles(law="cpc", numbers=["99", "101", "105", "107", "111", "119", "120", "145", "148", "174", "247", "353", "389"])` au besoin. Ne jamais déduire une mention manquante depuis le nom de fichier.

| Type de document | Mentions critiques à relever | Signal d'absence |
|---|---|---|
| **Acte de procédure** (`cpc` 99) | Tribunal, district, **numéro de dossier de cour**, parties, faits numérotés, conclusions, date, signature, indication des pièces (145, 247) | **Absence de n° de dossier = projet non déposé** (non `PUBLIC`); vérifier s'il s'agit d'une page isolée |
| **Avis d'assignation** (`145`) | Pièces au soutien indiquées, délai de réponse de 15 jours | Irrégularité formelle |
| **Protocole** (`148`) | Les 9 rubriques obligatoires, modes PRD, temps/coûts, échéances | Incomplet (retour possible) |
| **Jugement / Arrêt** (`389`) | Tribunal, district, n° cour, parties, date, **dispositif**, signature juge (+ noms des juges/dissidences en appel) | Sans dispositif = extrait ou projet; sans motifs en 1re instance = non irrégulier |
| **Procès-verbal de signification** (`119`, `120`) | N° cour, parties, nature signifiée, lieu, **date et heure**, récipiendaire/qualité, refus/échec, frais, serment huissier (+ récépissé si personne désignée) | **Critique** : commande le point de départ et le déplacement `art. 111 al. 2`; signaler tout délai déclenché |
| **Mise en demeure** (`ccq` `1595`) | Sommation précise (objet, défaut, exigence, délai, sanction), date et mode d'envoi | Sans sommation ni délai = simple lettre |
| **Pièce / Facture / Photo** | **Cote (P-1, D-1)**, date propre, auteur, signature (sous seing privé) ou cours habituel des affaires, totaux/devise | **N° de cour / district = sans objet** hors procédure cotée; absence de cote = non encore cotée `PIECE` |

## 4. Chronologie factuelle

Extraire une suite d'événements datés (un document est une **source**, non un événement).
* **Date propre uniquement :** Jamais la date système de création/numérisation/téléversement du fichier.
* **Précisions de date :** Exacte (`2025-11-12`), encadrée (`~2025-11`, `entre 2025-11-04 et 2025-11-12`), ou inconnue (`[DATE]`). Noter l'heure et le fuseau si deux gestes surviennent le même jour (signification, offre).
* **Format :** `| Date | Événement | Source (pièce, page/courriel) | Statut (Établi / Rapporté / Déduit) |`
* **Pied obligatoire :** Lister `[TROU]` (intervalles critiques sans pièce), **Contradictions** (deux pièces incompatibles présentées face à face sans trancher) et **Pièces sans événement**. Signaler les dates d'ancrage procédurales à `administration-litige`.
