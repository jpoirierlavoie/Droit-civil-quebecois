---
name: recherche-juridique
description: >-
  Utiliser dès qu'une question porte sur le droit civil ou commercial québécois applicable
  (C.c.Q., C.p.c., lois RLRQ ou fédérales), même simple : vice caché, contrat, bail,
  responsabilité, hypothèque, garantie, solidarité, prescription, déchéance, avis préalable,
  compétence du tribunal, fondement d'un recours, recherche ou vérification d'arrêts CanLII et
  doctrine. En anglais — use for Quebec legal research, statutory rules, latent defects,
  liability, lease, prescription, limitation period, jurisdiction, case law citation check. Ne
  pas utiliser pour rédiger un acte ou contrat (redaction-juridique), inspecter une pièce
  (analyse-juridique) ni calculer une échéance procédurale (administration-litige).
---

# Recherche juridique québécoise

Établit le droit applicable, les verrous préalables et les autorités vérifiées à partir des sources primaires (`lois`, `juris`, `outils`) et de la doctrine admissible.

<!-- SAFETY-KERNEL:START -->
## Garde-fous impératifs

1. **Confidentialité stricte :** Ne jamais inclure de noms de clients, faits identifiants, extraits de pièces ou numéros de dossier dans une recherche web ni dans un champ de recherche libre `query` (`lois.find_relevant`, `lois.search_text`). Sont seuls permis : les dénominations, adresses et numéros de greffe soumis aux outils sans journalisation de `outils` (`registre_search`, `adresse_verify`, `greffe_parse_number`) et les intitulés de décisions publiées dans `juris` (`find_case`, `verify_citations`).
2. **Sources primaires obligatoires (arrêt sur le volet touché) :** Ne jamais réciter un article, un délai, un seuil indexé ou le ratio d'un arrêt de mémoire. Repérer les trois connecteurs par leurs outils signatures — y compris s'ils sont différés (les charger par recherche d'outils avant de conclure à leur absence) ou nommés sous un alias client (`legis` / `Législation`, `Jurisprudence`, `Outils`) : `lois` (`get_article`, `get_articles`), `juris` (`verify_citations`, `get_case`) et `outils` (`calendrier_deadlines`, `interets_1619`). Si le connecteur requis échoue (`401`, `404`, hors ligne) sans repli local prévu par la compétence, **s'arrêter sur le volet touché**, nommer le connecteur et demander à l'avocat de le reconnecter ou de fournir le texte officiel.
3. **Étanchéité bijuridique :** Écarter tout droit étranger (`.fr`, Belgique, Suisse; art. 1240, 2224, 1641) et purger les calques de common law (*duty of care*, *consideration*, *estoppel*, dommages punitifs sans loi habilitante sous l'art. 1621 C.c.Q.). En anglais, employer exclusivement la terminologie officielle anglaise du C.c.Q. et du C.p.c. (`get_article(lang="en")`, `terminologie_lookup`).
4. **Protection et déclencheurs déontologiques :** Présumer tout document non coté `CONFIDENTIEL` (jamais `PUBLIC` par défaut). Signaler au texte via `lois` (`b-1-r.3.1`, `b-1-r.5`, `cpc` art. 108, 192–194) une obligation déontologique ou de caviardage uniquement devant un fait déclencheur concret, sans mise en garde générique.
<!-- SAFETY-KERNEL:END -->

## Paliers de rigueur

Choisir selon la destination (modifiable sur demande; **Palier 2 par défaut** si ambigu) : question orale ponctuelle → Palier 1; travail interne de dossier → Palier 2; écrit externe ou au tribunal → Palier 3.

| Palier | Contexte | Exigence de sources et livrable |
|---|---|---|
| **Palier 1 — Rapide / Remue-méninges** | Exploration, question ponctuelle informelle | Raisonner en concepts sans deviner aucun numéro d'article ni d'arrêt de mémoire (`[À VÉRIFIER VIA LOIS]`). **Escalade dynamique obligatoire** vers le Palier 2 dès qu'une date de prescription, un délai d'appel, un seuil de compétence ou un avis préalable est en jeu. |
| **Palier 2 — Note ou fiche de travail** | Analyse d'un dossier, avis interne | Vérifier chaque texte décisif via `lois` (`get_articles`), authentifier les arrêts via `juris` (`verify_citations`), noter le statut de lecture de chaque décision et formuler l'attaque adverse. |
| **Palier 3 — Écrit au tribunal / Externe** | Appui à une plaidoirie, avis formel au client | Contrôle intégral : aucune proposition décisive ne repose au-dessous du statut `Lue (intégrale) [par. X]` (texte intégral officiel fourni et lu en session — PDF ou document complet CanLII/SOQUIJ/CAIJ; jamais un sommaire ou aperçu web —, motifs majoritaires vérifiés). Si `juris` confirme l'arrêt sans texte intégral lu, **écrire le fondement législatif vérifié** et maintenir `[RATIO / PAR. X À INSÉRER APRÈS LECTURE DE <citation + lien CanLII>]`. |

## Routage des tâches et feuilles

Charger au plus une ou deux feuilles locales selon la tâche (jamais de renvoi vers un autre `SKILL.md`) :

| Intention de la demande | Feuille locale à lire | Connecteurs d'entrée |
|---|---|---|
| Vérifier prescription, déchéance, compétence, avis préalables, régimes exclusifs ou DIP | `references/grille-prealables.md` | `lois` (`get_articles`, `search_text`), `outils` (`greffe_parse_number`) |
| Interroger les sources primaires (`lois`, `juris`), faire la boule de neige ou exploiter des PDF fournis | `references/strategie-sources.md` | `lois` (`find_relevant`, `get_structure`, `get_articles`), `juris` (`parse_citation`, `verify_citations`, `get_case`, `citator`) |
| Chercher de la doctrine web, filtrer `.fr`, classer le statut de lecture et livrer (ponctuel, fiche, note) | `references/doctrine-et-livrables.md` | Recherche web (liste blanche), `outils` (`terminologie_lookup`, `termino_attestations`) |
| Délai d'instance ou échéance procédurale C.p.c. détecté | `../administration-litige/references/echeanciers-cpc.md` *(si absent : appeler `lois` sur `cpc` et `outils.calendrier_deadlines`)* | `outils` (`calendrier_deadlines`), `lois` (`get_articles`) |
| Déclencheur déontologique concret (conflit, confidentialité, délai échu par faute de l'avocat) | `../deontologie-et-pratique/references/radar-deontologique.md` *(si absent : appeler `lois` sur `b-1-r.3.1`)* | `lois` (`get_articles`) |

## Ordre d'exécution

1. **Capter l'appui factuel** depuis les fichiers locaux, documents téléversés ou faits donnés par l'avocat; marquer tout fait manquant `[À CONFIRMER]` sans jamais l'inventer.
2. **Traiter l'urgence d'abord :** si une prescription ou un délai est imminent, le signaler en tête de réponse avant le fond.
3. **Décomposer en questions de droit** (qualification, norme, conditions, défenses, réparation, forum, prescription).
4. **Exécuter les préalables** selon le palier (`references/grille-prealables.md`).
5. **Lire la loi à la source** (`lois`) en relevant la date de consolidation et la loi applicable dans le temps (fait générateur en droit substantiel vs date courante en procédure).
6. **Croiser doctrine (liste blanche) et jurisprudence (`juris`)** sans jamais prêter à un arrêt un ratio non lu dans son texte intégral ou un extrait majoritaire vérifié.
7. **Présenter l'attaque adverse la plus forte** et livrer avec le Registre des sources.

## Contrôle avant remise

1. **Connecteurs vérifiés :** Tous les textes cités ont été lus via `lois` (avec date de consolidation) ou marqués `[À VÉRIFIER VIA LOIS]` au Palier 1; aucun arrêt de mémoire ni ratio tiré d'un simple sommaire.
2. **Statuts de lecture :** Chaque arrêt porte `Citée`, `Résumée`, `Rapportée`, `Lue (extrait) [par. X]` ou `Lue (intégrale) [par. X]`; au Palier 3, les arrêts dont le texte intégral officiel (PDF/document complet) n'est pas lu en session restent sous crochet `[RATIO / PAR. X À INSÉRER APRÈS LECTURE DE <citation + lien CanLII>]`.
3. **Épuration :** Zéro source `.fr`, belge ou suisse; zéro transposition mécanique de common law; zéro donnée client dans une requête web.
4. **Attaque adverse et écarts :** Meilleur argument contraire formulé; toute contradiction avec les hypothèses du dossier placée en tête.
