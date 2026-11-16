# Doctrine admissible, statuts de lecture et gabarits de livraison

Encadre la recherche doctrinale web (sans fuite de confidentialité) et calibre les livrables de recherche selon le statut probatoire de chaque autorité.

## 1. Liste blanche doctrinale et filtrage web

**Règle de requête :** Toujours ajouter un marqueur québécois (`"Québec"`, `"C.c.Q."`, `"Cour d'appel du Québec"`, numéro d'article québécois). Ne **jamais** inclure un nom de partie, montant ou fait identifiant du dossier.

| Catégorie | Sources admissibles | Portée et limites |
|---|---|---|
| **Officiel & institutionnel** | LégisQuébec, Publications du Québec, Barreau du Québec (*Développements récents* en partie indexés), Chambre des notaires, MJQ, Tribunaux du Québec, Éducaloi | Éducaloi sert à orienter seulement, jamais cité en note formelle |
| **Doctrine savante** | Érudit (*Cahiers de droit*, *R.J.T.*, *R. du N.*, *R.G.D.*), *Revue du Barreau*, *McGill Law Journal*, dépôts universitaires (Papyrus, Corpus UL, eScholarship McGill), CanLII Connects | **Barrière mobile ~12 mois** sur les revues Érudit : l'absence de résultat récent n'est pas un silence doctrinal — renvoyer au CAIJ |
| **Bulletins de cabinets & blogues** | Langlois, Lavery, Fasken, BLG, McCarthy, Norton Rose, Stikeman, Osler, Gowling, BCF, TCJ, Cain Lamarre, Dunton Rainville, De Grandpré Chait, Miller Thomson, Robic; Lexology/Mondaq; blogues SOQUIJ et CRL | Sources **secondaires** utiles pour repérer des arrêts récents; toujours authentifier chaque arrêt cité via `juris.verify_citations` |
| **Payant / hors d'atteinte** | Traités Baudouin, Jobin/Vézina, Lluelles/Moore, *JurisClasseur Québec*, fonds complets SOQUIJ et CAIJ | **Ne jamais citer un traité de mémoire** — inscrire l'ouvrage à consulter dans les vérifications suggérées au CAIJ |

**Exclusion systématique de la France et civilistes étrangers :** Rejeter intégralement toute source `.fr` (Légifrance, Dalloz, Village de la Justice, doctrine.fr, LexisNexis France, Cour de cassation, Conseil d'État), belge, suisse ou luxembourgeoise. **Test rapide :** présence des art. 1240, 1382, 2224, 1641, 1134, *référé*, *assignation*, *pourvoi en cassation*, *tribunal judiciaire*, *SARL*. Un seul marqueur écarte toute la source. Qualifier sans transposer mécaniquement la common law canadienne (*limitation period*, *duty of care*); retenir les arrêts de la Cour suprême du Canada et le droit fédéral.

## 2. Échelle du statut de lecture (voyage avec l'autorité)

| Statut | Ce qui est vérifié | Usage autorisé dans le livrable |
|---|---|---|
| **Citée** | `juris.verify_citations` → `CONFIRMÉE` | Nommer l'arrêt, le tribunal et la date seulement |
| **Résumée** | + fiche et mots-clés `juris.get_case` | Indiquer l'objet annoncé **en l'attribuant à la fiche** (« la fiche annonce… ») |
| **Rapportée** | Mentionnée par un auteur identifié | Attribuer nommément à l'auteur (« selon X… »), jamais à la cour |
| **Lue (extrait) `[par. X]`** | Passage exact vérifié majoritaire *(insuffisant seul au Palier 3)* | Citer le passage exact au Palier 2 *(au Palier 3, lecture intégrale du texte officiel [PDF ou document complet CanLII/SOQUIJ/CAIJ] requise avant de conclure sur le ratio)* |
| **Lue (intégrale) `[par. X]`** | Décision lue intégralement dans la session (texte intégral officiel — PDF ou document complet CanLII/SOQUIJ/CAIJ; jamais un sommaire ou aperçu web) | Énoncer le *ratio*, citer `[par. X]`, fonder une plaidoirie ou un avis (Palier 3) |

**Seuil du Palier 3 (tribunal / avis formel) :** Aucune proposition décisive ne repose au-dessous de `Lue (intégrale) [par. X]` (décision complète lue en session, motifs majoritaires vérifiés; un extrait partiel ne lève pas le marqueur). Sans texte intégral officiel fourni et lu en session (PDF ou document complet CanLII/SOQUIJ/CAIJ; un sommaire ou aperçu web ne lève jamais le marqueur), présenter l'argumentation législative vérifiée et maintenir `[RATIO / PAR. X À INSÉRER APRÈS LECTURE DE <citation + lien CanLII>]`.

## 3. Budget et structure des trois livrables

Viser **3 à 5 autorités vérifiées** (loi au bon alinéa + arrêt de principe C.A./C.S.C. + 1–2 applications + autorité contraire). Zéro arrêt vaut mieux qu'un remplissage douteux.

1. **Vérification ponctuelle (ou contrôle de citations) :** Réponse directe + texte consolidé, ou tableau `| Citation annoncée | Intitulé annoncé | Verdict | Fiche réelle |` suivi de 3 lignes max de verdict global (`DISCORDANTE` invalide la source entière).
2. **Fiche (1 page) :** `## Question` · `## Réponse courte` · `## Préalables` *(rubriques actives + prescription)* · `## Législation` *(avec date de consolidation)* · `## Jurisprudence` *(avec statuts)* · `## Attaque adverse` · `## Réserves et vérifications` · `## Registre des sources`.
3. **Note de recherche (complète) :** Même ossature plus `## Doctrine` et `## Application aux faits`, avec les 4 groupes de préalables écrits même s'ils sont vides, prose suivie et tableau final :

| Autorité | Statut | Provenance | Vérifiée |
|---|---|---|---|
| art. X C.c.Q. | Texte officiel | `lois.get_articles` (consolidé AAAA-MM-JJ) | oui |
| Citation neutre | `Résumée` / `Lue [par. X]` | `juris.verify_citations` / texte intégral fourni (PDF) | oui / à lire |
