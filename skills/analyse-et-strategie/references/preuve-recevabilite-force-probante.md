# Force probante et recevabilité générales (C.c.Q., LCJTI, C.p.c.)

Évalue ce qu'une pièce prouve en droit civil québécois et ce qui limite sa recevabilité. **Lire les textes via `lois.get_articles` avant toute conclusion formelle.**

## Qualification

Un acte de procédure allègue et **ne prouve rien**. Qualifier d'abord le **moyen de preuve** (`2811 C.c.Q.`) : écrit, témoignage (y compris déclaration écrite `292 C.p.c.` ou `2869–2870 C.c.Q.`), présomption (`2846–2849`), aveu (`2852` judiciaire vs extrajudiciaire apprécié), élément matériel (`2854–2855` photo/enregistrement exigeant preuve distincte d'authenticité sauf `art. 5 al. 3` LCJTI).

Qualification de l'écrit (`law="ccq"`):
* *Acte authentique / notarié (`2813–2821`)* : fait preuve à l'égard de tous des faits que l'officier avait mission de constater (vérifier si extrait certifié officiel REQ/Registre foncier/RDPRM ou simple impression d'écran).
* *Acte sous seing privé (`2826–2829`)* : opposé au signataire apparent, **tenu pour reconnu** s'il n'est pas contesté par déclaration sous serment avant l'inscription (`262 C.p.c.`).
* *Écrit d'entreprise non signé (`2831`)* : doit être **habituellement utilisé dans le cours des activités** (distinguer une comptabilité courante d'un chiffrier reconstitué pour le litige).
* *Autre écrit (`2832`)* / *Papier domestique (`2833`)* : un écrit non signé (courriel, capture) impose à celui qui l'invoque d'en prouver l'auteur (`2835`).

## Authentification et intégrité

Vecteurs à charger via `lois.get_articles` :
* `law="ccq"` : *fardeau/moyens* `["2803", "2804", "2811"]`; *écrits/copies* `["2813", "2814", "2818", "2819", "2821", "2822", "2826", "2828", "2831", "2832", "2833", "2835", "2860"]`; *intégrité techno/éléments matériels* `["2837", "2838", "2839", "2840", "2854", "2855"]`.
* `law="c-1.1"` (LCJTI) : `numbers=["5", "7", "12", "16"]`.
* `law="cpc"` : `numbers=["246", "248", "250", "251", "262", "292", "293"]`.

* *Original / copie (`2860`; LCJTI `12, 16`)* : demander où est l'original si seule une copie circule.
* *Intégrité technologique (`2838–2840`; LCJTI `7`)* : dispensée de preuve sauf preuve d'altération (relever capture recadrée, fil tronqué, horodatage incohérent).

## Recevabilité

Vecteur `law="ccq"` : `numbers=["2843", "2850", "2852", "2857", "2858", "2862", "2863", "2864", "2865", "2869", "2870"]`.

* *Preuve testimoniale d'un acte juridique (`2862`) vs contradiction d'un écrit (`2863–2865`)* : la preuve testimoniale d'un acte juridique est plafonnée à `1 500 $` `[À VÉRIFIER VIA LOIS]`, sauf commencement de preuve (`2865`) ou à l'égard d'un acte fait dans le cours des activités d'une entreprise (`2862 al. 2`); indépendamment de la valeur en litige, le témoignage ne peut jamais contredire ou changer les termes d'un écrit constatant un écrit valablement fait (`2863`, sous réserve de l'interprétation sous `2864` ou du commencement de preuve sous `2865`).
* *Ouï-dire (`2843, 2869–2870`)* : une lettre ou un rapport relatant les dires d'un tiers ne prouve pas leur véracité sans consentement ou autorisation avec garanties sérieuses.
* *Preuve obtenue illégalement (`2858`)* : rejet d'office si atteinte aux droits fondamentaux + déconsidération (et rejet **sans** critère de déconsidération en cas de violation du secret professionnel).

## Force probante

Synthétiser systématiquement le poids probatoire au regard du fardeau (`2803 C.c.Q.`) et de la norme de la prépondérance des probabilités (`2804 C.c.Q.`) :
* Fait **Établi** (pièce signée non contestée, acte authentique, aveu judiciaire);
* Fait **Rapporté** (correspondance unilatérale, écrit non signé non encore attribué);
* Fait **Déduit** ou **`[À CONFIRMER]`**.

## Protection

Renvoyer toute question de secret professionnel, privilège de litige ou de règlement, ou caviardage (`108 C.p.c.`, Loi 25) à `preuve-privilege-confidentialite-caviardage.md`.

## Ce que la pièce ne prouve pas

Énoncer en conclusion en deux points : (1) ce que la pièce **prouve** vs (2) ce qu'elle **ne prouve pas** (notamment : l'auteur d'un écrit non signé sous `2835`, l'authenticité d'un chiffrier monté pour les fins du procès hors `2831`, la véracité des dires d'un tiers sous `2843`, ni l'absence d'altération d'un document technologique fragmentaire).
