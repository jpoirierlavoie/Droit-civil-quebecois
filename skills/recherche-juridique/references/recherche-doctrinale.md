# Recherche doctrinale et filtrage web

Encadre la recherche doctrinale web au Québec sans fuite de confidentialité et avec exclusion absolue du droit étranger.

## Sources et outils

**Règle de requête web :** Toujours inclure un marqueur québécois (`"Québec"`, `"C.c.Q."`, `"Cour d'appel du Québec"`, numéro d'article québécois). **Ne jamais inclure un nom de partie, montant ou fait identifiant du dossier.**

| Catégorie | Sources admissibles (liste blanche) | Portée et limites |
|---|---|---|
| **Officiel & institutionnel** | LégisQuébec, Publications du Québec, Barreau du Québec (*Développements récents* en partie indexés), Chambre des notaires, MJQ, Tribunaux du Québec, Éducaloi | Éducaloi sert à orienter seulement, jamais cité en note formelle |
| **Doctrine savante** | Érudit (*Cahiers de droit*, *R.J.T.*, *R. du N.*, *R.G.D.*), *Revue du Barreau*, *McGill Law Journal*, dépôts universitaires (Papyrus, Corpus UL, eScholarship McGill), CanLII Connects | **Barrière mobile ~12 mois** sur les revues Érudit : l'absence de résultat récent n'est pas un silence doctrinal — renvoyer au CAIJ |
| **Bulletins de cabinets & blogues** | Langlois, Lavery, Fasken, BLG, McCarthy, Norton Rose, Stikeman, Osler, Gowling, BCF, TCJ, Cain Lamarre, Dunton Rainville, De Grandpré Chait, Miller Thomson, Robic; Lexology/Mondaq; blogues SOQUIJ et CRL | Sources **secondaires** utiles pour repérer des arrêts récents; toujours authentifier chaque arrêt cité via `juris.verify_citations` |
| **Payant / hors d'atteinte** | Traités Baudouin, Jobin/Vézina, Lluelles/Moore, *JurisClasseur Québec*, fonds complets SOQUIJ et CAIJ | **Ne jamais citer un traité de mémoire** — inscrire l'ouvrage à consulter dans les vérifications suggérées au CAIJ |

Outils d'appui linguistique : `outils.terminologie_lookup`, `outils.termino_attestations`, `outils.terminologie_scan`.

## Séquence

1. **Formuler des requêtes abstraites** ciblées sur le concept juridique et un marqueur québécois.
2. **Filtrer les sources étrangères avant même d'extraire un principe :** rejeter intégralement toute source `.fr` (Légifrance, Dalloz, Village de la Justice, doctrine.fr, LexisNexis France, Cour de cassation, Conseil d'État), belge, suisse ou luxembourgeoise. **Test rapide :** présence des art. `1240`, `1382`, `2224`, `1641`, `1134`, *référé*, *assignation*, *pourvoi en cassation*, *tribunal judiciaire*, *SARL*. Un seul marqueur écarte toute la source.
3. **Éviter la transposition mécanique de common law :** écarter *limitation period*, *duty of care*, *consideration*, *estoppel*; retenir les arrêts de la Cour suprême du Canada et le droit fédéral applicables au Québec.
4. **Extraire les citations d'arrêts repérées** et les authentifier obligatoirement via `juris.verify_citations`.

## Statuts de lecture

* Une proposition issue d'un article doctrinal ou d'un bulletin de cabinet sans lecture de l'arrêt cité porte le statut **`Rapportée`** (« selon l'auteur X… »), jamais une attribution directe au tribunal.
* Un texte payant ou derrière barrière mobile (`Érudit` < 12 mois, traités) n'est jamais cité de mémoire : le consigner comme piste de vérification au CAIJ / SOQUIJ.

## Modes d'échec

* **Contamination française ou de common law :** Rejet immédiat dès détection d'un marqueur étranger.
* **Hallucination de citations dans un billet :** Toute citation dont `juris.verify_citations` retourne `DISCORDANTE` entraîne le rejet complet du billet source.
* **Accès web indisponible ou limité :** Signaler la limite d'accès et indiquer les traités et fonds CAIJ/SOQUIJ à vérifier manuellement par l'avocat.
