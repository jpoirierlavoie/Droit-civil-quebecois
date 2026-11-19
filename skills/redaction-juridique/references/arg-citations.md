# Discipline de citation et statuts de lecture dans les écrits au tribunal

Fixe les règles strictes de présentation et de vérification des autorités législatives, jurisprudentielles et doctrinales dans tout plan d'argumentation, exposé ou mémoire.

## Destinataire et format

Applicable à tout document destiné à un juge, greffier spécial ou décideur (`plan d'argumentation`, `argumentation écrite`, `exposé`, `mémoire d'appel`). Norme de référence : *Manuel canadien de la référence juridique* (Guide McGill).

## Structure

Ordre civiliste hiérarchisé dans chaque section juridique :
1. **Texte législatif ou réglementaire** (lu via `lois` avec date de consolidation vérifiée, article et alinéa exacts);
2. **Jurisprudence** (Cour suprême du Canada → Cour d'appel du Québec → Cour supérieure / Cour du Québec, par citation neutre + `[par. X]` ou `[par. X–Y]`);
3. **Doctrine** (uniquement de source admissible vérifiée, jamais un traité payant cité de mémoire).

## Discipline de citation

* **Authentification obligatoire (`juris`) :** Chaque décision citée passe par `juris.verify_citations` et `juris.get_case` (citation neutre exacte, date exacte, lien CanLII). Un verdict `DISCORDANTE` disqualifie immédiatement la source.
* **Règle absolue du Palier 3 :** **Aucune proposition décisive ne repose sur un arrêt au statut `Citée`, `Résumée`, `Rapportée` ou `Lue (extrait)` seul.**
  * Pour formuler un *ratio*, la décision officielle complète (PDF ou document complet CanLII/SOQUIJ/CAIJ; jamais un sommaire ni un aperçu web) doit avoir été **lue en session** avec vérification que le passage cité exprime les **motifs majoritaires** (jamais une dissidence ni un *obiter* sans le signaler expressément).
  * Si l'arrêt est confirmé sur `juris` sans lecture intégrale en session : exposer l'assise législative vérifiée via `lois` et poser le marqueur explicite **`[RATIO / PAR. X À INSÉRER APRÈS LECTURE DE <citation + lien CanLII>]`**.

## Pièges

* **Confusion majorité / dissidence / motifs concurrents :** Prêter au tribunal l'opinion d'un juge dissident.
* **Paragraphe inventé ou approximatif :** Inscrire un numéro de paragraphe `[par. 42]` sans l'avoir lu dans le texte officiel complet.
* **Citation d'un sommaire SOQUIJ/CanLII comme ratio :** Ne jamais transformer « la fiche annonce… » en règle de droit jugée par la cour.

## Contrôle

1. Vérifier chaque citation neutre via `juris.verify_citations`.
2. Vérifier chaque renvoi `[par. X]` contre le texte complet lu en session ou maintenir `[RATIO / PAR. X À INSÉRER APRÈS LECTURE DE <citation + lien CanLII>]`.
3. Synchroniser la liste exacte des citations avec le cahier des sources (`production-et-conformite` / `cahier-des-sources.md`).
