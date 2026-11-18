# Protocole de l'instance (`art. 148–150, 490 C.p.c.`)

Encadre la rédaction et la négociation du protocole de l'instance civile en procédure ordinaire. **Vérifier d'abord via `lois` que le dossier n'est pas assujetti au régime simplifié C.Q. (`535.2 C.p.c.`, où le protocole est supprimé).**

## Objet et destinataire

* **Nature :** Contrat judiciaire de gestion de l'instance conclu entre les parties et déposé au tribunal pour encadrer le déroulement jusqu'à la mise en état (`148–150 C.p.c.`, formulaire officiel `SJ-1302` *Protocole de l'instance* en Cour supérieure le cas échéant, comportant la *Page de présentation* et la case administrative `CHEM*EXA` uniquement lors du **premier protocole** et omise sur tout protocole modifié/subséquent).
* **Sursis statutaire partiel (`art. 69 LFI`) :** Si un codéfendeur est en faillite ou sous protection d'insolvabilité, consigner en note explicative l'effet de la suspension des procédures à son égard sans paralyser l'instance contre les codéfendeurs solvables.
* **Destinataires :** Les procureurs de toutes les parties (ou parties non représentées) et le greffe du tribunal saisi (Cour supérieure ou Cour du Québec hors régime simplifié).

## Mentions obligatoires

Lire `lois.get_articles(law="cpc", numbers=["148", "149", "150", "152", "173", "490", "535.2"])` :
* Numéro de dossier, district, tribunal, parties et avocats;
* Date d'expiration du délai de rigueur de mise en état (`6 mois`, `173 C.p.c.` — calculé via `gestion-du-mandat` / `outils.calendrier_deadlines`);
* **Les 9 rubriques obligatoires (`148 al. 2 C.p.c.`)** en engagements précis et datés.

## Structure

1. **Modes privés de prévention et de règlement des différends (PRD) :** démarche envisagée, médiation, conférence de règlement;
2. **Moyens préliminaires (`166–168`) :** nature, date de présentation et délais;
3. **Interrogatoires préalables (`221 s.`) :** personnes interrogées, mode (oral/écrit), durée (`3 h` / `5 h`), lieu et dates limites;
4. **Expertises (`231 s.`) :** commune ou séparée, spécialité, dates de communication des rapports et de contestation (`241`);
5. **Défense (`170`) :** écrite ou orale et échéance (et demande reconventionnelle le cas échéant);
6. **Communication des pièces et éléments de preuve (`246 s.`) :** échéances respectives;
7. **Incidents prévisibles et cautionnement pour frais (`492`)** s'il y a lieu;
8. **Prolongation du délai de mise en état** (motif justifié si demandé, `173`);
9. **Modes de notification convenus (`109–111`)** et adresses courriel officielles.
* **Points de divergence et rubriques pratiques (`148–149`, `SJ-1302`) :** Consigner clairement les positions respectives sur chaque point divergent pour décision en gestion (`149 al. 3`), sans omettre les sous-questions des rubriques (options de conférence de règlement à l'amiable CRA, choix explicite entre **défense orale `170` avec exposé sommaire** et **défense écrite `171`**, calendrier d'interrogatoires et de communication des engagements/objections — ex. préavis et réponses convenus tels `14 j / 3 j / 14 j` en harmonie avec `228 al. 2 C.p.c.` — et tableau prévisible des frais de justice `339`). En cas de dépôt avec positions divergentes ou défaut de collaboration, joindre la **preuve de notification (`149 C.p.c.`)** aux autres parties.

## Clauses ou formules à proscrire

* **Protocole en régime simplifié C.Q. (`< 100 000 $`, `535.2`) :** Ne jamais rédiger ni exiger un protocole `148` dans un dossier soumis aux art. `535.1–535.15 C.p.c.`.
* **Dates vagues ou conditionnelles non datées** (« dans les meilleurs délais », « après les fêtes ») : chaque étape porte une date calendaire exacte calculée par `outils.calendrier_deadlines`.
* **Dépassement silencieux du `6 mois` (`173`) :** Tout calendrier qui excède `6 mois` exige une demande expresse de prolongation motivée avant échéance (délai de rigueur).

## Contrôle

1. Vérifier que le dossier relève de l'instance ordinaire (et non du régime simplifié `535.2`).
2. Vérifier la présence des 9 rubriques obligatoires de l'art. `148` (et toutes les sous-questions du formulaire `SJ-1302`), le choix défense orale (`170`) c. écrite (`171`), l'estimation des frais (`339`), la présence de la *Page de présentation* sur le 1er protocole seulement (`CHEM*EXA`), toute note de sursis `art. 69 LFI`, et la preuve de notification (`149`).
3. Faire vérifier toutes les dates calendaires via `gestion-du-mandat` (`conformite-echeanciers-cpc.md` et `outils.calendrier_deadlines`), notamment la présomption d'acceptation après `20 jours` (`150`) et la mise en état (`173`).
