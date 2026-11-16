# Radar déontologique : 11 moments, vecteurs MCP et silences du texte

**Aucune citation statique n'est reproduite ici :** charger obligatoirement le seul sous-lot pertinent via `lois.get_articles` sur `law="b-1-r.3.1"` (*Code de déontologie des avocats*), `law="b-1-r.5"` (*Règlement sur la comptabilité et les normes d'exercice professionnel*) et `law="cpc"` avant d'énoncer une obligation.

## 1. Carte des 11 moments et vecteurs `lois.get_articles`

| Moment | Déclencheurs concrets | Articles à charger (`b-1-r.3.1`, `b-1-r.5`, `cpc`) |
|---|---|---|
| **1. Ouverture & conflits** | Nouveau mandat, ancien client, clients multiples, avocat témoin, compétence/temps | `b-1-r.3.1`: `["29", "64", "71", "72", "74", "76", "77", "83", "84", "86", "87", "88"]`; `b-1-r.5`: `["11", "13", "14", "20", "21", "22", "23", "24", "25", "26", "27"]` |
| **2. Mandat & honoraires** | Portée limitée, aide juridique, modalités financières, forfait, tiers payeur, disponibilité | `b-1-r.3.1`: `["28", "31", "34", "48", "99", "100", "101", "102", "103", "104", "105", "106", "107", "108", "109", "110"]`; `b-1-r.5`: `["54", "55"]` |
| **3. Conduite, accès & archives** | Sous-traitance essentielle, dossier abusif, offre de règlement, erreur/omission préjudiciable, copie/rectification, fermeture (7 ans) | `b-1-r.3.1` (*conduite/diligence*) : `["20", "21", "22", "23", "25", "26", "30", "35", "36", "37", "38", "39", "40", "41", "45", "46"]`; *règlement/erreur/tiers* : `["42", "43", "47", "73"]`; *accès/archives* : `["53", "54", "55", "57", "58", "59", "90", "91", "92", "93"]`; `b-1-r.5`: `["15", "16", "18", "19"]` |
| **4. Confidentialité & IA** | Tous renseignements du client (plus large que le secret `c-12 art. 9`, `b-1 art. 131`, `c-26 art. 60.4`), infonuagique/IA, prévention violence | `b-1-r.3.1`: `["21", "35", "60", "61", "62", "63", "65", "66", "67", "68", "69", "70", "112", "116"]`; `b-1-r.5`: `["17", "29"]` |
| **5. Conflit en cours** | Différend en mandat commun, apparition d'un conflit, demande en inhabilité, juge lié | `b-1-r.3.1`: `["48", "49", "51", "76", "80", "85"]`; `cpc`: `["192", "193"]` |
| **6. Fidéicommis** | Avances, chèques, soldes, espèces `>= 7 500 $`, conciliation mensuelle/annuelle | `b-1-r.3.1`: `["94", "95", "96", "97"]`; `b-1-r.5` (*registres/conciliation*) : `["28", "29", "30", "31", "32", "33", "34", "38", "39", "40", "41", "42", "43", "44", "45", "46"]`; *dépôts/retraits/comptes* : `["50", "51", "52", "53", "54", "56", "57", "58", "59", "60", "61", "62", "63", "64", "65", "66"]`; *espèces* : `["69", "70", "71", "72", "73"]` |
| **7. Partie adverse & confrère** | Courriel direct d'une **personne représentée** (`120 al. 1`), engagement (`44`), tactiques dilatoires | `b-1-r.3.1`: `["43", "44", "112", "113", "115", "118", "119", "120"]` |
| **8. Devoirs envers le tribunal** | Autorités IA non vérifiées (`116`), pièce/preuve fausse ou à conserver (`117`), communication hors audience avec le juge (`121`) | `b-1-r.3.1`: `["79", "80", "111", "114", "116", "117", "118", "121"]` |
| **9. Témoins** | Entrevue de témoin (`120 al. 2` déclarer intérêts), usurpation (`122`), compensation permise vs prohibée (`123`) | `b-1-r.3.1`: `["76", "115", "117", "120", "122", "123"]` |
| **10. Fin du mandat** | Cessation volontaire vs obligatoire, mise en demeure `192`, autorisation du tribunal après fixation `194` | `b-1-r.3.1`: `["48", "49", "50", "51", "52", "65", "96", "97"]`; `cpc`: `["192", "194"]` |
| **11. Cessation d'exercice** | Retraite, fonction incompatible, cessionnaire au décès/inaptitude, prise de possession syndic | `b-1-r.5`: `["74", "75", "76", "77", "78", "79", "80", "81", "82"]` |

**Usages d'IA (5 points d'ancrage) :** Compétence technologique (`21 al. 2`), supervision et jugement non délégués (`20, 35`), confidentialité infonuagique (`60–63`; `Règl. 17, 29`), aucune heure fictive si l'outil accélère (`99, 101, 102(2°)`), sincérité et vérification officielle des autorités (`112, 116`).

## 2. Les 19 silences du texte (*Ce que le texte ne dit pas*)

