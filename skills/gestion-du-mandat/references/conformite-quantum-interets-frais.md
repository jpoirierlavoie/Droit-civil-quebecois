# Tableaux de quantum, intérêts (art. 1619 C.c.Q.), taux BdC, IPC, loyer TAL et état des frais

Produit des tableaux structurés (Markdown et export `.csv` UTF-8 avec BOM `utf-8-sig` compatible Excel `fr-CA`) pour les réclamations pécuniaires, intérêts légaux ou à taux préférentiel, conversions de devises (*Loi sur la monnaie*), indexations IPC, fixations de loyer TAL, tableaux *Scott* et mémoires de frais de justice.

## Déclencheurs

* Calcul d'intérêts légaux (`5 %`) et d'indemnité additionnelle (`art. 1619 C.c.Q.`), d'un taux contractuel fixe ou d'un taux préférentiel + marge (`prime_plus_margin`);
* Conversion en dollars canadiens d'une dette en devise étrangère (`taux_boc_rates`, art. 12 *Loi sur la monnaie*, `1561, 3161 C.c.Q.`) ou relevé des taux directeur/d'escompte/préférentiel BdC;
* Indexation contractuelle selon l'IPC StatCan (`indice_ipc`, `18-10-0004-01` / `18-10-0005-01`);
* Calcul ou vérification d'ajustement de loyer résidentiel TAL (`loyer_tal`, `RLRQ, c. T-15.01, r. 2`, Décret 1455-2025) ou relevé de loyer moyen SCHL (`34-10-0133-01`);
* Préparation d'un tableau comparatif de dommages ou d'un tableau *Scott* (construction / commercial);
* Confection, vérification ou contestation d'un état des frais de justice après jugement (`339–344 C.p.c.`, `t-16-r.10`).

## Vecteur

