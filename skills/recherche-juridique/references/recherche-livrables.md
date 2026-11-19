# Statuts de lecture et gabarits des livrables de recherche

Calibre les trois formats de livraison de la recherche juridique et fixe le seuil probatoire exigible selon le palier.

## Sources et outils

* `lois.get_articles` : assise législative vérifiée avec date de consolidation.
* `juris.verify_citations` et `juris.get_case` : authentification CanLII et lien officiel.
* Décisions complètes téléversées en session (PDF ou document complet CanLII/SOQUIJ/CAIJ) pour atteindre le statut `Lue (intégrale) [par. X]`.

## Séquence

1. **Respecter le budget d'autorités :** Viser **3 à 5 autorités vérifiées** (loi au bon alinéa + arrêt de principe C.A./C.S.C. + 1–2 applications + autorité contraire). Zéro arrêt vaut mieux qu'un remplissage douteux.
2. **Sélectionner le gabarit selon la demande et le palier :**
   * **Vérification ponctuelle (ou contrôle de citations) :** Réponse directe + texte consolidé, ou tableau `| Citation annoncée | Intitulé annoncé | Verdict | Fiche réelle |` suivi de 3 lignes max de verdict global (`DISCORDANTE` invalide la source entière).
   * **Fiche (1 page, Palier 2) :** `## Question` · `## Réponse courte` · `## Préalables` *(rubriques actives + prescription)* · `## Législation` *(avec date de consolidation)* · `## Jurisprudence` *(avec statuts)* · `## Attaque adverse` · `## Réserves et vérifications` · `## Registre des sources`.
   * **Note de recherche (complète, Palier 2–3) :** Même ossature plus `## Doctrine` et `## Application aux faits`, avec les 4 groupes de préalables écrits même s'ils sont vides, prose suivie et tableau final :

| Autorité | Statut | Provenance | Vérifiée |
|---|---|---|---|
| art. X C.c.Q. | Texte officiel | `lois.get_articles` (consolidé AAAA-MM-JJ) | oui |
| Citation neutre | `Résumée` / `Lue [par. X]` | `juris.verify_citations` / texte intégral fourni (PDF) | oui / à lire |

## Statuts de lecture

| Statut | Ce qui est vérifié | Usage autorisé dans le livrable |
|---|---|---|
| **Citée** | `juris.verify_citations` → `CONFIRMÉE` | Nommer l'arrêt, le tribunal et la date seulement |
| **Résumée** | + fiche et mots-clés `juris.get_case` | Indiquer l'objet annoncé **en l'attribuant à la fiche** (« la fiche annonce… ») |
| **Rapportée** | Mentionnée par un auteur identifié | Attribuer nommément à l'auteur (« selon X… »), jamais à la cour |
| **Lue (extrait) `[par. X]`** | Passage exact vérifié majoritaire *(insuffisant seul au Palier 3)* | Citer le passage exact au Palier 2 *(au Palier 3, lecture intégrale du texte officiel [PDF ou document complet CanLII/SOQUIJ/CAIJ] requise avant de conclure sur le ratio)* |
| **Lue (intégrale) `[par. X]`** | Décision lue intégralement dans la session (texte intégral officiel — PDF ou document complet CanLII/SOQUIJ/CAIJ; jamais un sommaire ou aperçu web) | Énoncer le *ratio*, citer `[par. X]`, fonder une plaidoirie ou un avis (Palier 3) |

**Seuil du Palier 3 (tribunal / avis formel) :** Aucune proposition décisive ne repose au-dessous de `Lue (intégrale) [par. X]` (décision complète lue en session, motifs majoritaires vérifiés; un extrait partiel ne lève pas le marqueur). Sans texte intégral officiel fourni et lu en session, présenter l'argumentation législative vérifiée et maintenir `[RATIO / PAR. X À INSÉRER APRÈS LECTURE DE <citation + lien CanLII>]`.

## Modes d'échec

* **Sur-citation de sommaire :** Présenter un résumé CanLII/web ou une note doctrinale comme un ratio jugé par le tribunal.
* **Absence de Registre des sources :** Livrer une fiche ou note sans tracer les statuts de lecture ni la date de consolidation législative.
* **Oubli de l'attaque adverse :** Ne pas formuler le meilleur argument contraire ni les écarts face aux hypothèses du dossier.