*Une absence de règle écrite ne crée ni une permission ni un usage obligatoire — la signaler sans la combler (et vérifier au besoin `Code 1–19`, `124 s.`, `Règl. 1–10` via `lois`) :*
1. **Méthode de recherche de conflits :** aucune procédure, aucun registre ni moment précis imposés (seules des interdictions de résultat aux art. 64, 71, 83, 87).
2. **Convention d'honoraires écrite :** non exigée en général (écrit exigé seulement pour intérêts sur souffrance `103`, forfait `104`, disponibilité acquise `Règl. 54(2)/55`).
3. **Honoraires conditionnels / pourcentage :** `Code 109` est marqué « (Inopérant) ».
4. **Contenu complet du dossier :** `Règl. 13–14, 22` exigent seulement identification, nature du mandat et pièces de vérification; `Règl. 16` sépare procédures / correspondance / autres.
5. **Délai de conservation des pièces d'identité :** aucun délai propre; délai général de 7 ans après fermeture (`Règl. 18`).
6. **Règles techniques courriel / chiffrement / IA :** aucune norme technique précise (seuls `Code 21, 60–63, 116` et `Règl. 15, 17, 22, 29, 30` + directives des tribunaux).
7. **Délais de grâce et préavis de défaut entre confrères :** usages professionnels, non codifiés dans `112–113`.
8. **Autorités défavorables :** aucune règle déontologique n'oblige à les citer (`116–117` visent l'erreur et la preuve).
9. **Demandes ex parte :** rien dans `121` (qui vise les communications hors tribunal avec le juge).
10. **Exactitude des allégations de procédure :** seules `116` et `117` encadrent erreur et preuve.
11. **Préparation des témoins :** rien hors fausseté, identité et rémunération (`115, 117, 122–123`).
12. **Divulgation d'offres de règlement au tribunal :** `43` traite seulement de la transmission au client (la confidentialité relève du privilège/C.p.c.).
13. **Cessation obligatoire pour conflit en cours de mandat :** hors mandat commun (`85`), `49` ne nomme pas le conflit (simple faculté sous `48(4)`), et aucun consentement général n'est prévu hors `74, 84, 87`.
14. **Droit de rétention pour honoraires impayés :** `96` renvoie aux « cas prévus par la loi » sans les énumérer.
15. **Définitions comptables liminaires :** relire `Règl. 1–10` via `lois` si la qualification d'un fonds est en doute.
16. **Praticien seul et `Code 104` :** l'art. 104 mentionne « au sein d'un cabinet »; le texte tait l'étendue exacte au praticien seul quant à la description détaillée.
17. **Point de départ des 10 jours de `192 C.p.c.` :** court de la notification de la **mise en demeure** (formulation passive), jamais du retrait de l'avocat.
18. **Cadence de reddition de compte (`40`) et réponse (`39`) :** seulement « périodiquement ou sur demande » et « disponibilité raisonnable ».
19. **Forme du consentement en mandat commun (`84`) :** consentement après 3 informations, sans exigence d'écrit.

## 3. Paires de numéros à ne pas confondre

| Paire | Distinction essentielle |
|---|---|
| `Code 48` vs `49` | `48` : faculté (« peut » cesser; inclut conflit `48(4)`). `49` : obligation (« cesse »; ne nomme pas le conflit). |
| `Code 64` vs `87` / `88` | `64` : refuser un mandat risquant d'utiliser un secret d'un autre client. `87` : ne pas agir contre un ancien client (`88` : autre avocat du cabinet). |
| `Code 83 / 84 / 85` | `83` : interdit si intérêts opposés. `84` : consentement informé préalable. `85` : différend en cours de mandat commun. |
| `Code 99 / 100 / 101 / 102` | `99` : information financière préalable + variations. `100` : explication du relevé. `101` : honoraires/avances justes. `102` : 9 critères. |
| `Code 53` vs `57` | `53` : accès/copie du dossier. `57` : restitution d'une pièce confiée (demande écrite). |
| `Code 116` vs `119` | `116` : ne pas tromper le **tribunal**. `119` : ne pas tromper **partie / avocat**. |
| `Code 120` vs `121` | `120` : partie représentée (`al. 1`) et témoin (`al. 2`). `121` : juge hors audience. |
| `Règl. 13–14` vs `20–27` | `13–14` : **identification** dans *tout* dossier. `20–27` : **vérification** d'identité (seulement réception/débours/virement de fonds hors transfert électronique, sauf dispenses `21`). |
| `Règl. 18 / 31 / 32 / 82` | 7 ans : `18` et `31` dès la fermeture du dossier; `32` fin d'exercice financier; `82` dossiers non repris. |
| `Règl. 50 / 54 / 56 / 58 / 62` | `50` compte général; `62` compte particulier (revenus exigés); `54` sommes interdites au général; `56/58` retraits permis et modalités. |
| `Règl. 57 / 69 / 70 / 71 / 72` | `70` reçu pour *toutes* espèces; `69` plafond `7 500 $` (sauf 6 exceptions); `71` déclaration 30 j si `>= 7 500 $`; `57/72` retrait/remboursement en espèces. |
| `Code 51` vs `C.p.c. 194` | Cumulatifs : `51` (avis client/partie/tribunal + délai raisonnable) + `194` (notification au greffier; autorisation du tribunal si instruction fixée). |
