# Analyse des documents judiciaires (procès-verbaux, jugements, ordonnances)

[NON VALIDÉ PAR LA PRATIQUE]

Encadre la lecture et la qualification des procès-verbaux d'audience, jugements, ordonnances et décisions administratives (portée, dates d'ancrage procédurales et autorité de la chose jugée).

## Qualification

Charger `lois.get_articles(law="cpc", numbers=["30", "31", "32", "158", "321", "335", "338", "355", "360", "389", "656", "660", "661"])` et `law="ccq", numbers=["2813", "2814", "2818", "2848", "3155"]` puis qualifier la nature exacte de l'acte :
* **Jugement final au fond (`30, 321 C.p.c.`) :** Met fin à l'instance ou statue sur le litige; dessaisit le juge et acquiert force de chose jugée dès qu'il n'est pas ou n'est plus susceptible d'appel (`321 al. 2`);
* **Jugement rendu en cours d'instance / mesure de gestion (`31, 32, 158 C.p.c.`) :** Distinguer ce qui concerne la conduite de l'instance (`32`, sans appel) de ce qui cause un préjudice irrémédiable ou détermine le droit (`31`, appel sur permission);
* **Ordonnance provisoire, sauvegarde ou injonction (`49, 158(8°), 509–512 C.p.c.`) :** Portée temporelle limitée et régime d'exécution provisoire spécifique (`660`);
* **Procès-verbal d'audience ou de gestion (`c-25.01-r.0.2.1`) :** Constat officiel du greffier quant aux présences, admissions séance tenante, dépôts et ordonnances rendues à l'audience;
* **Décision administrative déposée au greffe (`656 al. 1 C.p.c.`) ou arrêt (`389 C.p.c.`) :** Vérifier la disposition attribuant force exécutoire ou le dispositif majoritaire et les dissidences (`389 al. 1`).

## Authentification et intégrité

* Vérifier le numéro de dossier de cour (`outils.greffe_parse_number`), le district, la juridiction (`palais_get`), le nom du juge ou greffier spécial, la signature et le timbre/sceau du greffe (ou copie certifiée conforme délivrée sous `335 al. 2 C.p.c.`).
* Pour toute décision publiée invoquée, authentifier la citation neutre, le dispositif majoritaire et l'histoire postérieure via `juris.verify_citations`, `juris.get_case` et `juris.subsequent_history`.
* Vérifier si une rectification postérieure existe (`338 C.p.c.`).

## Recevabilité

* **Acte authentique (`2813–2818 C.c.Q.`) :** Fait preuve à l'égard de tous des constatations que le juge ou l'officier public avait mission d'énoncer (les copies certifiées conservent la force de l'original selon `2819–2821 C.c.Q.`).
* **Décision rendue hors du Québec (`3155 s. C.c.Q.`, `507–508 C.p.c.`) :** Ne devient exécutoire au Québec qu'après demande en reconnaissance et exécution (sauf exception légale ou conventionnelle) et contrôle des motifs de refus (`3155 C.c.Q.`).

## Force probante

Distinguer strictement :
* **Dispositif vs motifs (`2848 C.c.Q.`) :** Seul ce qui fait l'objet du **dispositif** (et son soutien nécessaire) passe en force de **chose jugée** (présomption absolue exigeant l'identité de cause, de parties agissant dans les mêmes qualités et d'objet); les *obiter dicta* ou constatations incidentes n'emportent pas chose jugée.
* **Dates d'ancrage impératives (à transmettre immédiatement à `gestion-du-mandat` / `conformite-echeanciers-cpc.md`) :**
  * date du jugement rendu à l'audience en présence des parties vs date de l'**avis du jugement** (`335, 360 al. 1 C.p.c.`) pour le calcul des `30 j` / `10 j` / `5 j`;
  * date d'une rectification affectant le **dispositif** (`338 al. 3` : fait courir à nouveau le délai d'appel ou d'exécution);
  * date d'exécutabilité (`656 al. 2` : expiration du délai d'appel, `10 j` en défaut, ou exécution provisoire `355, 660–661`).

## Protection

Vérifier si la décision comporte une ordonnance de non-publication, de confidentialité ou de huis clos (`12`, `16 C.p.c.`) ou des renseignements devant demeurer caviardés au dossier public (`108 C.p.c.`, Loi 25).

## Ce que la pièce ne prouve pas

* Un procès-verbal sans jugement écrit rédigé ne supplée pas à une ordonnance non consignée au dispositif.
* Un jugement interlocutoire sur mesure provisoire ou d'apparence de droit ne tranche pas le fond avec autorité de la chose jugée (`2848 C.c.Q.`).
* Un projet d'ordonnance non signé ou sans timbre de greffe ne constitue pas un jugement exécutoire.
