# Anti-contamination et terminologie anglaise officielle

Tables compactes de détection et de correction pour tout projet français ou anglais devant un forum québécois. **Un seul marqueur sur un texte fourni déclenche la relecture intégrale du document.**

## 1. Contrôle outillé obligatoire (`outils` & `lois`)

1. **Analyse automatisée (`outils.terminologie_scan`) :** Exécuter sur tout projet fini (jusqu'à 32 000 caractères; scinder au-delà) pour repérer automatiquement francismes de France, calques de common law et archaïsmes procéduraux antérieurs au C.p.c. de 2016.
2. **Vérification bilingue officielle :** Ne jamais traduire littéralement un concept civil ou procédural en anglais. Appeler `lois.get_article(law="ccq"|"cpc", article="...", lang="en")` ou `outils.terminologie_lookup` et `outils.termino_attestations`.

## 2. Marqueurs français à purger (procédure, droit substantiel, sociétés)

| Marqueur français à bannir | Remplacement québécois exact |
|---|---|
| *PAR CES MOTIFS* | `POUR CES MOTIFS, PLAISE AU TRIBUNAL :` |
| *Assignation*, *exploit d'huissier* | Demande introductive d'instance, avis d'assignation; signification par huissier |
| *Conclusions* (écritures), *conclusions récapitulatives* | Actes de procédure (*conclusions* = ce qui est demandé au tribunal) |
| *Référé*, *mise en état* (juge), *ordonnance de clôture* | Injonction interlocutoire/provisoire, ordonnance de sauvegarde; protocole de l'instance, gestion d'instance, mise en état |
| *Tribunal judiciaire / de commerce*, *prud'hommes*, *Conseil d'État* | Cour supérieure, Cour du Québec, Tribunal administratif du travail; contrôle judiciaire (C.S.) |
| *Pourvoi en cassation*, *Cour de cassation* | Appel (C.A.Q.), demande d'autorisation / pourvoi (C.S.C.) |
| *Sous huitaine / quinzaine*, *sommation d'avoir à*, *CGV/CGU* | Dans un délai de huit (8) / quinze (15) jours; mise en demeure; conditions générales |
| *SARL, SAS, SASU, gérant, RCS, Kbis, RGPD* | Société par actions / inc. / ltée, administrateur/dirigeant, REQ, état de renseignements, Loi 25 (`p-39.1`) |
| *Art. 1240/1382, 2224, 1641, 1134, 1103/1109* | `1457`, `2925`, `1726 s.`, `1434`, `1399 s.` C.c.Q. |

## 3. Marqueurs de common law à purger en français (et à qualifier)

| Réflexe de common law | Traitement québécois |
|---|---|
| *Duty of care*, *standard of care*, *tort* | Faute et responsabilité extracontractuelle (`1457 C.c.Q.`) |
| *Consideration*, clause de `1 $` | Retirer (échange de consentement seul, `1385 C.c.Q.`) |
| *Estoppel*, *equitable relief*, *fiduciary duty* | Fin de non-recevoir; raisonnement civiliste; administrateur du bien d'autrui / loyauté |
| *Liquidated damages*, *punitive damages* d'office | Clause pénale (`1622`); dommages punitifs interdits sans loi habilitante (`1621`) |
| *Statement of claim*, *motion*, *discovery*, *limitation period* | Demande introductive, demande en cours d'instance, interrogatoire préalable, prescription (`2925`) |
| *Affidavit* (en français), *particulars*, *prayer for relief* | Déclaration sous serment (`105`), précisions, conclusions |
| *Indemnify and hold harmless*, *best efforts* | Garantir et prendre fait et cause; préciser obligation de moyens vs de résultat |

## 4. La règle inverse en anglais (terminologie officielle du C.p.c. / C.c.Q.)

En anglais devant un tribunal québécois, **bannir les termes de common law** (*statement of claim*, *motion*, *discovery*, *limitation period*, *tort*, *duty of care*, *consideration*, *cease and desist*) et employer les **termes officiels des textes anglais du C.c.Q. et du C.p.c.** (même lorsqu'ils ressemblent aux termes proscrits en français !) :

| Français | Anglais officiel vérifié | Source |
|---|---|---|
| acte de procédure | ***pleading*** *(valide en anglais)* | C.p.c. 99 |
| demande introductive / en cours d'instance | *originating application* / *application* | C.p.c. 100, 101 |
| déclaration sous serment | ***affidavit*** *(officiel en anglais)* | C.p.c. 105 |
| avis d'assignation / procès-verbal de signification | *summons* / *certificate of service* | C.p.c. 145, 119 |
| protocole / exposé sommaire / mise en état | *case protocol* / *brief outline of the arguments made* / *trial readiness* | C.p.c. 148, 170, 173 |
| défense / demande reconventionnelle / moyen préliminaire | *defence* / *cross-application* / *preliminary exception* | C.p.c. 170, 172, 166 |
| interrogatoire préalable / communication | *pre-trial examination* / *disclosure of exhibits and other evidence* | C.p.c. 221, 246 |
| pièce / en liasse | *exhibit* (*Exhibit P-1*) / *filed jointly* | C.p.c. 145, 246 |
| déclaration d'appel / avis du jugement | *notice of appeal* / *notice of judgment* | C.p.c. 358, 360 |
| mise en demeure / exécution en nature | *extrajudicial demand* / *specific performance* | C.c.Q. 1595, 1601 |
| acte authentique / sous seing privé / écrit d'entreprise | *authentic act* / *private writing* / *unsigned writing regularly used…* | C.c.Q. 2813, 2826, 2831 |
| prescription / délai de rigueur | *prescription* / *strict time limit* | C.c.Q. 2925; C.p.c. 148, 173 |
| réserve de droits vs pourparlers | *UNDER ALL RESERVES* vs *WITHOUT PREJUDICE* | Usage québécois |

## Règles de citation et étanchéité procédurale en anglais

* **`Article` (`art.`) c. `Section` (`s.`) :** Dans la rédaction civile québécoise en anglais, conserver **`article`** (`art.`) pour le *Civil Code of Québec* (`C.C.Q.`) et le *Code of Civil Procedure* (`C.C.P.`), et réserver **`section`** (`s.`) aux lois statutaires particulières (*CQLR*) et aux lois fédérales ; vérifier l'uniformité dans tout l'acte et l'index des autorités.
* **Quarantaine Cour fédérale / common law :** Ne jamais transposer dans une procédure civile québécoise les intitulés strictement fédéraux ou de common law (`Statement of Claim`, `Statement of Defence`, `Notice of Application` sous la *Rule 301/359* des *Règles des Cours fédérales*, `Applicant's Record` / `Applicant's Motion Record`, `Affidavit of Documents`). En Cour supérieure du Québec, les intitulés canoniques sont `Originating Application`, `Defence` / `Brief Statement of Grounds of Defence`, `Affidavit` (*terme officiel du C.p.c. en anglais à l'art. 105 C.C.P.*, parallèlement à `Sworn Statement` dans les formulaires administratifs du ministère de la Justice), `Application for Judicial Review` (`art. 529–531 C.C.P.`) et `Table of Exhibits` / `List of Exhibits` / `Book of Authorities`.
* **Cohérence linguistique corps / endos / pied de page :** Un acte rédigé en anglais exige un cartouche, un titre, un pied de page, un serment et un *endos* intégralement rédigés en anglais (aucun en-tête français résiduel issu d'un gabarit copié-collé, et vice versa pour un acte en français).
