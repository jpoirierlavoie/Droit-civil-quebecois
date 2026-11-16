# Ouverture de dossier, conflits, identification et mandat

Structure l'ouverture conforme d'un dossier, l'analyse des conflits et la rédaction des clauses essentielles de mandat/honoraires. **Lire les textes cités via `lois.get_articles` (`b-1-r.3.1`, `b-1-r.5`, `cpc`) avant de valider un avis ou un modèle.**

## 1. Grille d'ouverture de dossier (`Règl. 11, 13, 14, 20–27`; `Code 29, 64, 71–88`)

| Étape | Contrôle à effectuer | Outillage |
|---|---|---|
| **1. Conflit d'intérêts** | Client actuel, ancien client (`87` préjudice ou avantage indu), mandats communs (`83–84` : 3 informations + consentement; client régulier `86`), secret d'un autre client (`64`), avocat témoin (`76`), juge lié (`79–80`). En cas de conflit complexe ou changeant de cabinet : consulter le syndic (`70`). | `lois.get_articles` (`b-1-r.3.1`) |
| **2. Compétence & temps (`29`)** | Domaines visés, charge disponible, besoin d'un co-procureur ou collaborateur (informer le client selon `30` si exécution essentielle par un tiers). | `lois.get_article` |
| **3. Identification (`Règl. 13–14`)** | **Toujours requise** (même sans avance) : nom, adresse, téléphone, occupation (personne physique); dénomination, n° constitution, nature des activités, dirigeants autorisés (personne morale); identité du tiers bénéficiaire s'il y a lieu. | `outils.registre_search`, `registre_get_entity`, `adresse_verify` *(instantanés hors ligne sans administrateurs physiques — vérifier au REQ au besoin)* |
| **4. Vérification d'identité (`Règl. 20–27`)** | **Déclenchée seulement** s'il y a réception, déboursé ou virement de fonds **autrement que par transfert électronique** (vérifier les dispenses `Règl. 21`, dont honoraires/débours/avances ou règlement de procédure!). Personne physique : document fiable indépendant au plus tard à la réception; Société : existence, nom, adresse, administrateurs et détenteurs `>= 25 %` dans les **60 jours** (`26(2°)`). Client hors vue : mandataire par entente écrite ou répondant canadien (`24–25`). | `lois.get_articles` (`b-1-r.5` `20–27`) + `calcul_delai.py` (60 jours) |

## 2. Mandat, portée limitée et modalités financières (`Code 28, 31, 34, 99–108`; `Règl. 54–55`)

*Note sur la forme :* Aucune convention d'honoraires écrite générale n'est imposée par le Code, mais l'écrit demeure indispensable en bonne pratique et **obligatoire** pour : intérêts conventionnels sur comptes en souffrance (`103`), rémunération forfaitaire (`104`), entente de disponibilité acquise (`Règl. 54(2), 55`).

| Clause du mandat / lettre d'engagement | Exigence déontologique |
|---|---|
| **Objet et étendue (`28`, `31`)** | Décrire précisément ce qui est inclus et **exclu** (p. ex. appel, exécution forcée, vérification fiscale); si mandat à portée limitée (`31`), énoncer les limites sans atténuer les devoirs professionnels. |
| **Risques et PRD (`28, 34, 42`)** | Exposer objectivement les risques et coûts; vérifier l'admissibilité à l'aide juridique (`34`); informer sur les modes privés de PRD (`42`). |
| **Base financière (`99–104`)** | Taux horaire, forfait écrit (`104`), pourcentage/résultat (noter `109` inopérant), provision/avance en fidéicommis vs disponibilité acquise écrite (`Règl. 54–55`), politique d'intérêts sur souffrance écrite (`103`), avis de variation importante des coûts (`99`), avantages reçus de tiers (`108`). |
| **Technologie & confidentialité (`21, 60–63`)** | Consentement ou cadre clair sur le courriel, l'infonuagique sécurisée et la conservation (au moins 7 ans après fermeture, `Règl. 18`). |

## 3. Gestion courante du lien client et fin de mandat

* **Comptes périodiques & offres (`40, 43, 47`) :** Rappeler le devoir d'informer de l'évolution (`40`), de soumettre **toute** offre de règlement (`43`) et de dénoncer rapidement toute omission préjudiciable (`47`).
* **Cessation d'agir (`Code 48–52`, `C.p.c. 192, 194`) :** Vérifier motif sérieux (`48` dont défaut de payer après préavis raisonnable) vs cessation obligatoire (`49`); appliquer les mesures conservatoires (`52`), remettre pièces/fonds (`57, 97`), notifier client/parties/greffier (`194`) et obtenir l'autorisation du tribunal si la date d'instruction est fixée (`194 al. 2`).
