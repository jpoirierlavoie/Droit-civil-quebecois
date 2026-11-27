# Formulaires d'avant-mise en état : protocole de l'instance (`148, 173 C.p.c.`) et avis C.Q. (`SJ-1273`, `SJ-1274`)

Encadre la préparation, rubrique par rubrique, des **formulaires officiels régissant l'instance avant la mise en état** — sans jamais confectionner d'acte libre à la main : le *Protocole de l'instance en matière civile* (`148–150 C.p.c.`) en procédure ordinaire, et les formulaires obligatoires **`SJ-1273`** / **`SJ-1274`** en régime simplifié de la Cour du Québec (`535.1–535.15 C.p.c.`, directive `qccq-regles-simplifiees`, où le protocole est supprimé par `535.2`).

## Objet et destinataire

* **Principe directeur :** En droit judiciaire québécois, le contrat judiciaire de gestion préparatoire prend exclusivement la forme des **formulaires prescrits par les tribunaux**. L'assistant prépare les réponses exactes et datées destinées à chaque case ou ligne du formulaire officiel.
* **Effet déterminant du 1er protocole sur la date limite ultime d'inscription (`150, 173 C.p.c.`) :**
  * C'est l'acceptation présumée du **premier protocole** (`20 jours` suivant son dépôt sans convocation du tribunal, `150 C.p.c.`) ou son établissement par le tribunal qui fait courir le **délai de rigueur de `6 mois`** pour mettre le dossier en état et déposer la demande d'inscription (`173 al. 1 C.p.c.`).
  * **Défaut de déposer le 1er protocole à temps (`45 jours`, ou `3 mois` sous `490`, `173 al. 3 C.p.c.`) :** le délai de rigueur de `6 mois` **court rétroactivement depuis la signification de la demande introductive**, et le tribunal ne peut plus le prolonger sauf **impossibilité d'agir de fait**.
  * **Protocoles modifiés subséquents :** un protocole modifié entre parties omet la *Page de présentation* (`CHEM*EXA`) et **ne prolonge jamais par lui-même la date limite ultime d'inscription** issue du 1er protocole — toute prolongation du délai de rigueur exige l'autorisation expresse du tribunal avant l'échéance (`173 al. 2 C.p.c.`, lignes 6–7 du formulaire).
* **Sursis statutaire partiel (`art. 69 LFI`) :** Si un codéfendeur est en faillite ou sous protection d'insolvabilité, consigner l'effet de la suspension à son égard sans paralyser l'instance contre les codéfendeurs solvables.
* **Destinataires :** Les procureurs de toutes les parties (ou parties non représentées) et le greffe du tribunal saisi (Cour supérieure ou Cour du Québec).

## Mentions obligatoires

