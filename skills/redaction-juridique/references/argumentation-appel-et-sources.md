# Plan d'argumentation, actes d'appel et cahier des sources

Rédige les documents argumentatifs remis au tribunal — où les citations juridiques, interdites dans les actes introductifs, constituent la substance même du texte.

## 1. Plan d'argumentation (première instance)

Document sommaire destiné au **juge**, jamais substituable à une conclusion absente de la procédure (une conclusion oubliée exige un amendement, pas une plaidoirie). Consulter les règlements de pratique via `lois` (`c-25.01-r.0.2.1` C.S., `c-25.01-r.0.2.2`/`r.0.2.3`, `c-25.01-r.9` C.Q.) pour les limites de pages et délais de remise.

| Contexte | Structure type |
|---|---|
| **Défaut / Au fond après enquête** | `RÉSUMÉ` (1–2 par., thème et demande claire dès le 1er par.) → `CADRE JURIDIQUE` (ordre civiliste : texte → jurisprudence → doctrine) → `APPLICATION AUX FAITS` (avec cotes/témoignages exacts) → `CONCLUSIONS RECHERCHÉES` (**mot pour mot** de la procédure) |
| **Moyen préliminaire (`166–168`)** | Moyen soulevé → critère et source → application (faits allégués tenus pour avérés sur irrecevabilité) → conclusions |
| **Demande interlocutoire / Injonction (`510–511`)** | Critères un par section (apparence de droit, préjudice sérieux/irréparable, urgence, balance des inconvénients) → conclusions |
| **En défense** | Résumé → admis vs contesté → cadre juridique → conclusions en rejet |

* **Discipline impérative de citation (Palier 3) :**
  * Suivre le *Manuel canadien de la référence juridique* (citation neutre + `[par. X]` majoritaire).
  * **Aucune proposition décisive ne repose sur un arrêt non lu intégralement (`Résumée`, `Rapportée` ou `Lue (extrait)` seul).** Si `juris.verify_citations` et `juris.get_case` confirment l'arrêt mais que le PDF complet n'est pas téléversé et lu intégralement en session : exposer l'assise législative lue via `lois` et maintenir le crochet explicite **`[RATIO / PAR. X À INSÉRER APRÈS LECTURE DE <citation + lien CanLII>]`**.
* **Ce qui ne franchit jamais la porte du tribunal :** Aveu de faiblesse formulé comme tel (« notre point faible est… » → reformuler : « la partie adverse soutiendra que…, mais… »), risque de recouvrement, objectifs secrets du client, plancher de règlement, provision/honoraires, évaluation interne d'un témoin.

## 2. Déclaration d'appel, exposé et mémoire d'appel (`C.p.c.` & `c-25.01-r.0.2.01`)

**Appeler `lois.get_articles` avant de rédiger tout acte d'appel :**
* `law="cpc"`, `numbers=["352", "353", "357", "358", "360", "361", "365", "372", "373", "374", "376"]`
* `law="c-25.01-r.0.2.01"` (*Règlement de la Cour d'appel du Québec en matière civile*) : inspecter la structure (`get_structure`) pour charger les exigences de format, typographie, nombre de pages et annexes.

| Acte d'appel | Points critiques |
|---|---|
| **Déclaration d'appel (`352–353`)** (+ demande de permission le cas échéant `357`) | Tribunal et date du jugement entrepris, nature du litige/valeur, appel de plein droit vs permission, énoncé concis des moyens d'erreur (droit, erreur manifeste et déterminante en faits), conclusions d'appel, attestation de signification/notification (`358`). |
| **Exposé (`374`)** | Pour appels en matière familiale, intégrité/état/capacité, non contentieux, saisie, jugement en cours d'instance ou sur gestion; format abrégé soumis au règlement et à la décision de gestion. |
| **Mémoire d'appel (`372–373`)** | Parties, énoncé commun (si déposé, `372 al. 2`) ou exposé des faits et questions en litige, argumentation structurée par question (norme d'intervention pour chacune), conclusions, annexes I (jugement entrepris), II (actes de procédure/textes légaux) et III (pièces et dépositions pertinentes). |

## 3. Cahier des sources / Book of Authorities

Vérifier les exigences particulières du tribunal et du district via `lois` (`c-25.01-r.0.2.1`, `c-25.01-r.9`, `c-25.01-r.0.2.01`) — notamment les directives sur le dépôt électronique avec hyperliens vs reproduction d'extraits.

1. **Correspondance 1:1 :** Chaque autorité citée au plan ou au mémoire — et rien d'autre — figure au cahier, classée en trois onglets : **Législation**, **Jurisprudence**, **Doctrine**.
2. **Authentification préalable :** Chaque arrêt passe par `juris.verify_citations` et `juris.get_case` (récupérant l'hyperlien officiel CanLII et la citation neutre exacte).
3. **Structure du cahier généré :**
   * Table des matières / Index numéroté (`Onglet | Autorité & citation complète | Paragraphes ou articles pertinents | Statut de lecture | Hyperlien CanLII / LégisQuébec`).
   * Fiche par onglet : reproduction de l'article consolidé (`lois`) ou extraits vérifiés majoritaires `[par. X–Y]` tirés du PDF complet lu en session, ou crochet `[EXTRAITS [PAR. X] ET COPIE PDF À JOINDRE DE <citation + lien CanLII>]` si le jugement complet n'a pas encore été lu intégralement.
