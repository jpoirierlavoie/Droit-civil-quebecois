# Recherche jurisprudentielle et vérification CanLII (`juris`)

Encadre la méthode de la boule de neige sur `juris`, le contrôle des citations et l'exploitation des décisions fournies par l'avocat.

## Sources et outils

| Capacité | `juris` (CanLII métadonnées) | Limite critique |
|---|---|---|
| **Texte intégral** | **Non** (métadonnées, intitulé et mots-clés seulement) | Ne jamais prêter un ratio depuis une simple fiche `get_case` |
| **Recherche par sujet** | **Non** (nom de parties `find_case` ou citation uniquement) | Utiliser des ancrages issus du dossier, de l'avocat ou de la doctrine de liste blanche |
| **Graphe / citateur** | `citator(rel="cited" \| "citing" \| "legislation")` | Ne remonte pas d'un article vers tous les jugements qui le citent |
| **Sort ultérieur** | `subsequent_history` (indice heuristique) | Ne détecte ni infirmation sans intitulé voisin, ni pourvoi pendant, ni refus de permission d'appeler |
| **Listes d'autorités dispensées** | `list_exempt_cases` (hors ligne) et `check_exempt_cases` (27 listes, 9 tribunaux) | Dispense procédurale de reproduction au cahier des sources uniquement ; n'établit NI l'autorité actuelle NI le dispositif |

## Séquence

1. **Filtrer hors ligne :** `juris.parse_citation` écarte les citations mal formées avant d'occuper un lot CanLII.
2. **Authentifier en lot :** `juris.verify_citations` accepte jusqu'à **25 citations** en un appel (avec `refresh=false` par défaut pour ménager le quota CanLII). Transmettre systématiquement `{citation, expected_title, expected_year}` dès qu'un intitulé ou une année figurent au texte (ou en tête de citation neutre) afin de déjouer les combinaisons fabriquées.
3. **Interpréter les 6 verdicts :**
   * `CONFIRMÉE` : citation exacte; enchaîner sur `juris.get_case` pour lire l'intitulé, la date exacte et les **mots-clés** (source riche d'arrêts de principe et d'articles liés).
   * `DISCORDANTE` : la citation existe mais désigne une autre décision que celle annoncée — **alerte critique d'hallucination IA**. Toutefois, devant un `appariement partiel` où la **citation neutre** (année, tribunal et numéro) concorde mais que l'intitulé diverge par une abréviation ou variante courante (`St`/`Saint`, `P.G.`/`Procureure générale`, forme féminine, `Cie`/`Compagnie`), comparer d'abord les noms complets des parties et vérifier la fiche `juris.get_case` avant d'écarter l'arrêt.
   * `NON CONSTRUCTIBLE` : renvoi de recueil (`R.C.S.`, `R.J.Q.`, `C.A.`) ou d'éditeur (`J.E.`, `REJB`, `EYB`, `AZ`) — enchaîner avec `juris.find_case` sur le nom des parties.
   * `INTROUVABLE` : couverture historique ou délai de diffusion CanLII; ne prouve pas l'inexistence.
   * `ILLISIBLE` / `INDÉTERMINÉE` : vérification **non effectuée** (quota `429` ou panne); ne jamais assimiler à `INTROUVABLE`.
4. **Piège de `find_case` :** Les dates retournées par `find_case` sont approximatives (souvent `AAAA-01-01`). **Toujours confirmer la date exacte avec `juris.get_case`.**
5. **Piège de `browse_cases` :** Trie par **date de diffusion CanLII**, non par date de jugement (écart parfois > 2 ans en C.S.). Pour reconstituer un ordre chronologique réel, récolter puis appeler `verify_citations`.
6. **Étendre et arrêter tôt :** `juris.citator` sur 2–3 itérations max.
7. **Jugements téléversés (PDF/texte complet SOQUIJ, CAIJ, CanLII) :** Vérifier d'abord la citation neutre via `verify_citations`, confirmer que le passage cité exprime les motifs **majoritaires** (jamais une dissidence ni un *obiter* isolé sans le signaler), et relever `[par. X]` ou `[par. X–Y]`.

## Statuts de lecture

Chaque arrêt doit porter exactement l'un de ces statuts :
* `Citée` (`verify_citations` → `CONFIRMÉE`)
* `Résumée` (+ fiche et mots-clés `get_case`)
* `Rapportée` (mentionnée par une source doctrinale identifiée)
* `Lue (extrait) [par. X]` (passage vérifié majoritaire, insuffisant seul au Palier 3)
* `Lue (intégrale) [par. X]` (décision complète officielle lue en session)

Au Palier 3, toute décision non lue intégralement en session reste sous le marqueur `[RATIO / PAR. X À INSÉRER APRÈS LECTURE DE <citation + lien CanLII>]`.

## Modes d'échec

* **`401`, `403`, `404`, `429`, `QUOTA_EPUISE`, `INDÉTERMINÉE` ou `INTERROMPU` sur `juris` :** **Arrêt obligatoire sur la vérification jurisprudentielle** (sur un `403` sur requête libre, reformuler d'abord sans opérateurs ni guillemets ; s'il persiste, s'arrêter). Nommer le connecteur `juris` et le code/cause retourné, inviter l'avocat à rétablir l'accès sur `acces.poirierlavoie.ca/moi` ; ne jamais inventer un arrêt ni substituer un aperçu web à une lecture intégrale.
* **`[CLEF_ABSENTE]` ou `[CLEF_REFUSEE]` sur `juris` :** L'interrogation de `juris` (y compris la lecture de son index local partagé) exige strictement la clé API CanLII personnelle active du praticien (BYOK). S'arrêter sur la vérification jurisprudentielle et inviter l'avocat à déposer ou renouveler sa clé CanLII dans `acces.poirierlavoie.ca/moi` (ou par en-tête `X-Clef-CanLII`) — seuls `parse_citation`, `list_exempt_cases` et `check_exempt_cases` (`resolve_canlii=false`) demeurent utilisables hors ligne sans clé.
* **Contradiction web vs `juris` :** La fiche et la citation authentifiée sur `juris` l'emportent sans discussion.
