# Rédaction des actes de procédure civile (C.p.c.)

Couvre la demande introductive (instance ordinaire et régime simplifié C.Q.), la défense, l'exposé sommaire, la demande reconventionnelle, la demande en cours d'instance, le protocole de l'instance, la déclaration sous serment et l'acte modifié. **Vérifier via `lois.get_articles` avant d'écrire tout article ou seuil.**

*Vecteur C.p.c. (`law="cpc"`) :* `numbers=["33", "35", "41", "42", "99", "100", "101", "105", "141", "145", "146", "148", "170", "172", "206", "207", "208", "535.1", "535.2", "535.3", "535.4", "535.6", "535.14", "535.15", "660", "661"]`; plus `law="ccq"`, `numbers=["1525", "1526", "1619", "1620", "1621"]`.

## 1. Structure complète vs Bloc pour gabarit

* **Complet (défaut) :** Cartouche (`CANADA / PROVINCE DE QUÉBEC / DISTRICT DE [...]`, `COUR [...]`, `N° [...]`), désignation complète des parties (vérifier personnes morales via `outils.registre_search`/`registre_get_entity` et adresses civiques via `outils.adresse_verify`), titre + article habilitant (`(Articles 141 et suivants du Code de procédure civile)`), `AU SOUTIEN DE SA DEMANDE, [PARTIE] EXPOSE RESPECTUEUSEMENT CE QUI SUIT :`, sections (`LES PARTIES`, `LES FAITS`, caractérisations, `LES DOMMAGES`, `LA COMPÉTENCE DU TRIBUNAL`), `POUR CES MOTIFS, PLAISE AU TRIBUNAL :`, date/signature/coordonnées `[À COMPLÉTER]` (+ *Avis d'assignation* `145 C.p.c.` et *endos* pour une demande introductive).
* **Bloc pour gabarit (sur demande) :** Corps seulement, sans cartouche, sans signature ni Markdown (sauf majuscules et gras sur les cotes `**Pièce P-1**`).

## 2. Discipline de l'article 99 C.p.c. et cotes de pièces

* **Une idée cohérente par numéro :** Scinder dès que la catégorie change (fait générateur → préjudice → lien causal). Chaque descripteur qualifie le fait avec précision (« dur et acéré »), sans adjectif émotif (« scandaleux », « outrageux »). Verbes au présent/passé composé; désignations constantes avec majuscule (`le Demandeur`, `la Défenderesse`).
* **Le droit ne s'écrit pas dans un acte de procédure** — deux exceptions étroites : (1) l'article habilitant sous le titre de l'acte, (2) la section `LA COMPÉTENCE DU TRIBUNAL`.
* **Formules de pièce (gras sur la cote, ordre continu de première invocation `P-1..P-n`, `D-1..D-n`) :**
  * Standard : `… le tout tel qu'il appert d'une copie [du document], produite au soutien des présentes sous la cote **Pièce P-3** ;`
  * En liasse : `… sous la cote **Pièce P-4, en liasse** ;` (anglais : *filed jointly as **Exhibit P-4***).
  * Renvoi ultérieur : `… tel qu'il appert de la **Pièce P-3** déjà produite ;` (jamais de nouvelle cote).

## 3. Caractérisation, dommages, compétence et conclusions

| Rubrique | Exigences et pièges fréquents |
|---|---|
| **Caractérisation (fin des FAITS)** | Satisfait l'exigence de non-surprise (`99`) sans citer d'article : faute (`constitue un défaut manifeste et un manquement caractérisé…`), norme de conduite, causalité hypothétique (`n'eût été de…`), lien direct (`direct, immédiat et non interrompu`); ou en contrat : obligation, inexécution, demeure, préjudice. |
| **Dommages** | Une allégation par chef justifiant le montant (`5 000,00 $`); clore par le total + réserve d'amendement. **Dommages punitifs (`1621 C.c.Q.`) interdits sans loi habilitante vérifiée** (Charte, L.p.c., etc.). |
| **Compétence** | Vérifier `33` et seuil indexé `35` via `lois` (`< 75 000 $` C.Q. exclusif, `75 000 $` à `< 100 000 $` concurrent `[À VÉRIFIER VIA LOIS]`). Distinguer **41** (domicile du défendeur; clause d'élection nulle en contrat d'adhésion) de **42** (fors additionnels). Clore par « bien fondée en faits et en droit ». |
| **Conclusions** | Impératifs en majuscules (`CONDAMNER`, `DÉCLARER`, `ORDONNER`, `REJETER`), tous soutenus par des allégations. **Solidarité (`1525–1526 C.c.Q.`) jamais automatique** hors entreprise ou faute commune. **Exécution provisoire malgré appel (`660–661 C.p.c.`)** à demander dès le jugement de 1re instance en alléguant le préjudice sérieux/irréparable. Intérêts + indemnité additionnelle depuis la mise en demeure (chiffrage liquide via `outils.interets_1619` si demandé). Clore : `LE TOUT avec les frais de justice.` |

## 4. Variantes procédurales et modifications

| Acte | Règles propres |
|---|---|
| **Régime simplifié C.Q. (`535.1–535.15`)** | Applicable de plein droit sous `100 000 $` en C.Q. : **aucun protocole** (`535.2`), demande `<= 5 pages` (`535.3`), exposé sommaire `<= 2 pages` (`<= 7 pages` si reconvention, `535.6`), déclaration écrite de témoin `<= 5 pages` (`535.14`), expertise commune `< 50 000 $` (`535.15`). Avertir qu'un texte non paginé exige vérification de pagination finale dans Word. |
| **Défense / Reconvention** | Réponse paragraphe par paragraphe (`admet`, `nie`, `nie tel que rédigé`, `ignore`), puis version des faits en continuant la numérotation, cotes `D-1..D-n`. Reconvention : propre numérotation et compétence si la valeur change. |
| **Protocole (`148`)** | 9 rubriques obligatoires en engagements datés (PRD, moyens préliminaires, interrogatoires, expertise, défense, communication preuve, incidents, prolongation mise en état, notifications); noter les points de divergence si désaccord. |
| **Déclaration sous serment (`105`)** | Jamais « affidavit » en français (`affidavit` est officiel en anglais). 1re personne; **faits personnels seulement** (aucune opinion ni conclusion de droit); clore sur la formule de sincérité. |
| **Acte modifié (`206–208`)** | Intitulé `… MODIFIÉE`; **geler strictement les cotes existantes** (`[Pièce P-2 retirée]`, nouvelle pièce = `P-(n+1)` — ne jamais renuméroter `P-3` en `P-2`); conserver les numéros de paragraphes (`14. [Retiré] ;` et insertions `12.1`); marquer les ajouts/retraits. |

## 5. Avis d'assignation (art. 145–146 C.p.c.) et avis de présentation (art. 101 C.p.c.)

Lire `lois.get_articles(law="cpc", numbers=["101", "145", "146", "535.4", "535.6"])` avant rédaction :

* **Avis d'assignation (`145–146`, modèle établi par la ministre de la Justice joint à toute demande introductive) :** Énoncer le délai de réponse de `15 jours` suivant la signification (et l'avertissement de jugement par défaut possible sans autre avis avec frais de justice), les options du défendeur (régler, contester avec dépôt d'une réponse et établissement du protocole — ou, en régime simplifié C.Q. `535.1 s.`, sans protocole, avec communication des pièces du demandeur en `20 j` `535.4` et exposé sommaire de défense en `95 j` `535.6`), la mention relative au transfert aux petites créances, l'indication des pièces au soutien (`145 al. 1`), le district/greffe, les coordonnées complètes de l'avocat ou de la partie non représentée et le renvoi à l'aide juridique ainsi qu'aux Centres de justice de proximité.
* **Avis de présentation (`101`, demande en cours d'instance ou injonction) :** Date, heure, salle et palais (`outils.palais_get`), notification au moins `5 jours` avant la présentation sauf urgence ou autre délai fixé par le tribunal, avec pièces et déclaration sous serment jointes.
* **Bordereau et endos de cour :** Suivre les gabarits formels de bordereau et d'endos (`bordereaux-concordance-et-endos.md` via `administration-litige`).
