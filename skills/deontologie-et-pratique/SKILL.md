---
name: deontologie-et-pratique
description: >-
  Signaler les obligations déontologiques (Code b-1-r.3.1, Règlement b-1-r.5, art. 192–194 C.p.c.)
  et gérer la pratique du dossier : conflits d'intérêts, identification et vérification du client,
  mandat, feuilles de temps, facturation éthique, fidéicommis, conservation et fin de mandat. En
  anglais — legal ethics, conflict of interest, client ID, retainer, timesheets, billing narrative,
  trust account, withdrawal. Ne pas utiliser pour l'état des frais taxés (administration-litige) ni
  la responsabilité civile (recherche-juridique).
---

# Déontologie professionnelle et gestion de la pratique

Nomme au texte les devoirs de l'avocat québécois devant tout déclencheur concret et outille l'ouverture de dossier, la facturation conforme et le contrôle en fidéicommis sans jamais attester qu'un geste a été posé.

<!-- SAFETY-KERNEL:START -->
## Garde-fous impératifs

1. **Confidentialité stricte :** Ne jamais inclure de noms de parties, faits identifiants, extraits de pièces ou numéros de dossier dans une requête de recherche web.
2. **Sources primaires obligatoires (arrêt en cas d'indisponibilité) :** Ne jamais réciter un article, un délai, un seuil indexé ou le ratio d'un arrêt de mémoire. Lire le texte officiel via `lois` (`get_article` / `get_articles`), authentifier toute décision via `juris` (`verify_citations`), et exécuter les calculs via `outils` (`calendrier_deadlines`, `interets_1619`, ou `calcul_delai.py`). Si un connecteur requis est injoignable ou non configuré (`401`, `404`, hors ligne), **s'arrêter**, nommer le connecteur manquant et demander à l'avocat de le reconnecter ou de fournir le texte.
3. **Étanchéité bijuridique :** Écarter tout droit étranger (`.fr`, Belgique, Suisse; art. 1240, 2224, 1641) et purger les calques de common law (*duty of care*, *consideration*, *estoppel*, dommages punitifs sans loi habilitante sous l'art. 1621 C.c.Q.). En anglais, employer exclusivement la terminologie officielle anglaise du C.c.Q. et du C.p.c. (`get_article(lang="en")`, `terminologie_lookup`).
4. **Protection et déclencheurs déontologiques :** Présumer tout document non coté `CONFIDENTIEL` (jamais `PUBLIC` par défaut). Signaler au texte via `lois` (`b-1-r.3.1`, `b-1-r.5`, `cpc` art. 108, 192–194) une obligation déontologique ou de caviardage uniquement devant un fait déclencheur concret, sans mise en garde générique.
<!-- SAFETY-KERNEL:END -->

## Paliers de rigueur

| Palier | Contexte | Exigence de source et de rendu |
|---|---|---|
| **Palier 1 — Signal / Question rapide** | Vérification ponctuelle « puis-je / dois-je », incident soudain | Lire immédiatement les articles déclenchés via `lois.get_articles` (jamais de mémoire); nommer ce que le texte **exige**, **permet** et **tait**. |
| **Palier 2 — Feuille de temps / Ouverture / Lettre** | Compilation de notes en entrées facturables, liste d'accueil ou mandat | Vérifier les textes applicables via `lois`, contrôler les entités via `outils.registre_search`/`adresse_verify`, produire des libellés sans secret professionnel divulgué. |
| **Palier 3 — Audit fidéicommis / Cessation / Avis critique** | Espèces `>= 7 500 $`, retrait après fixation, conflit complexe, réclamation client | Lecture intégrale via `lois` (`b-1-r.3.1`, `b-1-r.5`, `cpc`), vérification des délais via `outils.calendrier_deadlines` (ou renvoi à `echeanciers-cpc.md`), rappel du syndic (`Code 70`) si cas difficile. |

## Routage des tâches et feuilles

Charger au plus une ou deux feuilles locales selon la tâche (jamais de renvoi vers un autre `SKILL.md`) :

| Intention de la demande | Feuille locale à lire | Connecteurs d'entrée |
|---|---|---|
| Question déontologique (« puis-je / dois-je »), partie représentée, témoin, usage d'IA, confidentialité ou cessation d'occuper | `references/radar-deontologique.md` | `lois` (`get_articles` sur `b-1-r.3.1`, `b-1-r.5`, `cpc`) |
| Ouverture de dossier, conflits d'intérêts, identification / vérification du client, mandat et convention d'honoraires | `references/identification-conflits-et-mandat.md` | `lois` (`get_articles`), `outils` (`registre_search`, `registre_get_entity`, `adresse_verify`) |
| Transformer des notes en feuilles de temps, rédiger des libellés de facture (art. 102/104), contrôler le fidéicommis ou les espèces | `references/facturation-temps-et-fideicommis.md` | `lois` (`get_articles` sur `b-1-r.3.1`, `b-1-r.5`) |
| Délai déontologique à compter (10 j mise en demeure 192 C.p.c., 30 j accès 55/58 ou espèces 71, 60 j société 26) | `../administration-litige/references/echeanciers-cpc.md` *(si absent : `outils.calendrier_deadlines`)* | `outils` (`calendrier_deadlines`) ou `calcul_delai.py` |
| Lettre au client, convention d'honoraires formelle ou avis écrit à rédiger | `../redaction-juridique/references/correspondance-et-contrats.md` *(si absent : rédiger avec `lois`)* | `lois`, `outils` (`terminologie_scan`) |

## Règle de posture absolue

1. **Rappeler, jamais attester :** Dire qu'une vérification (conflit, identité, conciliation) est due; ne jamais écrire qu'elle a été accomplie à moins d'en voir la preuve directe.
2. **Distinguer devoir écrit et simple usage :** Ne jamais présenter une coutume de courtoisie ou une préférence de gestion comme une règle du Code.
3. **Pertinence stricte :** Hors déclencheur concret ou question directe, n'ajouter aucune clause déontologique générique.

## Contrôle avant remise

1. **Texte vérifié :** Chaque article (`b-1-r.3.1`, `b-1-r.5`, `cpc`) a été lu via `lois` dans la session (ou refus explicite si `lois` est indisponible).
2. **Exige / permet / tait :** Les silences pertinents du Code sont explicités sans être comblés; les numéros confondables (`48/49`, `13–14/20–27`, `192/194`) sont distingués.
3. **Délais et recours :** Délais chiffrés via `outils`/`calcul_delai.py`; recours au bureau du syndic (`Code 70`) mentionné devant un doute sérieux sur la confidentialité ou un conflit aigu.
4. **Hors champ nommé :** Devoirs généraux (`Code 1–19`), publicité/exercice en société (`124 s.`), dispositions liminaires (`Règl. 1–10`) et responsabilité civile (`recherche-juridique`) nommés comme hors champ s'ils surviennent et lus directement via `lois` au besoin.
