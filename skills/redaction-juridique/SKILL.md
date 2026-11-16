---
name: redaction-juridique
description: >-
  Rédiger ou réviser tout écrit civil ou commercial québécois en français ou en anglais : demande
  introductive (ordinaire ou simplifiée C.Q.), défense, demande en cours d'instance, déclaration sous
  serment, plan d'argumentation, mémoire/déclaration d'appel, cahier des sources, mise en demeure,
  lettre et contrat/transaction. En anglais — draft pleading, originating application, demand letter,
  argument outline, appellate brief, book of authorities, contract, redline. Ne pas utiliser pour
  établir le droit (recherche-juridique) ni calculer des délais (administration-litige).
---

# Rédaction juridique québécoise

Convertit des faits et un droit vérifiés en écrits québécois complets et étanches aux réflexes français et de common law.

<!-- SAFETY-KERNEL:START -->
## Garde-fous impératifs

1. **Confidentialité stricte :** Ne jamais inclure de noms de parties, faits identifiants, extraits de pièces ou numéros de dossier dans une requête de recherche web.
2. **Sources primaires obligatoires (arrêt en cas d'indisponibilité) :** Ne jamais réciter un article, un délai, un seuil indexé ou le ratio d'un arrêt de mémoire. Lire le texte officiel via `lois` (`get_article` / `get_articles`), authentifier toute décision via `juris` (`verify_citations`), et exécuter les calculs via `outils` (`calendrier_deadlines`, `interets_1619`, ou `calcul_delai.py`). Si un connecteur requis est injoignable ou non configuré (`401`, `404`, hors ligne), **s'arrêter**, nommer le connecteur manquant et demander à l'avocat de le reconnecter ou de fournir le texte.
3. **Étanchéité bijuridique :** Écarter tout droit étranger (`.fr`, Belgique, Suisse; art. 1240, 2224, 1641) et purger les calques de common law (*duty of care*, *consideration*, *estoppel*, dommages punitifs sans loi habilitante sous l'art. 1621 C.c.Q.). En anglais, employer exclusivement la terminologie officielle anglaise du C.c.Q. et du C.p.c. (`get_article(lang="en")`, `terminologie_lookup`).
4. **Protection et déclencheurs déontologiques :** Présumer tout document non coté `CONFIDENTIEL` (jamais `PUBLIC` par défaut). Signaler au texte via `lois` (`b-1-r.3.1`, `b-1-r.5`, `cpc` art. 108, 192–194) une obligation déontologique ou de caviardage uniquement devant un fait déclencheur concret, sans mise en garde générique.
<!-- SAFETY-KERNEL:END -->

## Paliers de rigueur

| Palier | Contexte | Exigence de fond et de contrôle |
|---|---|---|
| **Palier 1 — Ébauche rapide / Canevas** | Premier jet, restructuration, reformulation sur faits fournis | Appliquer la forme québécoise exacte; marquer toute donnée absente `[À CONFIRMER]` et toute assise non vérifiée `[à vérifier]` sans inventer d'articles. |
| **Palier 2 — Brouillon de travail** | Mise en demeure, lettre, contrat, projet d'acte | Vérifier les textes habilitants et seuils via `lois`; vérifier les entreprises/adresses via `outils` (`registre_search`, `adresse_verify`); distinguer faits `Établi` vs `Rapporté`. |
| **Palier 3 — Acte prêt au dépôt / Externe** | Acte de procédure, plan d'argumentation, appel, cahier des sources | Contrôle intégral : textes et règlements de cour lus via `lois`, **aucune autorité décisive sous `Lue (extrait) [par. X]`** (sinon insérer `[RATIO / PAR. X À INSÉRER APRÈS LECTURE DE <citation + lien CanLII>]`), contrôle `outils.terminologie_scan`, cotes continues et liste des vérifications hors texte. |

## Mode de sortie et routage des feuilles

* **Mode complet par défaut (actes de cour) :** Inclut cartouche (`CANADA / PROVINCE DE QUÉBEC / DISTRICT DE [...]`), intitulé, corps numéroté, `POUR CES MOTIFS`, signature `[À COMPLÉTER]` (+ avis d'assignation et endos pour une demande introductive).
* **Mode « Bloc pour gabarit du cabinet » (sur demande) :** Corps pur sans cartouche, sans signature et sans Markdown (intertitres en majuscules, gras réservé aux cotes `**Pièce P-1**`).

Charger au plus une ou deux feuilles locales (jamais de renvoi vers un autre `SKILL.md`) :

| Type d'écrit | Feuille locale à lire | Connecteurs d'entrée |
|---|---|---|
| Demande introductive (ordinaire ou C.Q. simplifiée 535.1), défense, reconvention, demande en cours d'instance, protocole, déclaration sous serment, modification (206–208) | `references/actes-de-procedure.md` | `lois` (`get_articles`), `outils` (`registre_*`, `adresse_verify`, `interets_1619`, `greffe_parse_number`) |
| Plan d'argumentation, déclaration/exposé/mémoire d'appel, cahier des sources | `references/argumentation-appel-et-sources.md` | `lois` (`c-25.01-r.0.2.01`, `r.0.2.1`, `r.9`), `juris` (`verify_citations`, `get_case`) |
| Mise en demeure, lettre (confrère, client, tribunal), contrat, transaction, quittance | `references/correspondance-et-contrats.md` | `lois` (`get_articles`), `outils` (`interets_1619`, `registre_*`, `adresse_verify`) |
| Révision d'un texte douteux ou rédaction en **anglais** devant un forum québécois | `references/anti-contamination-bilingue.md` | `outils` (`terminologie_scan`, `terminologie_lookup`, `termino_attestations`), `lois` (`get_article(lang="en")`) |
| Fondement juridique non encore établi en amont | `../recherche-juridique/references/grille-prealables.md` *(si absent : appeler `lois` et `juris`)* | `lois`, `juris` |
| Risque de caviardage (`art. 108`, Loi 25) ou fait déclencheur déontologique (partie représentée `120`) | `../analyse-juridique/references/preuve-et-protection.md` ou `../deontologie-et-pratique/references/radar-deontologique.md` | `lois` (`get_articles`) |

## Contrôle avant remise

1. **Assise factuelle :** Aucune date, montant, désignation ni cote inventé (`[À CONFIRMER]` apparent, repris hors bloc); faits tirés d'une simple déclaration du client signalés comme `Rapporté`.
2. **Séparation droit / faits :** Zéro article ni jurisprudence dans un acte de procédure (sauf article habilitant sous le titre et compétence du tribunal) ou une mise en demeure; citations complètes et vérifiées dans un plan d'argumentation ou mémoire.
3. **Épuration :** Zéro marqueur français (`PAR CES MOTIFS`, `assignation`, art. 1240/2224/1641) ni calque de common law; exécuter `outils.terminologie_scan` sur le projet au Palier 3.
4. **Sobriété et langue :** Langue du dossier (en anglais : terminologie officielle du C.c.Q./C.p.c., `UNDER ALL RESERVES` vs `WITHOUT PREJUDICE`); couper les adjectifs émotifs.
