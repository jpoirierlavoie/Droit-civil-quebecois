# Grille des préalables et ancrages d'appel

Carte opérationnelle des neuf verrous préalables. **Ne jamais réciter les textes ci-dessous :** appeler en un lot `lois.get_articles` sur les identifiants indiqués avant toute affirmation juridique au Palier 2 ou 3.

## 1. Grille en neuf temps selon le palier

| Palier | Exigence de contrôle et de rédaction |
|---|---|
| **Palier 1 (Rapide)** | Contrôle mental des pièges temporels et de compétence; escalader vers `lois.get_articles` dès qu'une date ou un seuil mord. |
| **Palier 2 (Fiche)** | Vérifier les 9 temps; n'écrire de façon compacte que les rubriques actives plus la prescription. |
| **Palier 3 (Note complète)** | Exécuter et écrire les 4 groupes de rubriques (Qualification/Délai, Avis/Immmunité, Compétence, Qualité/Fins de non-recevoir), même si une rubrique est vide. |

| # | Préalable | Points à trancher |
|---|---|---|
| 1 | **Qualification du recours** | Rapport de droit, régime spécial ou droit commun, cumul contractuel/extracontractuel (art. 1458 C.c.Q.) |
| 2 | **Délai et nature** | Prescription ou déchéance (art. 2878 C.c.Q.), point de départ factuel, suspension, interruption |
| 3 | **Avis préalable** | Avis de réclamation ou mise en demeure légale, délai, sanction, interaction art. 2930 C.c.Q. |
| 4 | **Régime exclusif / immunité** | LATMP, SAAQ, IVAC ou immunité statutaire écartant le recours civil |
| 5 | **Compétence matérielle** | Cour supérieure, Cour du Québec (seuil indexé art. 35), tribunal spécialisé, clause d'arbitrage |
| 6 | **Compétence territoriale / DIP** | District (art. 41 vs 42 C.p.c.), élection de for, litispendance, livre X C.c.Q. (art. 3148) |
| 7 | **Qualité, intérêt, capacité** | Titulaire du droit (art. 85 C.p.c.), mise en cause obligatoire, représentation par avocat |
| 8 | **Fins de non-recevoir** | Chose jugée, transaction, quittance, renonciation |
| 9 | **Moyens préliminaires** | Déclinatoire, irrecevabilité, abus (art. 51, 166–168 C.p.c.) — délais renvoyés à l'administration du litige |

## 2. Vecteurs groupés à charger via `lois.get_articles`

### Prescription, déchéance, suspension et interruption (`law="ccq"`)
Lot recommandé : `numbers=["2878", "2884", "2892", "2895", "2896", "2904", "2905", "2906", "2907", "2908", "2909", "2925", "2926", "2926.1", "2927", "2928", "2929", "2930"]`.

* **Piège structurant (2878) :** La prescription ne peut être suppléée d'office; la **déchéance** résulte d'un texte exprès et **doit** être déclarée d'office.
* **Piège du point de départ (2925–2926) :** Le point de départ est presque toujours une question de fait (connaissance suffisante de la faute, du préjudice et du lien causal), objet principal de la recherche jurisprudentielle.
* **Piège de signification (2892) :** Le dépôt interrompt la prescription à condition de **signifier dans les 60 jours** suivant l'expiration du délai.
* **Piège de grâce (2895) :** Trois mois de grâce après rejet étranger au fond (notification de l'avis du jugement).
* **Piège 2926.1 :** Combine 10 ans (préjudice corporel d'acte criminel), imprescriptibilité (enfance, violence sexuelle ou conjugale) et déchéances de 3 ans liées au décès. Ne jamais résumer en une ligne.
* **Piège 2930 :** En préjudice corporel, aucun avis municipal ni délai plus court ne fait échec au livre VIII.

### Compétence, seuils et moyens préliminaires (`law="cpc"` et `"ccq"`)
Lot recommandé (`cpc`) : `numbers=["33", "35", "41", "42", "51", "85", "166", "167", "168", "535.1", "535.2", "535.3", "535.15"]`; plus `law="ccq"`, `numbers=["1458", "3148"]`.

* **Seuil indexé art. 35 `[seuil indicatif — lire l'article via lois]` :** Cour du Québec exclusive sous `75 000 $`, concurrente de `75 000 $` à moins de `100 000 $` hors intérêts, indexée par tranches de `5 000 $` à la *Gazette officielle*. En Cour du Québec sous art. 35, le **régime simplifié (art. 535.1–535.15)** s'impose (sans protocole, demande `<= 5 pages`, expertise commune sous `50 000 $`). Vérifier le seuil courant à la *Gazette officielle* si le montant approche une borne.
* **Confusion 41 / 42 C.p.c. :** Le domicile du défendeur relève de **41**; **42** n'ajoute que trois fors additionnels au choix du demandeur (contrat, fait générateur/préjudice, immeuble). Élection de for nulle en contrat d'adhésion (art. 41 al. 2).
* **Irrecevabilité (168) :** Non couverte du seul fait de ne pas l'avoir soulevée avant la première conférence de gestion.

## 3. Avis préalables et régimes exclusifs à instancier via `lois.search_text`

Lorsqu'un litige touche une municipalité, un accident, un bâtiment, un emploi ou la consommation, ne jamais présumer le droit commun avant d'interroger `lois.find_relevant` et `lois.search_text` :

| Piste | Mots-clés `lois.search_text` | Exemples de lois au corpus (`lois.list_laws`) |
|---|---|---|
| **Avis préalables** | `"avis préalable"`, `"à peine de déchéance"`, `"quinze jours"` | `c-19` (cités et villes), `c-27.1` (Code municipal), `b-1.1-r.8` |
| **Régimes exclusifs** | `"recours exclusif"`, `"aucun recours"`, `"immunité"` | Lois sectorielles ou fédérales selon la matière |
| **Délais de procédure** | *Hors recherche substantielle* | Renvoyer la chaîne et le calcul à `administration-litige` (`calcul_delai.py` / `outils.calendrier_deadlines`) |
