# Fondamentaux de rédaction des actes de procédure (socle commun)

Socle obligatoire à charger **avec** la fiche `acte-*` visée pour tout acte de procédure québécois. **Vérifier les articles via `lois.get_articles` avant d'écrire tout article ou seuil.**

*Vecteur de base (`law="cpc"`) :* `numbers=["33", "35", "41", "42", "99", "100", "105", "141", "145", "660", "661"]`; plus `law="ccq"`, `numbers=["1525", "1526", "1619", "1620", "1621"]`.

## 1. Structure complète par défaut vs Bloc pour gabarit du cabinet

* **Complet (défaut au Palier 3) :**
  * Cartouche en tableau à deux colonnes : colonne gauche pour l'intitulé complet des parties (désignation abrégée `(ci-après, …)` en minuscules, sans point-virgule parasite) ; colonne droite pour `CANADA / PROVINCE DE QUÉBEC / DISTRICT DE [...]`, `COUR [...]` (`COUR DU QUÉBEC`, jamais `COUR DE QUÉBEC` ; `Chambre civile`, jamais `Chambre civil`), `N° [...]` (ou `[À COMPLÉTER]`) ;
  * En-tête à partir de la page 2 (`N° de dossier` + titre exact de l'acte) et pied de page du cabinet (raison sociale, adresse synchronisée avec l'endos, téléphone, **courriel de notification** `art. 110 C.p.c.`, référence interne) ;
  * Désignation complète des parties (vérifier personnes morales via `outils.registre_search`/`registre_get_entity` sans valeur de certificat, et adresses civiques via `outils.adresse_verify`);
  * Titre exact + article habilitant (`(Articles 141 et suivants du Code de procédure civile)`);
  * En-tête de présentation du récit : `AU SOUTIEN DE SA DEMANDE, [PARTIE] EXPOSE RESPECTUEUSEMENT CE QUI SUIT :`;
  * Sections : `LES PARTIES`, `LES FAITS`, caractérisations, `LES DOMMAGES`, `LA COMPÉTENCE DU TRIBUNAL`;
  * Clôture : `POUR CES MOTIFS, PLAISE AU TRIBUNAL :`, date/signature/coordonnées `[À COMPLÉTER]` (+ *Avis d'assignation* `145 C.p.c.` et renvoi à l'*endos* paysage `11 x 8,5 po` pour une demande introductive ; accord strict `par son avocat` vs `par leurs avocats` selon le nombre de représentés).
  * Contrôles anti-copier-coller systématiques avant dépôt : continuité des numéros de paragraphes (aucun doublon `8., 8.`), suppression de toute mention `PROJET`, concordance de date et de langue entre corps, pied de page et endos, et graphie exacte `cote` (sans accent circonflexe).
* **Bloc pour gabarit du cabinet (sur demande explicite) :** Corps pur seulement — sans cartouche, sans signature ni Markdown (intertitres en majuscules, gras réservé aux cotes `**Pièce P-1**`).

## 2. Discipline de l'article 99 C.p.c. et cotes de pièces

* **Une idée cohérente par numéro :** Scinder dès que la catégorie change (fait générateur → préjudice → lien causal). Chaque descripteur qualifie le fait avec précision (« dur et acéré »), sans adjectif émotif (« scandaleux », « outrageux »). Verbes au présent ou au passé composé; désignations constantes avec majuscule (`le Demandeur`, `la Défenderesse`).
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

## 4. Déclaration sous serment (`105 C.p.c.`)

* Jamais « affidavit » en français (`affidavit` est officiel uniquement en anglais).
* Rédigée à la **1re personne** (`Je, soussigné(e)…`); **faits personnels seulement** (aucune opinion ni conclusion de droit).
* Clore par la formule de sincérité et le bloc d'assermentation (`[À COMPLÉTER]`), y compris la mention de serment reçu à distance par moyen technologique lorsque applicable (`art. 105 C.p.c.`).
* Pour l'application en cours d'instance (`101 al. 3 C.p.c.`), rappeler que la déclaration sous serment n'est requise que lorsque la demande repose sur des faits dont la preuve n'est pas déjà au dossier ou lorsqu'une disposition particulière l'exige.
