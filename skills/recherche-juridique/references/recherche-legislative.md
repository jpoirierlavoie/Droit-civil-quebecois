# Recherche législative et réglementaire (`lois`)

Encadre l'interrogation du corpus législatif et réglementaire québécois et fédéral via `lois`. **Aucun champ de recherche libre `query` (`lois.find_relevant`, `lois.search_text`) ne doit recevoir de noms de clients ou faits identifiants.**

## Sources et outils

| Capacité | `lois` (LégisQuébec / Justice Canada) | Limite critique |
|---|---|---|
| **Texte intégral** | **Oui**, verbatim, consolidation courante | Vérifier toujours et reporter la `date de consolidation` |
| **Recherche par sujet** | **Oui** (`search_text` hybride + `find_relevant`) | Corpus fermé (97 lois indexées) : un résultat vide ne prouve jamais l'inexistence d'une règle |
| **Historique / versions** | **Non** (pas de versions abrogées ni ancien C.p.c. c. C-25) | Confirmer la loi applicable dans le temps (fait générateur en droit substantiel vs date courante en procédure) |
| **Règlements & directives** | `related_laws` pour lois habilitantes et règlements de cour | Vérifier à LégisQuébec ou sur les sites des tribunaux si un amendement récent est en cause |

* **Restriction de loi dans `search_text` :** Éviter de filtrer sur une seule loi sans certitude : une recherche filtrée qui renvoie un faux ami bloque l'élargissement automatique au corpus et crée un faux négatif silencieux.

## Séquence

1. `lois.find_relevant(query)` ou `lois.list_laws(subject/forum)` si la loi exacte est inconnue (requête en concepts abstraits, zéro nom ni fait identifiant).
2. `lois.get_structure(law)` (ou `lois.get_division(..., include_text=false)`) pour repérer les numéros d'articles sans charger tout un chapitre.
3. `lois.get_articles(law, numbers=[...])` en **un seul appel groupé** pour tous les articles d'une même loi, plutôt que `N` appels séquentiels `get_article`.
4. `lois.related_laws(law)` pour vérifier les règlements d'application, lois habilitantes et règles de pratique (`c-25.01-r.0.2.1`, `c-25.01-r.9`, `c-25.01-r.0.2.01`, `t-16-r.10`).
5. `lois.resolve_reference(citation)` ou `lois.get_article(law, article, lang="en")` pour obtenir l'équivalent anglais officiel exact.

## Statuts de lecture

* **Texte officiel consolidé (`lois`) :** Article lu intégralement via `lois.get_article` / `get_articles` / `get_division` avec sa **date de consolidation** relevée en session.
* **`[À VÉRIFIER VIA LOIS]` :** Réservé uniquement au Palier 1 exploratoire; **interdit** au Palier 2 ou 3.
* **Loi hors corpus :** Si une loi récente ou sectorielle manque au corpus `lois`, indiquer explicitement l'absence au corpus et demander à l'avocat de fournir le texte consolidé depuis LégisQuébec / Justice Canada.

## Modes d'échec

* **`404`, `401` ou hors ligne sur `lois` :** **Arrêt obligatoire sur le volet législatif.** Nommer le connecteur `lois` et le code/cause retourné; **ne jamais basculer silencieusement sur la mémoire ni sur le web** pour reconstituer un article ou un seuil indexé.
* **Contradiction web vs `lois` :** Le texte officiel retourné par `lois` l'emporte sans discussion; signaler la divergence.