* `law="ccq"` : `numbers=["1561", "1617", "1618", "1619", "1620", "1896", "1942", "1950", "1955", "3161"]` (selon le chef visé : intérêts, devises ou bail résidentiel)
* `law="cpc"` : `numbers=["54", "339", "340", "341", "342", "343", "344"]`
* `law="t-15.01"` (*Loi sur le Tribunal administratif du logement*) : `89–91` (recours internes `LTAL`, fixation de loyer exclue d'appel à la C.Q. sous `91`). Note : `RLRQ, c. T-15.01, r. 2` (*Règlement sur les critères de fixation de loyer*) ne figure pas dans le corpus `lois` — ses barèmes et formules 2026 vérifiés sont exécutés par `outils.loyer_tal`.
* `law="t-16-r.10"` (*Tarif judiciaire en matière civile*, texte plat sans divisions) : appeler directement `lois.get_articles(law="t-16-r.10", from="1", to="25")` (éviter `get_structure` qui est vide) en relevant la **date de consolidation** et l'indexation annuelle des droits de greffe!

## Obligations

### 1. Décompte des intérêts légaux, contractuels et taux préférentiel (`art. 1617–1620 C.c.Q.`)
**Ne jamais calculer les intérêts à la main ni extrapoler un trimestre L.A.F. ou une date de taux préférentiel non vérifiée.**
* Exécuter obligatoirement `outils.interets_1619(end_date, tranches=[...], mode=...)` : calcule au jour exact (`Exact/Exact`, intérêt simple `1620 C.c.Q.`, accumulation rationnelle `BigInt`) selon 4 modes : `'legal_plus_1619'`, `'legal_only'`, `'contractual'` (`rate_bps`), et `'prime_plus_margin'` (`spread_bps` global ou par tranche, `-5000..50000`).
* **Mode `'prime_plus_margin'` (BDC `V80691311`) :** utilise la série hebdomadaire des mercredis de la Banque du Canada (`V80691311`) et s'arrête sans extrapolation à `prime_table_last_verified_date`. `rate_overrides` est **interdit** en mode `prime_plus_margin`. L'outil émet `TAUX_BOC_PRIME_INDICATIF_BANCAIRE` : vérifier au contrat le prêteur bancaire stipulé, la date de prise d'effet, tout plancher, la base de jours et la capitalisation éventuelle (`1620 C.c.Q.`).
* **Usage strictement restreint de `rate_overrides` :** `rate_overrides` est **interdit** sur tout trimestre déjà publié dans la table embarquée du serveur (l'outil rejette l'appel). Il ne sert qu'à injecter un taux art. 28 L.A.F. nouvellement publié par Revenu Québec / *Gazette officielle du Québec* pour un trimestre postérieur à `laf_table_last_quarter` avant la mise à jour du connecteur, et exige alors une vérification humaine sur la source officielle.

### 2. Taux de change et taux BdC (`outils.taux_boc_rates`)
* **`category` :** `'fx'` (taux de change vs CAD), `'policy'` (`V39079`), `'bank'` (`V122530`), `'prime'` (`V80691311`) ou `'all_rates'`. Ne jamais passer `currency='CAD'`.
* **Conversion exacte `BigInt` (`amount`, `direction='foreign_to_cad'|'cad_to_foreign'`) :** applique art. 12 *Loi sur la monnaie* (`L.R.C. 1985, c. C-52`) avec `date` et `currency`. Signale automatiquement tout report au jour ouvrable précédent (`requested_date` vs `effective_observation_date`, `TAUX_BOC_REPORT_JOUR_OUVRABLE_PRECEDENT`) et le régime méthodologique (`noon_spot_pre_2017_05_01` avant le `2017-05-01` vs `daily_average_1630_et` à 16 h 30 HE depuis le `2017-05-01`). La date de conversion judiciaire applicable (`1561, 3161 C.c.Q.`) demeure une question de droit (`TAUX_BOC_CONVERSION_LOI_MONNAIE`).

### 3. Indexation IPC StatCan (`outils.indice_ipc`)
* **Séries couvertes :** StatCan `18-10-0004-01` (mensuel `YYYY-MM`) et `18-10-0005-01` (annuel `YYYY`), `geo` (`'quebec'`, `'montreal_rmr'`, `'quebec_rmr'`, `'canada'`), `product` (`'all_items'`, `'shelter'`, `'rented_accommodation'`, `'rent'`, `'health_care_services'`). Note : `'rent'` et `'health_care_services'` sont absents à l'échelle RMR (`vectorId=0`, rejetés pour `montreal_rmr` et `quebec_rmr`).
* **Indexation `BigInt` et garde d'année de base :** sur une plage `start_period`/`end_period` avec `amount`, accepte `floor_bps`, `cap_bps` (`-5000..50000`) et `rounding` (`'half_away_from_zero'` ou `'half_up'`). Toute divergence entre `uom` et `end_uom` (`'2002=100'` vs `'1992=100'`) bloque l'indexation sans facteur de raccordement officiel StatCan (`IPC_BASE_REINDEXATION_ATTENTION`).

### 4. Fixation de loyer TAL et loyers SCHL (`outils.loyer_tal`)
* **`mode='bareme'` (`year` 2015–2027) :** expose les pourcentages annuels publiés pré-2026 et post-2026 (`Décret 1455-2025` : `4,5 % / 6,0 %` pour janv.–1er avril 2026 ; `3,1 % / 6,7 %` + `5,0 %` immobilisations pour 2 avril 2026–1er avril 2027).
* **`mode='calcul_2026'` (`RLRQ, c. T-15.01, r. 2`) :** requiert `lease_renewal_date` (`>= 2026-01-01` sauf avis `< 2026-01-01`) et `current_rent_cents`; prend en charge RPA (`is_rpa`, `rpa_personal_services_cents`), revenus de l'immeuble, taxes municipales/scolaires et assurances asymétriques, déneigement (`12.1`), travaux majeurs `5 %` (`capital_works`), nouvelles dépenses (`new_expenses`) et variations d'aide (`aid_variations`).
* **Gardes obligatoires :**
  * `notice_date < '2026-01-01'` déclenche le régime transitoire pré-2026 (`TAL_REGIME_TRANSITOIRE_PRE_2026`, art. 6 Décret 1455-2025);
  * `section_f_exemption_5_ans=true` signale l'exemption de 5 ans (`art. 1955 C.c.Q.`, Section F du bail obligatoire — `TAL_EXEMPTION_CINQ_ANS_ART_1955_CCQ`);
  * `TAL_POUVOIR_DISCRETIONNAIRE_FIXATION` rappelle le pouvoir d'appréciation du TAL (art. 6, 7, 8–9, 11–12, 13, 15).
* **`mode='schl'` :** loyers moyens du marché StatCan/SCHL (`34-10-0133-01` par `cmhc_geo`, `structure_type`, `unit_type`, cellules supprimées à `rent_dollars: null`). Émet `SCHL_LOYER_MOYEN_INDICATIF` (moyenne indicative, ni plafond légal ni preuve comparative `1896/1950 C.c.Q.`).

### 5. Tableaux de dommages et tableaux comparatifs (construction / commercial / *Scott*)
* **Ventilation des dommages :** `| Poste / Chef de réclamation | Période / Date | Base contractuelle ou factuelle | Pièce(s) au soutien | Montant réclamé ($) | Point de départ intérêts | Notes / risque de preuve |`
* **Tableau de type *Scott* :** `| # | Poste / Élément allégué | Pièce / Photo / Rapport | Position du Demandeur ($) | Position du Défendeur ($) | Écart ($) | Évaluation / Note au tribunal |`
* **Formatage Excel (`utf-8-sig`) :** Fournir un fichier `.csv` encodé en UTF-8 avec BOM (`utf-8-sig`, délimiteur `;` ou `,` indiqué) avec formules `=SOMME(...)` / `=SUM(...)` simples et colonnes de dates ISO (`AAAA-MM-JJ`).

### 6. État des frais de justice / *Bill of Costs* (`art. 339–344 C.p.c.` et `t-16-r.10`)
* **Gabarit d'état des frais (`344 C.p.c.`) :** `| Poste | Date | Description & référence C.p.c. / t-16-r.10 | Pièce justificative (reçu / mémoire huissier) | Montant demandé ($) | Taxe / Remarque greffier |`
* **Délais de vérification et révision (`344`) :** Notifier l'état des frais à la partie qui les doit; **`10 jours`** pour notifier une opposition (sinon vérification par le greffier sans audience ou sur dossier), et **`10 jours`** de la décision du greffier pour demander la révision au tribunal (`344 al. 3` — calcul exact via `conformite-echeanciers-cpc.md` / `outils.calendrier_deadlines`).

## Silences et paires confondables

* **Frais de justice (`339`) vs honoraires extrajudiciaires :** Les frais de justice comprennent droits/frais de greffe, signification/notification, sténographie/transcription, indemnités des témoins, honoraires/débours d'experts (soumis à proportionnalité `339 al. 2`) et certains frais d'interprète/publicité — **jamais les honoraires extrajudiciaires de l'avocat** (sauf condamnation exceptionnelle pour abus de procédure sous `54 C.p.c.`).
* **Point de départ `1617` vs `1618 C.c.Q.` :** Distinguer la date de la demeure (`1594–1595`, `1617`, ou assignation si aucune mise en demeure préalable) de la date du préjudice ou de l'assignation (`1618` en préjudice corporel ou moral).
* **`V80691311` (BDC) vs taux préférentiel contractuel :** La série `V80691311` est hebdomadaire (mercredis) et indicative; elle ne remplace pas la vérification de la banque prêteuse, de la date de prise d'effet, du plancher ni du mode de calcul stipulés au contrat.
* **Change pré-`2017-05-01` vs post-`2017-05-01` et date de conversion (`1561/3161 C.c.Q.`) :** Avant le `2017-05-01`, la Banque du Canada publiait un taux au comptant de midi HE (remplacé par la moyenne quotidienne de 16 h 30 HE); la date de conversion juridique (échéance, demeure, jugement ou paiement) doit être tranchée en droit.
* **IPC contractuel (`2002=100` vs `1992=100`) vs bail résidentiel (`1942 C.c.Q.`) :** Ne jamais enchaîner deux années de base sans facteur StatCan; une clause d'indexation automatique à l'IPC est sans effet sur la fixation d'un bail résidentiel régi par les art. `1942 C.c.Q.` et `RLRQ, c. T-15.01, r. 2`.
* **Fixation TAL (`< 2026-01-01` vs `>= 2026-01-01`, `1955 C.c.Q.`) vs loyers SCHL :** Toujours vérifier la date de l'avis (`Décret 1455-2025` art. 6) et la Section F (`1955 C.c.Q.`); les loyers moyens SCHL ne sont ni un plafond ni une preuve comparative `1896/1950 C.c.Q.`.
* **Périodes futures :** Signaler tout trimestre L.A.F., date BDC, mois IPC ou barème TAL postérieur aux dernières données publiées sans jamais l'extrapoler.