Lire `lois.get_articles(law="cpc", numbers=["148", "149", "150", "152", "170", "171", "173", "341", "342", "490", "535.2", "535.4", "535.5", "535.6", "535.7", "535.12", "535.13", "535.15"])` et, en C.Q. simplifiée, `lois.get_articles(law="qccq-regles-simplifiees", from="1", to="6")` :
* Numéro de dossier (`outils.greffe_parse_number`), district, tribunal, parties et avocats responsables;
* Date de signification de la demande introductive et **date d'expiration du délai de rigueur d'inscription** (`6 mois` à compter de l'acceptation/établissement du 1er protocole sous `173`, ou `6 mois` depuis la signification de l'avis d'assignation en régime simplifié C.Q. sous `535.13` — calculé via `gestion-du-mandat` / `outils.calendrier_deadlines`);
* **En procédure ordinaire :** les 9 rubriques obligatoires (`148 al. 2 C.p.c.`) ventilées selon les lignes du formulaire officiel;
* **En régime simplifié C.Q. (`< 100 000 $`) :** les rubriques des formulaires obligatoires **`SJ-1273`** (`535.4 / 535.6 / 535.7`) et, s'il y a moyen préliminaire ou incident dénoncé sous `535.5`, **`SJ-1274`**.

## Structure

* **A. Instance ordinaire — *1er Protocole de l'instance en matière civile* (`art. 148 C.p.c.`, C.S. lignes 1–42) :**
  1. **Page de présentation obligatoire (1er protocole uniquement, agrafée devant la page 1) :** réponses `OUI / NON` de triage administratif (désaccord sur durée/lieu/format ou nombre de représentants aux interrogatoires l. 20–22, sur nombre/teneur des expertises l. 23–26, demande d'autorisation de défense écrite l. 28/33, suspension l. 5 avec motifs, prolongation l. 6–7 ; case `RÉSERVÉ AU GREFFIER : CHEM*EXA`). **Ne jamais joindre cette page à un protocole modifié.**
  2. **Généralités, inscription et CRA (lignes 1–8) :** date de signification, nature et valeur du litige, **questions en litige obligatoirement communes**, demande éventuelle de suspension (`1, 3 ou 6 mois`) ou de prolongation motivée du délai d'inscription (`173`), position sur la conférence de règlement à l'amiable (`demandée par tous / envisageable / exclue`).
  3. **Moyens préliminaires, incidents et sauvegarde (lignes 9–20) :** dates limites fermes de dépôt (`167` déclinatoire, `168/51` irrecevabilité/abus, `169` précisions/documents/radiation, `492` cautionnement, `188` intervention forcée, `189` appel en garantie, `193` inhabilité, `206` modification, `158 al. 5 / 169` sauvegarde).
  4. **Interrogatoires préalables, préengagements et engagements (lignes 21–27, `221 s.`) :** noms, durée en heures, mode (`oral / écrit`) et dates convenues (parties et tiers, autorisation requise `oui/non`) ; respecter les clauses types civiles préimprimées — demande des documents à discuter au moins **`30 jours`** à l'avance et communication au moins **`3 jours`** avant l'interrogatoire (ligne 26), puis communication des engagements au plus tard **`30 jours`** après l'interrogatoire **sans attendre les notes sténographiques** (ligne 27) *(ne jamais importer les délais de `14 jours` propres au formulaire familial)*.
  5. **Expertises, défense, communication de preuve, frais et notification (lignes 28–42) :** expertise commune (`oui/non`, nature ou motifs de refus) ou une seule par discipline (`232`), choix entre **défense par exposé sommaire (ligne 32)** et **demande motivée d'autorisation de défense écrite (ligne 33, `171`)** (+ reconvention l. 34–35), dates limites de communication des pièces et déclarations `292` (`248`, l. 36–38), évaluation des frais de justice incluant expertises (`339`, l. 39–41), mode de notification (`110 s.`, huissier/courriel, l. 42) et rappel des sanctions `341–342 C.p.c.`. En cas de divergences (`149 al. 3`), consigner chaque position et joindre la **preuve de notification (`149`)**.
* **B. Régime simplifié C.Q. — Formulaires obligatoires **`SJ-1273`** et **`SJ-1274`** (`qccq-regles-simplifiees` par. 1–6) :**
  * **`SJ-1273` (*Avis requis par les art. 535.4, 535.6 et 535.7 C.p.c.*) :** déposé à `20 j` par le demandeur (`535.4`), `95 j` par le défendeur (`535.6`) et `95 j` / `45 j` par le tiers (`535.7`). Remplir : instruction par priorité / PRD (joindre preuve ou attestation), CRA obligatoire c. remplacement par conférence préparatoire (`535.12`), demande d'autorisation de pages supplémentaires (`> 5 p.` demande/intervention/déclaration `292`, `> 2 p.` exposé sommaire, `> 7 p.` exposé + reconvention), interrogatoires oraux (`> 1` soumis à autorisation) et écrits, expertise (aucune / commune / individuelle avec distinction `>= 50 000 $` c. `< 50 000 $` sous `535.15`), témoignages par déclaration écrite (`292`) ; cases `CHEM*CON` réservées au greffier.
  * **`SJ-1274` (*Avis de dénonciation de moyens préliminaires et incidents*, `535.5 C.p.c.`, `45 j`) :** à remplir et placer obligatoirement devant l'acte dénoncé (renvoi, suspension, communication, précisions, radiation, rejet, jonction/disjonction), sous peine de **refus de dépôt par le greffier** (`qccq-regles-simplifiees` par. 5–6).
* **Accords accessoires d'instruction :** toute entente privée de confidentialité documentaire ou lettre d'instructions conjointes à l'expert commun demeure un simple accessoire opérationnel subordonné à ces formulaires (voir `contrat-ententes-judiciaires.md`).

## Clauses ou formules à proscrire

* **Acte libre « fait main » en lieu et place du formulaire prescrit**, ou **protocole `148` en régime simplifié C.Q. (`< 100 000 $`, `535.2`)** : utiliser exclusivement le formulaire officiel applicable au tribunal et au régime.
* **Dates vagues ou supposition qu'un protocole modifié reporte l'inscription (`173`) :** chaque étape porte une date calendaire exacte (`outils.calendrier_deadlines`), et tout dépassement du délai de rigueur de `6 mois` issu du 1er protocole exige une autorisation judiciaire expresse avant échéance (`173 al. 2`).
* **Contamination familiale (`14 j / 3 j / 14 j` ou Annexe A)** : exclure tout formulaire ou délai propre à la Chambre de la famille.

## Contrôle

1. Vérifier d'abord le régime procédural : instance ordinaire (`148`) c. régime simplifié C.Q. (`535.2` → `SJ-1273` / `SJ-1274`).
2. En instance ordinaire, contrôler les 9 rubriques (`148 al. 2`), la *Page de présentation* sur le **1er protocole uniquement** (`CHEM*EXA`), les délais civils `30 j / 3 j / 30 j` (lignes 26–27), le choix exposé sommaire c. autorisation de défense écrite (lignes 32–33), l'estimation des frais (`339`), toute note `art. 69 LFI` et la preuve de notification (`149`).
3. Calculer et vérifier via `gestion-du-mandat` (`conformite-echeanciers-cpc.md` et `outils.calendrier_deadlines`) la présomption d'acceptation de `20 jours` (`150`) et la **date limite ultime d'inscription (`173` ou `535.13`)**.
