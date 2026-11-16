---
name: administration-litige
description: >-
  Utiliser pour calculer une date limite ou gérer les opérations procédurales d'un litige au
  Québec (C.p.c.) : échéance, délai de signification, réponse, mise en état, production ou
  appel, calendrier d'instance (ordinaire ou simplifiée C.Q.), notification après 17 h, jours
  fériés, bordereau de pièces, concordance preuve-allégations, endos de cour, tableau de
  dommages/Scott, intérêts légaux et indemnité additionnelle (art. 1619 C.c.Q.) et état des
  frais de justice. En anglais — use for Quebec procedural deadlines, due dates, court schedule,
  exhibit list, concordance matrix, court backing, legal interest, damages table, bill of costs.
  Ne pas utiliser pour la prescription substantielle (recherche-juridique) ni rédiger un acte
  complet (redaction-juridique).
---

# Administration du litige et échéanciers

Répond aux besoins opérationnels et procéduraux du dossier : délais C.p.c., avis et bordereaux de pièces, concordance preuve-allégations, endos de cour, tableaux de dommages/intérêts et états des frais.

<!-- SAFETY-KERNEL:START -->
## Garde-fous impératifs

1. **Confidentialité stricte :** Ne jamais inclure de noms de clients, faits identifiants, extraits de pièces ou numéros de dossier dans une recherche web ni dans un champ de recherche libre `query` (`lois.find_relevant`, `lois.search_text`). Sont seuls permis : les dénominations, adresses et numéros de greffe soumis aux outils sans journalisation de `outils` (`registre_search`, `adresse_verify`, `greffe_parse_number`) et les intitulés de décisions publiées dans `juris` (`find_case`, `verify_citations`).
2. **Sources primaires obligatoires (arrêt sur le volet touché) :** Ne jamais réciter un article, un délai, un seuil indexé ou le ratio d'un arrêt de mémoire. Repérer les trois connecteurs par leurs outils signatures — y compris s'ils sont différés (les charger par recherche d'outils avant de conclure à leur absence) ou nommés sous un alias client (`legis` / `Législation`, `Jurisprudence`, `Outils`) : `lois` (`get_article`, `get_articles`), `juris` (`verify_citations`, `get_case`) et `outils` (`calendrier_deadlines`, `interets_1619`). Si le connecteur requis échoue (`401`, `404`, hors ligne) sans repli local prévu par la compétence, **s'arrêter sur le volet touché**, nommer le connecteur et demander à l'avocat de le reconnecter ou de fournir le texte officiel.
3. **Étanchéité bijuridique :** Écarter tout droit étranger (`.fr`, Belgique, Suisse; art. 1240, 2224, 1641) et purger les calques de common law (*duty of care*, *consideration*, *estoppel*, dommages punitifs sans loi habilitante sous l'art. 1621 C.c.Q.). En anglais, employer exclusivement la terminologie officielle anglaise du C.c.Q. et du C.p.c. (`get_article(lang="en")`, `terminologie_lookup`).
4. **Protection et déclencheurs déontologiques :** Présumer tout document non coté `CONFIDENTIEL` (jamais `PUBLIC` par défaut). Signaler au texte via `lois` (`b-1-r.3.1`, `b-1-r.5`, `cpc` art. 108, 192–194) une obligation déontologique ou de caviardage uniquement devant un fait déclencheur concret, sans mise en garde générique.
<!-- SAFETY-KERNEL:END -->

## Paliers de rigueur

Choisir selon la destination (modifiable sur demande; **Palier 2 par défaut** si ambigu) : question orale ponctuelle → Palier 1; travail interne de dossier → Palier 2; écrit externe ou au tribunal → Palier 3.

| Palier | Contexte | Exigence de calcul et de contrôle |
|---|---|---|
| **Palier 1 — Calcul rapide / Estimation** | Échéance isolée sur date donnée oralement | Calculer par `outils.calendrier_deadlines` ou `scripts/calcul_delai.py` (jamais de tête); escalader vers `lois` dès qu'un statut de rigueur ou un ancrage complexe (`111 al. 2`) est en jeu. |
| **Palier 2 — Tableau de gestion / Dossier** | Calendrier de l'instance, bordereau de travail, quantum | Vérifier tous les articles déclencheurs via `lois`; montrer le compte étape par étape; contrôler privilèges et caviardage (`108 C.p.c.`) avant tout bordereau externe. |
| **Palier 3 — Acte ou état prêt au dépôt / taxation** | Bordereau signifié, endos de cour, état des frais taxé, échéance critique | Relecture intégrale des articles (`cpc`, `t-16-r.10`, règlements de cour) via `lois`; contrôle strict des cotes et du greffe (`outils.greffe_parse_number`, `palais_get`); export CSV UTF-8 (`utf-8-sig`) prêt pour Excel. |

## Routage des tâches et feuilles

Charger au plus une ou deux feuilles locales selon la tâche (jamais de renvoi vers un autre `SKILL.md`) :

| Intention de la demande | Feuille / outil local à utiliser | Connecteurs d'entrée |
|---|---|---|
| Calculer ou dresser le calendrier d'une instance (ordinaire, C.Q. `535.1 s.`, appel), qualifier un délai | `references/echeanciers-cpc.md` + `scripts/calcul_delai.py` *(hors ligne / lots)* | `outils` (`calendrier_deadlines`, `calendrier_holidays`), `lois` (`get_articles` sur `cpc`, `i-16`) |
| Dresser un bordereau (145, 174, 247, 250), vérifier la concordance `Allégation ↔ Pièce ↔ Témoin` ou rédiger un **endos** | `references/bordereaux-concordance-et-endos.md` | `lois` (`cpc`, `c-25.01-r.0.2.1`, `r.9`, `r.0.2.01`), `outils` (`greffe_parse_number`, `palais_list`, `palais_get`) |
| Établir un tableau de dommages, calcul d'intérêts (`1619 C.c.Q.`), tableau de construction (*Scott*) ou **état des frais** (`339–344`) | `references/tableaux-quantum-et-frais.md` | `outils` (`interets_1619`), `lois` (`get_articles` sur `cpc`, `ccq`, `t-16-r.10`) |
| Pièces brutes non encore triées sur le plan privilège/caviardage avant bordereau ou chronologie | `../analyse-juridique/references/preuve-et-protection.md` *(si absent : vérifier `cpc` `11, 12, 16, 108` via `lois`)* | `../analyse-juridique/scripts/inspecter_piece.py` *(si disponible)*, `lois` |
| Délai échu par erreur de l'avocat ou autre déclencheur déontologique | `../deontologie-et-pratique/references/radar-deontologique.md` *(si absent : appeler `lois` sur `b-1-r.3.1` art. 47)* | `lois` (`get_articles`) |

## Contrôle avant remise

1. **Ancrage et calcul :** Date de départ nommée par sa pièce/nature (ou marquée `[DATE À CONFIRMER]`); calcul fait par `outils` ou `scripts/calcul_delai.py` (jamais mental), montrant le report `111 al. 2`, le quantième et le report `83 al. 3`.
2. **Avertissements obligatoires :** Mentionner en toutes lettres que la période `30 juin – 1er septembre` et `20 décembre – 7 janvier` ne suspend pas les délais (`82 al. 2`), que le 30 septembre est ouvrable au C.p.c., et que la prescription substantielle relève de `recherche-juridique`.
3. **Privilège et cotes :** Aucun document non vérifié coté `PUBLIC` par défaut; alerte de caviardage (`108 C.p.c.`) sur tout NAS, compte ou dossier médical avant communication.
4. **Tarifs et intérêts :** Montants du `Tarif judiciaire` (`t-16-r.10`) lus via `lois`; intérêts calculés via `outils.interets_1619` sans extrapoler de trimestre non publié.
