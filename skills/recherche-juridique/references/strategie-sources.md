# Méthode d'interrogation des sources primaires (`lois`, `juris`, `outils`)

Règles d'emploi des connecteurs, méthode de la boule de neige jurisprudentielle et gestion stricte des modes d'échec. **Aucun champ de recherche libre `query` (`lois.find_relevant`, `lois.search_text`) ni aucune recherche web ne doit recevoir de noms de clients ou faits identifiants** (seuls `outils` — sans journalisation — et `juris.find_case`/`verify_citations` sur décisions publiées reçoivent des noms ou adresses).

## 1. Capacités et limites des connecteurs

| Capacité | `lois` (LégisQuébec / Justice Canada) | `juris` (CanLII métadonnées) | `outils` (tables locales hors ligne) |
|---|---|---|---|
| **Texte intégral** | **Oui**, verbatim, consolidation courante | **Non** (métadonnées et mots-clés seulement) | Glossaires, registres ouverts REQ/Fed, RQA, MJQ |
| **Recherche par sujet** | **Oui** (`search_text` hybride + `find_relevant`) | **Non** (nom de parties ou citation uniquement) | Recherche d'entreprises, adresses, termes FR/EN |
| **Historique / versions** | **Non** (pas de versions abrogées ni ancien C.p.c. c. C-25) | Indice heuristique (`subsequent_history`) | S.O. |
| **Défaillance / hors ligne** | **Arrêt obligatoire** sur le volet législatif | **Arrêt obligatoire** sur la vérification | Repli sur le script Python local de `administration-litige` pour les délais |

* **Corpus législatif fermé (`lois`) :** Une absence de résultat signifie que le texte n'est pas dans les 97 lois du corpus, **jamais** qu'aucune règle n'existe. Confirmer à LégisQuébec si une loi récente ou un amendement de dernière heure est en cause, et toujours reporter la `date de consolidation`.
* **Restriction de loi dans `search_text` :** Éviter de filtrer sur une seule loi sans certitude : une recherche filtrée qui renvoie un faux ami bloque l'élargissement automatique au corpus et crée un faux négatif silencieux.

## 2. Séquence optimale `lois` (économie de jetons)

1. `find_relevant(query)` ou `list_laws(subject/forum)` si la loi exacte est inconnue.
2. `get_structure(law)` (ou `get_division(..., include_text=false)`) pour repérer les numéros d'articles sans charger tout un chapitre.
3. `get_articles(law, numbers=[...])` en **un seul appel groupé** pour tous les articles d'une même loi, plutôt que `N` appels séquentiels `get_article`.
4. `related_laws(law)` pour vérifier les règlements d'application et textes habilitants.

## 3. La méthode de la boule de neige sur `juris`

`juris` ne cherche pas par mots du jugement. Procéder depuis un ancrage issu du dossier, de l'avocat ou de la doctrine de liste blanche :

1. **Filtrer hors ligne :** `parse_citation` écarte les citations mal formées avant d'occuper un lot CanLII.
2. **Authentifier en lot :** `verify_citations` accepte jusqu'à **25 citations** en un appel (avec `refresh=false` par défaut pour ménager le quota CanLII).
3. **Interpréter les 6 verdicts :**
   * `CONFIRMÉE` : citation exacte; enchaîner sur `get_case` pour lire l'intitulé, la date exacte et les **mots-clés** (source riche d'arrêts de principe et d'articles liés).
   * `DISCORDANTE` : la citation existe mais désigne une autre décision que celle annoncée — **alerte critique d'hallucination IA**, écarter entièrement la source qui l'a produite.
   * `NON CONSTRUCTIBLE` : renvoi de recueil (`R.C.S.`, `R.J.Q.`, `C.A.`) ou d'éditeur (`J.E.`, `REJB`, `EYB`, `AZ`) — enchaîner avec `find_case` sur le nom des parties.
   * `INTROUVABLE` : couverture historique ou délai de diffusion CanLII; ne prouve pas l'inexistence.
   * `ILLISIBLE` / `INDÉTERMINÉE` : vérification **non effectuée** (quota `429` ou panne); ne jamais assimiler à `INTROUVABLE`.
4. **Piège critique de `find_case` :** Les dates retournées par `find_case` sont approximatives (souvent `AAAA-01-01`). **Toujours confirmer la date exacte avec `get_case`.**
5. **Piège de `browse_cases` :** Trie par **date de diffusion CanLII**, non par date de jugement (écart parfois > 2 ans en C.S.). Pour reconstituer un ordre chronologique réel, récolter puis appeler `verify_citations`.
6. **Étendre et arrêter tôt :** `citator(rel="cited" | "citing" | "legislation")` sur 2–3 itérations max (note : le graphe ne remonte pas d'un article vers les jugements qui le citent). Signaler que `subsequent_history` est purement heuristique (ne détecte ni infirmation sans intitulé voisin, ni pourvoi pendant, ni refus de permission d'appeler).

## 4. Exploitation de jugements téléversés (PDF/texte)

Lorsque l'avocat fournit des décisions tirées de SOQUIJ, CAIJ ou CanLII :
* Vérifier d'abord la citation neutre via `juris.verify_citations`.
* Vérifier dans la décision si le passage cité exprime les motifs **majoritaires** (jamais une dissidence ni un *obiter* isolé sans le signaler).
* Extraire le renvoi précis `[par. X]` ou `[par. X–Y]` et élever le statut à `Lue (extrait)` (ou à `Lue (intégrale)` si la décision complète est fournie et lue en session).

## 5. Modes d'échec et arrêt obligatoire

* **`401`, `404`, `429`, `QUOTA_EPUISE`, `INDÉTERMINÉE` ou `INTERROMPU` :** S'arrêter sur le volet touché, nommer le connecteur et le code/cause retourné, et **ne jamais basculer silencieusement sur la mémoire ni sur le web** pour combler un texte législatif ou une vérification de citation.
* **`[CLEF_ABSENTE]` ou `[CLEF_REFUSEE]` sur `juris` :** L'interrogation de `juris` (y compris la lecture de son index local partagé) exige strictement la clé API CanLII personnelle active du praticien (BYOK). S'arrêter sur la vérification jurisprudentielle et inviter l'avocat à déposer ou renouveler sa clé CanLII dans `acces.poirierlavoie.ca/moi` (ou par en-tête `X-Clef-CanLII`).
* **`hybride_desactive: true` sur `lois.search_text` :** Lorsque le compte titulaire a désactivé la recherche vectorielle hybride (`hybride_permis = 0` dans `acces.poirierlavoie.ca/moi`), `search_text` s'exécute strictement en mode lexical `FTS5` local ; combiner alors synonymes exacts du texte et `find_relevant`.
* **Contradiction web vs connecteur :** Le connecteur primaire l'emporte sans discussion; signaler la divergence.
