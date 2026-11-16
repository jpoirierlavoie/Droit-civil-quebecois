# Feuilles de temps, facturation éthique et contrôle en fidéicommis

Transforme les notes brutes d'activité en feuilles de temps/factures conformes au Code de déontologie (`b-1-r.3.1`) et encadre les contrôles de fidéicommis (`b-1-r.5`). **Lire les textes cités via `lois.get_articles` avant toute validation formelle.**

## 1. Feuilles de temps et libellés de facturation (`Code 99–104, 110`)

Lire `lois.get_articles(law="b-1-r.3.1", numbers=["60", "99", "100", "101", "102", "104", "110"])`.

* **Compilation depuis notes brutes / journaux :**
  * Extraire en tableau Markdown (ou `.csv` `utf-8-sig` avec formules `=SOMME(...)` / `=SUM(...)`) :
    `| Date | Intervenant | Catégorie (Recherche / Rédaction / Pièces / Audience / Admin) | Libellé client (art. 104) | Durée réelle (h) | Taux / Montant ($) | Facturable / Exclu |`
* **Rédaction éthique du libellé (`104` vs `60`) :**
  * **Décrire le service sans exposer la stratégie privilégiée :** Écrire « Analyse des pièces communiquées et préparation du projet d'exposé sommaire (par. 1 à 15) » plutôt que de révéler des aveux, doutes tactiques ou avis secrets sur un relevé susceptible d'être produit lors d'une demande de frais ou de révision.
  * **Proportionnalité et temps comprimé par l'IA (`101, 102(2°)`) :** Ne **jamais** gonfler ni facturer d'heures fictives lorsque des outils numériques ou modèles accélèrent la rédaction; ajuster selon les 9 facteurs de l'art. 102 (difficulté, importance, résultat, urgence, temps réellement consacré) et la convention convenue (`99`).
  * **Exclusions obligatoires (`110`) :** Tout temps consacré à répondre au bureau du syndic ou à une demande d'inspection du Barreau est **strictement non facturable** au client (`110`).
  * **Débours technologiques / tiers (`99, 101`) :** Exiger l'accord préalable et facturer au coût réel sans majoration cachée.
  * **Avis de dépassement (`99`) :** Signaler dès qu'un cumul approche ou dépasse l'estimation donnée au client.

## 2. Contrôle des mouvements en fidéicommis (`b-1-r.5` art. 28–73, `Code 94–97`)

Lire `lois.get_articles(law="b-1-r.5", numbers=["30", "38", "39", "40", "41", "42", "50", "52", "53", "54", "56", "57", "58", "59", "60", "62", "69", "70", "71", "72"])`.

| Règle de contrôle | Exigence du Règlement (`b-1-r.5`) |
|---|---|
| **Séparation des dépôts (`50, 52–54`)** | Déposer **sans délai** au compte général en fidéicommis toute avance non encore facturée (`50`). **Ne jamais y déposer** une avance pour honoraires/débours *déjà facturés* ni une somme acquise par entente écrite de disponibilité (`54`). Si une somme indivisible est mixte, déposer le tout et retirer sans délai la part non fiduciaire (`53`). |
| **Compte particulier (`62–66`)** | Obligatoire sans délai après le dépôt général dès que le client exige les intérêts/revenus de son dépôt (`62`). |
| **Retraits permis (`56–60`)** | Jamais plus que le solde de la carte-client du dossier (`59`); combler **sans délai** tout solde débiteur (`60`). Retrait pour honoraires permis **seulement après envoi de la facturation** (`56(2°)`), par chèque à l'ordre de l'avocat ou virement vers son compte non fiduciaire (`58`). **Aucun retrait en espèces**, au porteur ou à « caisse » (`57`, sauf remboursement sous `72`). |
| **Espèces et plafond de `7 500 $` (`69–73`)** | `[À VÉRIFIER VIA LOIS]` : reçu obligatoire à **6 mentions** signé par l'avocat et le remettant pour **toute** somme en espèces (`70`); plafond de `7 500 $` par mandat sauf 6 exceptions dont avance d'honoraires/débours (`69`); si `>= 7 500 $`, déclaration au directeur de l'inspection professionnelle dans les **30 jours** (`71`) et tout remboursement se fait **en espèces** (`72`). |
| **Registres & conciliation (`38–42`)** | Journal de caisse avec solde courant (`38`), registre des cartes-clients (`39`), conciliation mensuelle à 4 voies (`40–41`), rapport annuel (`42` — dans les **30 jours** d'une demande d'inspection) et conservation **7 ans** (`31–32`). |

## 3. Gabarits rapides de contrôle (carte-client & appel de provision)

* **Vérification d'une carte-client :** `| Date | Mode / Réf. | Libellé & facture liée | Entrée ($) | Sortie ($) | Solde dossier ($) | Alerte Règl. (54/56/59/69) |`
* **Appel de provision / renouvellement (`Code 99, 101`, `Règl. 50`) :** Rappel sobre des travaux accomplis, facturation transmise ou imminente, montant d'avance demandé au compte en fidéicommis, date requise, et rappel de l'art. `48(3)` seulement si un préavis de défaut de paiement devient nécessaire.
