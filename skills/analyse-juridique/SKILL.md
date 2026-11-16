---
name: analyse-juridique
description: >-
  Utiliser pour analyser un dossier, bâtir une stratégie ou examiner des pièces brutes (.pdf,
  .docx, .xlsx, .eml, images, notes sténo) : remue-méninges contradictoire, forces et
  faiblesses, théorie de la cause, recevabilité, force probante, ouï-dire, secret professionnel,
  privilège de litige ou de règlement, caviardage Loi 25, tri de pièces, mentions exigées,
  chronologie et interrogatoire préalable (plan, engagements, objections). En anglais — use for
  Quebec case strategy, brainstorming, evidence review, privilege, redaction, timeline,
  pre-trial examination, undertakings, objections. Ne pas utiliser pour établir le droit
  abstrait (recherche-juridique), rédiger un acte (redaction-juridique) ni compter un délai
  (administration-litige).
---

# Analyse juridique, stratégie et preuve

Évalue la stratégie d'un litige, mène le remue-méninges contradictoire et qualifie les documents bruts (nature, mentions, protection, valeur probante, chronologie, interrogatoires).

<!-- SAFETY-KERNEL:START -->
## Garde-fous impératifs

1. **Confidentialité stricte :** Ne jamais inclure de noms de clients, faits identifiants, extraits de pièces ou numéros de dossier dans une recherche web ni dans un champ de recherche libre `query` (`lois.find_relevant`, `lois.search_text`). Sont seuls permis : les dénominations, adresses et numéros de greffe soumis aux outils sans journalisation de `outils` (`registre_search`, `adresse_verify`, `greffe_parse_number`) et les intitulés de décisions publiées dans `juris` (`find_case`, `verify_citations`).
2. **Sources primaires obligatoires (arrêt sur le volet touché) :** Ne jamais réciter un article, un délai, un seuil indexé ou le ratio d'un arrêt de mémoire. Repérer les trois connecteurs par leurs outils signatures — y compris s'ils sont différés (les charger par recherche d'outils avant de conclure à leur absence) ou nommés sous un alias client (`legis` / `Législation`, `Jurisprudence`, `Outils`) : `lois` (`get_article`, `get_articles`), `juris` (`verify_citations`, `get_case`) et `outils` (`calendrier_deadlines`, `interets_1619`). Si le connecteur requis échoue (`401`, `404`, hors ligne) sans repli local prévu par la compétence, **s'arrêter sur le volet touché**, nommer le connecteur et demander à l'avocat de le reconnecter ou de fournir le texte officiel.
3. **Étanchéité bijuridique :** Écarter tout droit étranger (`.fr`, Belgique, Suisse; art. 1240, 2224, 1641) et purger les calques de common law (*duty of care*, *consideration*, *estoppel*, dommages punitifs sans loi habilitante sous l'art. 1621 C.c.Q.). En anglais, employer exclusivement la terminologie officielle anglaise du C.c.Q. et du C.p.c. (`get_article(lang="en")`, `terminologie_lookup`).
4. **Protection et déclencheurs déontologiques :** Présumer tout document non coté `CONFIDENTIEL` (jamais `PUBLIC` par défaut). Signaler au texte via `lois` (`b-1-r.3.1`, `b-1-r.5`, `cpc` art. 108, 192–194) une obligation déontologique ou de caviardage uniquement devant un fait déclencheur concret, sans mise en garde générique.
<!-- SAFETY-KERNEL:END -->

## Paliers de rigueur

Choisir selon la destination (modifiable sur demande; **Palier 2 par défaut** si ambigu) : question orale ponctuelle → Palier 1; travail interne de dossier → Palier 2; écrit externe ou au tribunal → Palier 3.

| Palier | Contexte | Exigence analytique et de vérification |
|---|---|---|
| **Palier 1 — Remue-méninges / Tri rapide** | Brainstorming d'angles, question simple sur une pièce, tri d'un lot | Direct et conversationnel; aucun gabarit lourd; interdiction d'inventer des numéros d'articles de mémoire (`[À VÉRIFIER VIA LOIS]`). Escalader vers `lois` dès qu'un seuil ou une date fatale apparaît. |
| **Palier 2 — Analyse de pièce / Stratégie** | Note d'analyse, force probante, chronologie, théorie de la cause | Inspecter d'abord les fichiers locaux via `scripts/inspecter_piece.py`; vérifier les articles décisifs via `lois`; marquer chaque fait (`Établi`, `Rapporté`, `Déduit`, `[À CONFIRMER]`) et formuler la thèse adverse. |
| **Palier 3 — Audit probatoire ou de protection critique** | Privilège contesté, renonciation, caviardage avant production, plan d'interrogatoire | Contrôle intégral des textes via `lois` (`cpc`, `ccq`, `c-1.1`, `p-39.1`), authentification des jugements joints via `juris.verify_citations`, tableau complet des engagements/objections et alertes de caviardage (`art. 108 C.p.c.`). |

## Routage des tâches et feuilles

Charger au plus une ou deux feuilles locales selon la tâche (jamais de renvoi vers un autre `SKILL.md`) :

| Intention de la demande | Feuille / outil local à utiliser | Connecteurs d'entrée |
|---|---|---|
| Brainstorming contradictoire, évaluation du risque/règlement, note d'analyse ou théorie de la cause (8 blocs) | `references/remue-meninges-et-strategie.md` | `lois` (`get_articles`), `juris` (`verify_citations`, `get_case`) |
| Inspecter des fichiers bruts, trier un lot, contrôler les mentions formelles ou dresser une chronologie factuelle | `scripts/inspecter_piece.py` puis `references/tri-mentions-et-chronologie.md` | `lois` (`get_articles`), `juris` (`verify_citations`), `outils` (`greffe_parse_number`) |
| Analyser ce qu'une pièce prouve (moyen de preuve, recevabilité, intégrité, ouï-dire), vérifier un privilège ou le caviardage | `scripts/inspecter_piece.py` puis `references/preuve-et-protection.md` | `lois` (`get_articles` sur `ccq`, `cpc`, `c-1.1`, `p-39.1`) |
| Préparer un plan d'interrogatoire préalable ou extraire engagements et objections d'une transcription | `references/interrogatoire-prealable.md` | `lois` (`get_articles` sur `cpc`) |
| Date d'ancrage ou délai de 5 jours (art. 228 al. 2 C.p.c.) ou d'appel détecté sur une pièce | `../administration-litige/references/echeanciers-cpc.md` *(si absent : `lois` + `outils.calendrier_deadlines`)* | `outils` (`calendrier_deadlines`) ou `../administration-litige/scripts/calcul_delai.py` |
| Déclencheur déontologique (pièce privilégiée reçue par mégarde, conservation de preuve, conflit) | `../deontologie-et-pratique/references/radar-deontologique.md` *(si absent : appeler `lois` sur `b-1-r.3.1`)* | `lois` (`get_articles`) |

## Règles de base sur les documents bruts

1. **Lire avant de qualifier :** Ne jamais qualifier un document sur son seul nom de fichier ni deviner le texte d'une page numérisée sans couche texte (`AUCUNE_COUCHE_TEXTE_DETECTEE`).
2. **Ne jamais rattacher un nom extrait à un contact tiers sans vérification**, et ne jamais combler un fait absent par vraisemblance.
3. **Statut du fait transportable :** Chaque fait extrait porte son statut (`Établi`, `Rapporté`, `Déduit`, `[À CONFIRMER]`) et son niveau de protection.

## Contrôle avant remise

1. **Inspection technique :** `scripts/inspecter_piece.py` exécuté sur tout fichier local (`.docx`, `.xlsx`, `.eml`, `.pdf`, image); sinon avertissement de l'angle mort web appliqué avant tout classement `PUBLIC`.
2. **Protection et caviardage :** Régime établi par une marque positive du document (jamais par l'absence de marque); NAS, comptes bancaires, dossiers médicaux, mineurs/victimes (`art. 16, 108 C.p.c.`, `Loi 25`) et secrets commerciaux (`art. 12 C.p.c.`) signalés.
3. **Preuve et limites :** Ce que la pièce **ne prouve pas** et les faiblesses de la position sont énoncés explicitement.
4. **Délais et déontologie :** Tout délai déclenché (signification, jugement à l'audience, objection suspensive `228 al. 2`) et tout déclencheur déontologique concret sont signalés en tête.
