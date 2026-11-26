# Argumentation écrite / notes et autorités de première instance

Encadre la rédaction d'une argumentation écrite développée ou de notes et autorités soumises en première instance lorsque permise par directive ou ordonnée/autorisée par le tribunal (distincte du simple plan d'argumentation d'audience régi par `arg-plan-argumentation.md`).

## Destinataire et format

Document remis au **juge de première instance** (jamais substituable à une conclusion absente des actes de procédure : toute conclusion oubliée requiert une demande de modification sous `206–208 C.p.c.`).
* **Autorisation ou directive préalable et échéance stricte (`267 C.p.c.`, `c-25.01-r.0.2.1 art. 47–48`) :** En première instance, la plaidoirie est **orale par défaut** — ne pas substituer un mémoire écrit complet à un *plan d'argumentation* sans directive expresse (p. ex. mémoire obligatoire `<= 10 pages` en pourvoi en contrôle judiciaire sans preuve sous `qccs-div-mtl` par. 57–59, `<= 10 pages` sur moyens préliminaires ou `<= 30 pages` sur autorisation d'action collective sous `par. 112–113`) ni permission ou demande du juge (`art. 47 R.C.s.Q.m.c.`). Avertir qu'à défaut de déposer la plaidoirie écrite dans le délai fixé à l'instruction, le juge peut prendre l'affaire en délibéré en l'état après avis (`art. 48 R.C.s.Q.m.c.`).
* Consulter via `lois.get_articles` les règlements de pratique de la Cour supérieure (`c-25.01-r.0.2.1`, `c-25.01-r.0.2.2`, `c-25.01-r.0.2.3`) et de la Cour du Québec (`c-25.01-r.9`), ainsi que les directives Vague 1 (`fonction='directive'`, `par.`/`dir.`, `fr`-only : `qccs-dist-mtl` `preseance-sur` `qccs-div-mtl`, `qccs-div-qc`, `qccq-mtl-prat-civile`, `qccq-mtl-prat-admin`, `qccq-daa-jurisprudence`; lire avec `lang='fr'`) pour le format, la police, l'interligne, les marges, la pagination, le plafond de pages et le délai de dépôt.
* Respecter strictement la langue de l'instance et l'unilinguisme dans tout le document (`anti-contamination-bilingue.md`).

## Structure

Structurer par paragraphes numérotés en continu :
1. **`INTRODUCTION ET QUESTIONS EN LITIGE`** — Thème juridique en 1–2 paragraphes, posture des parties, énoncé concis des questions que le tribunal doit trancher et réponse proposée à chacune.
2. **`TRAME FACTUELLE ÉTABLIE À L'ENQUÊTE`** *(ou, sans enquête testimoniale : **`FAITS ALLÉGUÉS TENUS POUR AVÉRÉS`** sur irrecevabilité `168 C.p.c.` / **`TRAME FACTUELLE ÉTABLIE PAR LES PIÈCES ET DÉCLARATIONS SOUS SERMENT`** en contrôle judiciaire `529 C.p.c.` ou dossier sur pièces)* — Récit chronologique sobre limité exclusivement aux faits prouvés, établis par pièces/serments recevables ou admis (`174(4°) C.p.c.`), avec renvoi systématique entre parenthèses aux cotes exactes (`Pièce P-X`, `Pièce D-Y`) et, lorsqu'il y a eu enquête orale, aux notes sténographiques (`Témoignage de [Nom], p. X, l. Y` / interrogatoire déposé `227 al. 2`).
3. **`DROIT APPLICABLE ET DISCUSSION`** — Pour chaque question en litige, suivre l'ordre civiliste (texte législatif lu via `lois` avec date de consolidation → arrêts de principe et applications vérifiés → doctrine québécoise vérifiée), puis appliquer aux faits en reliant chaque élément constitutif (et quantum `1619 C.c.Q.`) aux cotes au dossier.
4. **`RÉPONSE AUX MOYENS ADVERSES`** — Formuler objectivement la thèse adverse la plus forte soutenue à l'audience et y répondre point par point par les textes, la preuve contraire et la distinction jurisprudentielle (sans jamais formuler d'aveu interne de faiblesse).
5. **`CONCLUSIONS RECHERCHÉES`** — Reprendre **mot pour mot** les conclusions finales de l'acte de procédure avec formule introductive exacte (`POUR CES MOTIFS, PLAISE AU TRIBUNAL :`), date, lieu, signature et bloc procureur.

## Discipline de citation

Appliquer strictement `arg-citations.md` : citations neutres authentifiées via `juris.verify_citations`, paragraphes majoritaires `[par. X]` vérifiés sur texte intégral lu en session (blocs indentés en italique), et marqueur `[RATIO / PAR. X À INSÉRER APRÈS LECTURE DE <citation + lien CanLII>]` pour toute décision non lue intégralement au Palier 3.

## Pièges

* **Faits ou pièces hors preuve :** Écarter impérativement tout document non produit régulièrement (`250 C.p.c.`), tout passage d'interrogatoire hors dossier (`227 al. 2`), toute déclaration refusée ou toute allégation contestée non soutenue par la preuve.
* **Décontextualisation de transcription :** Ne jamais tronquer un extrait sténographique en omettant une réserve, une nuance en réinterrogatoire ou une objection accueillie/maintenue (`228`).
* **Conclusions nouvelles :** Ne jamais ajouter en plaidoirie écrite une réclamation, un intérêt ou une ordonnance absente des conclusions de l'acte de procédure (`345 al. 2(1°) C.p.c.` *ultra petita*).
* **Débordement en réplique écrite :** Lorsqu'un calendrier d'échange autorise une réplique écrite, la limiter strictement aux seuls points nouveaux soulevés en défense — sans répéter l'argumentation principale ni introduire un moyen neuf ou une pièce nouvelle.
* **Fuites internes et confidentialité (`108 C.p.c.`) :** Ne jamais importer les faiblesses internes (`Bloc F`), le plancher de règlement (`Bloc H`), les notes de stratégie (`[NOTE INTERNE]`) ni les identités protégées par une ordonnance de non-identification (conserver les mêmes initiales `A. B.` partout, y compris en tête de tableau et à l'endos).

## Contrôle

1. Correspondance **1:1** entre les autorités citées dans l'argumentation et l'index du cahier des sources (`production-et-conformite` / `cahier-des-sources.md`), avec numérotation continue des paragraphes et concordance exacte des conclusions.
2. Zéro proposition décisive sous `Lue (intégrale) [par. X]` au Palier 3 sans le marqueur `[RATIO / PAR. X ...]`.
3. Conformité matérielle et typographique via `controler_document.py` (polices, marges, commentaires cachés, révisions, nombre de pages; sur surface nuage sans Python local, **divulguer explicitement** que les contrôles octets/XML/PDF ont été omis et les inscrire au bon de travail manuel) et vérification de l'endos (`controle-endos-depot-signification.md`).
4. Purge linguistique exécutée via `outils.terminologie_scan`.
