# Analyse des documents judiciaires (procès-verbaux, jugements, ordonnances)

[FICHE À RÉDIGER]

Encadre la lecture et la qualification des procès-verbaux d'audience, jugements, ordonnances et décisions administratives (portée, dates d'ancrage procédurales et autorité de la chose jugée).

## Qualification

`[FICHE À RÉDIGER]` — Charger `lois.get_articles(law="cpc", numbers=["321", "335", "336", "338", "389"])` et `law="ccq", numbers=["2813", "2848"]` :
* Jugement final au fond vs jugement en cours d'instance / mesure de gestion (`32`, `158 C.p.c.`) vs ordonnance de sauvegarde ou injonction;
* Procès-verbal d'audience ou de conférence de gestion (constat authentique du greffier des présences, admissions et ordonnances prononcées séance tenante).

## Authentification et intégrité

`[FICHE À RÉDIGER]` — Vérifier le numéro de dossier de cour (`outils.greffe_parse_number`), le district, la date de signature par le juge ou le greffier spécial, le timbre du greffe et, s'il s'agit d'un jugement publié, l'authentification via `juris.verify_citations` / `juris.get_case`.

## Recevabilité

`[FICHE À RÉDIGER]` — Acte authentique (`2813–2818 C.c.Q.`) faisant preuve de ses constatations officielles; vérifier les conditions de reconnaissance d'une décision étrangère le cas échéant (`3155 s. C.c.Q.`).

## Force probante

`[FICHE À RÉDIGER]` — Distinguer :
* le **dispositif** (ce qui est ordonné et qui passe en force de **chose jugée**, `2848 C.c.Q.` : identité de parties, d'objet et de cause) des motifs;
* les **dates d'ancrage** critiques à transmettre à `gestion-du-mandat` (`conformite-echeanciers-cpc.md`) : date de l'avis du jugement (`355`, `360 C.p.c.`), jugement rendu à l'audience vs en délibéré, jugement rectifié (`338 al. 3`).

## Protection

Vérifier si la décision comporte une ordonnance de non-publication, de confidentialité ou de huis clos (`12`, `16 C.p.c.`) ou des renseignements devant demeurer caviardés au dossier public (`108 C.p.c.`).

## Ce que la pièce ne prouve pas

* Un procès-verbal sans jugement écrit rédigé ne supplée pas à une ordonnance non consignée au dispositif.
* Un jugement interlocutoire sur mesure provisoire ou d'apparence de droit ne tranche pas le fond avec autorité de la chose jugée.
* Un projet d'ordonnance non signé ou sans timbre de greffe ne constitue pas un jugement exécutoire.
