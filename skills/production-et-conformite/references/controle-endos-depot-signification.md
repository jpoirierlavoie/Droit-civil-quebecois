# Endos de cour, dépôt, signification et copies (`backing`)

Dresse l'endos de cour québécois conforme, contrôle les formalités de dépôt au greffe, encadre la signification/notification et distingue originaux et copies.

## Règles applicables

Vérifier les règles de forme et de dépôt du tribunal saisi via `lois` (`cpc` art. `107`, `109–111`, `116–129`, `130–140`, `c-25.01-r.0.2.1` C.S. art. 3–14, `c-25.01-r.9` C.Q., `c-25.01-r.0.2.01` C.A.Q., `t-16-r.10` droits de greffe) ainsi que les directives de pratique de la C.S. et de la C.Q. Vague 1 (`fonction='directive'`, `qccs-dist-mtl` avec `rel_type='preseance-sur'` `qccs-div-mtl`, `qccs-div-qc`, `qccq-regles-simplifiees`, `qccq-mtl-prat-civile`, `qccq-mtl-prat-admin`, `qccq-daa-jurisprudence`, en `par.`/`unit='paragraphe'`, `fr`-only, avec `links` sur les annexes `ps:*` ; directives C.A.Q. hors corpus Vague 1 à vérifier séparément) et les coordonnées du palais via `outils.greffe_parse_number` et `outils.palais_get`/`palais_list`.
*(Avertissement obligatoire : les tables MJQ d'adresses datent du relevé local sans n° de téléphone et doivent être revérifiées auprès du Ministère avant signification ou dépôt.)*

* **Structure complète d'un endos québécois (format US Letter paysage `11 × 8,5 po`) :**
  * `N° : [n° dossier de cour]` (décomposé via `outils.greffe_parse_number` — vérifier aucun chiffre tronqué sur les actes en pied de page et à l'endos)
  * `COUR [SUPÉRIEURE / DU QUÉBEC / D'APPEL]` (jamais `COUR DE QUÉBEC` ; `Chambre civile`, jamais `Chambre civil`) · `PROVINCE DE QUÉBEC` · `DISTRICT DE [District]` — ou intitulé exact du forum spécialisé (**Tribunal administratif du logement**, **TAQ**, **Cour du Québec — Division administrative et d'appel `500-80`** avec anonymisation/initiales si requise)
  * Parties : `[DEMANDEUR], c. [DÉFENDEUR]` (parité stricte de langue avec le corps de l'acte)
  * Intitulé exact de l'acte (`DEMANDE INTRODUCTIVE D'INSTANCE`, `BORDEREAU DES PIÈCES`, etc.) — avec mention **`ORIGINAL`** ou **`COPIE DE LA COUR`** / **`COPIE`** et montant en litige le cas échéant (`c-25.01-r.9 art. 10`)
  * Mention **`SOUS PLI CACHETÉ — ART. 12 C.P.C.`** ou **`CONFIDENTIEL — ART. 108 C.P.C.`** s'il y a lieu
  * Bloc d'identification du cabinet / procureur(e) synchronisé depuis une **source unique de vérité** : nom, barreau/étude, adresse exacte (vérifiée contre le pied de page de l'acte pour éviter toute ancienne adresse ou numéro de suite transposé), **courriel de notification (`art. 109–110 C.p.c.`)**, code d'avocat/informatique (`c-25.01-r.0.2.1 art. 3`), téléphone, `N/D : [référence interne]`
  * Espace réservé au timbre du greffe ou au procès-verbal de signification

## Contrôles automatisés

1. `outils.greffe_parse_number` : confirmer la validité du numéro de dossier de cour, le code de greffe, la chambre (`17`, `22`, `09`, etc.) et l'année.
2. `outils.palais_get` : obtenir la désignation officielle du palais ou point de service (à confirmer auprès du MJQ avant déplacement).
3. `python scripts/controler_document.py <document.docx|pdf> --json` : confirmer le format US Letter **portrait (`8,5 × 11 po`) et/ou paysage (`11 × 8,5 po` pour l'endos)** et l'absence de verrous techniques avant dépôt. *(Si Python local indisponible — `claude.ai`, ChatGPT sans Python, Gemini App `/mcp/oauth`, Deep Research — divulguer explicitement que la vérification octets/XML/PDF du format et des verrous a été omise et l'inscrire au bon de travail.)*

## Contrôles humains

* **Liste de contrôle avant dépôt / signification :**
  * Papier US Letter portrait (`8,5 × 11 po`) pour le corps et **paysage (`11 × 8,5 po`)** pour l'endos, et pagination vérifiée (`art. 535.3 / 535.6 C.p.c.`);
  * Concordance stricte entre corps et endos : **même nom exact de tribunal** (ex. jamais un endos « TAL » sur un plan destiné au « TAQ »), même adresse/numéro de bureau, même anonymisation / initiales sous `108 C.p.c.` partout (entête, tableaux et endos), même langue (jamais d'endos français sur un acte anglais ou vice versa), aucun chiffre manquant dans le numéro de dossier, retrait de toute mention `PROJET`;
  * Droits de greffe vérifiés (`t-16-r.10` lu via `lois`) et paiement joint pour le dépôt technologique (`107 al. 5 C.p.c.`);
  * Avis d'assignation (`145`), avis requis (`535.4/535.6/535.7`) ou avis de présentation (`101`) joint;
  * Distinction claire **`ORIGINAL`** (greffe / dossier du tribunal) vs **`COPIE DE LA COUR`** / **`COPIE`** (parties signifiées ou notifiées);
  * Mode approprié vérifié : **signification par huissier** (acte introductif `139`, injonction `510`, condamnation exécutoire, mise en demeure critique) vs **notification technologique ou autre (`109–111`, `133`, `134 C.p.c.`)** accompagnée d'un **bordereau de notification technologique** conservant preuve des destinataires et de l'horodatage (`<= 17 h 00` pour le jour même selon `111 al. 2`, dépôt hors heures `107 al. 4` — détails des délais dans `gestion-du-mandat`).

## Bon de travail

Produire un bon de travail court avant envoi/dépôt : vérification finale de l'endos (Original vs Copie), émission du mandat à l'huissier ou préparation de l'envoi de notification technologique avec accusé de réception, confirmation du paiement des droits de greffe (`t-16-r.10`), et **toute vérification octets/PDF omise lorsque `controler_document.py` n'a pas pu s'exécuter localement**.
