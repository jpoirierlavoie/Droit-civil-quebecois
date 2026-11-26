# Analyse des documents judiciaires (procès-verbaux, jugements, ordonnances)

Encadre la lecture et la qualification des procès-verbaux d'audience ou de signification, jugements, ordonnances et décisions administratives ou étrangères (portée, dates d'ancrage procédurales, inscription de faux et autorité de la chose jugée).

## Qualification

Charger `lois.get_articles(law="cpc", numbers=["30", "31", "32", "158", "258", "263", "321", "322", "334", "335", "338", "349", "355", "360", "389", "507", "508", "656", "660", "661"])` et `law="ccq", numbers=["2804", "2813", "2814", "2815", "2816", "2818", "2820", "2821", "2822", "2825", "2848", "3155"]` puis qualifier la nature exacte de l'acte :
* **Jugement final au fond (`30, 321 C.p.c.`) :** Met fin à l'instance ou statue sur le litige ; dessaisit le juge et acquiert force de chose jugée dès qu'il n'est pas ou n'est plus susceptible d'appel (`321 al. 2`) — sous réserve des jugements révisables pour faits nouveaux ou non contentieux sans caractère définitif (`322 C.p.c.`) ;
* **Jugement rendu en cours d'instance / mesure de gestion (`31, 32, 158 C.p.c.`) :** Distinguer ce qui concerne la conduite de l'instance (`32`, sans appel) de ce qui décide en partie du litige ou cause un préjudice irrémédiable (`31`, appel sur permission, ou de plein droit sur rejet d'une objection fondée sur le secret professionnel, la discrétion ministérielle ou la source journalistique) ;
* **Ordonnance provisoire, sauvegarde ou injonction (`49, 158(8°), 509–512 C.p.c.`) :** Portée temporelle limitée et régime d'exécution provisoire spécifique (`514, 660`) ;
* **Procès-verbal d'audience ou jugement inscrit à l'acte (`334 al. 2 C.p.c.`, `c-25.01-r.0.2.1 art. 52`, `c-25.01-r.9 art. 56`) :** Constat officiel du greffier quant aux présences, admissions et dépôts ; un jugement rendu à l'audience (même au fond) est **valablement constaté par l'inscription de la décision et de ses principaux considérants au procès-verbal attesté par celui qui l'a rendu** (`334 al. 2`), ou signé à même la demande en cours d'instance (`art. 52` / `art. 56`) ;
* **Décision administrative déposée au greffe (`656 al. 1 C.p.c.`), arrêt (`389 C.p.c.`) ou jugement étranger (`507–508 C.p.c.`) :** Vérifier la disposition attribuant force exécutoire, le dispositif majoritaire et les dissidences (`389 al. 1`), ou le statut d'exemplification étrangère.

## Authentification et intégrité

* Vérifier le numéro de dossier de cour (`outils.greffe_parse_number`), le district, la juridiction (`palais_get`), le nom du juge ou greffier spécial, la signature et le timbre/sceau du greffe (ou copie certifiée conforme délivrée sous `335 al. 2 C.p.c.`).
* **Primauté de l'original sur le plumitif (`334 al. 3 C.p.c.`) :** En cas de divergence entre le jugement original signé et les entrées des registres (*plumitif*), le jugement original prévaut.
* Pour toute décision publiée invoquée, authentifier la citation neutre, le dispositif majoritaire et l'histoire postérieure via `juris.verify_citations`, `juris.get_case` et `juris.subsequent_history`.
* Vérifier si une rectification postérieure existe (`338 C.p.c.`).

## Recevabilité

* **Acte authentique et inscription de faux (`2813–2816, 2818, 2820–2821 C.c.Q.` ; `258 C.p.c.`) :** Le jugement ou registre judiciaire fait preuve à l'égard de tous des faits que le juge, le greffier ou l'huissier avait mission de constater ou d'inscrire (`2818`), et les copies ou extraits authentiques suppléent à l'original (`2815–2816, 2820`). L'**inscription de faux (`2821 C.c.Q.`, `258 C.p.c.`)** est obligatoire pour contredire ces constatations officielles (ex. présence à l'audience, constatations personnelles d'un procès-verbal de signification), mais non pour contester la qualité ou la signature de l'officier public ni les simples déclarations des parties rapportées dans l'acte.
* **Décision ou acte public étranger : valeur semi-authentique c. exécution (`2822, 2825, 3155 s. C.c.Q.` ; `263, 507–508 C.p.c.`) :** Un acte ou jugement émanant apparemment d'un officier public étranger compétent fait preuve de son contenu comme acte semi-authentique (`2822`), sauf contestation obligeant celui qui l'invoque à prouver son authenticité (`2825 C.c.Q.`, `263 C.p.c.`). Pour être **reconnu et rendu exécutoire** au Québec (`3155 s. C.c.Q.`, `507–508 C.p.c.`), il doit être accompagné de l'attestation officielle de son caractère définitif ou exécutoire dans l'État d'origine (`508 al. 1`), des preuves certifiées de notification régulière s'il a été rendu par défaut (`508 al. 2`) et d'une traduction certifiée au Québec — **obligatoirement en français lorsque le demandeur est une personne morale (`508 al. 3 C.p.c.`)**.

## Force probante

Distinguer strictement :
* **Dispositif c. motifs et triple identité de la chose jugée (`2848 al. 1–2 C.c.Q.`) :** Seul ce qui fait l'objet du **dispositif** (et son soutien nécessaire) acquiert l'autorité de la **chose jugée** (présomption absolue exigeant l'identité de cause, de parties agissant dans les mêmes qualités et d'objet — étendue aux membres non exclus en action collective selon `2848 al. 2`) ; les *obiter dicta* n'emportent pas chose jugée. À l'égard des tiers, le jugement demeure opposable comme fait juridique ou titre, sous réserve de leur droit à la tierce opposition s'il préjudicie à leurs droits (`349 C.p.c.`).
* **Dates d'ancrage impératives (à transmettre immédiatement à `gestion-du-mandat` / `conformite-echeanciers-cpc.md`) :**
  * date du jugement rendu à l'audience en présence des parties c. date de l'**avis du jugement** (`335, 360 al. 1 C.p.c.`) pour le calcul des délais de rigueur de `30 j` / `10 j` / `5 j` ;
  * date d'une rectification affectant le **dispositif** (`338 al. 3` : fait courir à nouveau le délai d'appel ou d'exécution) ;
  * date d'exécutabilité (`656 al. 2` : expiration du délai d'appel, `10 j` sur jugement par défaut, ou exécution provisoire `355, 660–661`).

## Protection

Vérifier si la décision comporte une ordonnance de non-publication, d'anonymisation, de confidentialité ou de huis clos (`12`, `15`, `16 C.p.c.`) ou des renseignements devant demeurer caviardés au dossier public (`108 C.p.c.`, Loi 25).

## Ce que la pièce ne prouve pas

* Une simple remarque orale à l'audience non consignée au procès-verbal attesté par le juge (`334 al. 2 C.p.c.`) ni dans un jugement signé ne constitue pas une ordonnance exécutoire, et une entrée erronée au plumitif ne prévaut jamais sur le jugement original (`334 al. 3`).
* Un jugement interlocutoire sur mesure provisoire ou d'apparence de droit, ou un jugement révisable (`322 C.p.c.`), ne tranche pas définitivement le fond avec autorité de la chose jugée (`2848 C.c.Q.`).
* Un acquittement criminel ou pénal (rendu selon la norme du doute raisonnable) n'emporte pas chose jugée faisant obstacle à la responsabilité civile appréciée selon la prépondérance des probabilités (`2804 C.c.Q.`).
* Un projet d'ordonnance non signé ou sans attestation du juge ou du greffier compétent ne constitue pas un jugement exécutoire.
