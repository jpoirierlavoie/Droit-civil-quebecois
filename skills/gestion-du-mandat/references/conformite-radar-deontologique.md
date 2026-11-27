# Radar déontologique : 11 moments, vecteurs MCP et silences du texte

**Aucune citation statique n'est reproduite ici :** charger obligatoirement le seul sous-lot pertinent via `lois.get_articles` sur `law="b-1-r.3.1"` (*Code de déontologie des avocats*), `law="b-1-r.5"` (*Règlement sur la comptabilité et les normes d'exercice professionnel*) et `law="cpc"` avant d'énoncer une obligation.

## Déclencheurs

Ne signaler une obligation déontologique qu'en présence d'un déclencheur concret (ou d'une question directe) : jamais de mise en garde générique hors contexte.

| Moment | Déclencheurs concrets |
|---|---|
| **1. Ouverture & conflits** | Nouveau mandat, ancien client, clients multiples, avocat témoin, compétence/temps |
| **2. Mandat & honoraires** | Portée limitée, aide juridique, modalités financières, forfait, tiers payeur, disponibilité |
| **3. Conduite, accès & archives** | Sous-traitance essentielle, dossier abusif, offre de règlement, erreur/omission préjudiciable, copie/rectification, fermeture (7 ans) |
| **4. Confidentialité & IA** | Tous renseignements du client (plus large que le secret `c-12 art. 9`, `b-1 art. 131`, `c-26 art. 60.4`), infonuagique/IA, prévention violence |
| **5. Conflit en cours** | Différend en mandat commun, apparition d'un conflit, demande en inhabilité, juge lié |
| **6. Fidéicommis** | Avances, chèques, soldes, espèces `>= 7 500 $`, conciliation mensuelle/annuelle |
| **7. Partie adverse & confrère** | Courriel direct d'une **personne représentée** (`120 al. 1`), engagement (`44`), tactiques dilatoires |
| **8. Devoirs envers le tribunal** | Autorités IA non vérifiées (`116`), pièce/preuve fausse ou à conserver (`117`), communication hors audience avec le juge (`121`) |
| **9. Témoins** | Entrevue de témoin (`120 al. 2` déclarer intérêts), usurpation (`122`), compensation permise vs prohibée (`123`) |
| **10. Fin du mandat** | Cessation volontaire vs obligatoire, mise en demeure `192`, autorisation du tribunal après fixation `194` |
| **11. Cessation d'exercice** | Retraite, fonction incompatible, cessionnaire au décès/inaptitude, prise de possession syndic |

## Vecteur

| Moment | Articles à charger via `lois.get_articles` (`b-1-r.3.1`, `b-1-r.5`, `cpc`) |
|---|---|
| **1. Ouverture & conflits** | `b-1-r.3.1`: `["29", "64", "71", "72", "74", "76", "77", "83", "84", "86", "87", "88"]`; `b-1-r.5`: `["11", "13", "14", "20", "21", "22", "23", "24", "25", "26", "27"]` |
| **2. Mandat & honoraires** | `b-1-r.3.1`: `["28", "31", "34", "48", "99", "100", "101", "102", "103", "104", "105", "106", "107", "108", "109", "110"]`; `b-1-r.5`: `["54", "55"]` |
| **3. Conduite, accès & archives** | `b-1-r.3.1`: `["20", "21", "22", "23", "25", "26", "30", "35", "36", "37", "38", "39", "40", "41", "42", "43", "45", "46", "47", "53", "54", "55", "57", "58", "59", "73", "90", "91", "92", "93"]`; `b-1-r.5`: `["15", "16", "18", "19"]` |
| **4. Confidentialité & IA** | `b-1-r.3.1`: `["21", "35", "60", "61", "62", "63", "65", "66", "67", "68", "69", "70", "112", "116"]`; `b-1-r.5`: `["17", "29"]` |
| **5. Conflit en cours** | `b-1-r.3.1`: `["48", "49", "51", "76", "80", "85"]`; `cpc`: `["192", "193"]` |
| **6. Fidéicommis** | `b-1-r.3.1`: `["94", "95", "96", "97"]`; `b-1-r.5`: `["28", "29", "30", "31", "32", "33", "34", "38", "39", "40", "41", "42", "43", "44", "45", "46", "50", "51", "52", "53", "54", "56", "57", "58", "59", "60", "61", "62", "63", "64", "65", "66", "69", "70", "71", "72", "73"]` |
| **7. Partie adverse & confrère** | `b-1-r.3.1`: `["43", "44", "112", "113", "115", "118", "119", "120"]` |
| **8. Devoirs envers le tribunal** | `b-1-r.3.1`: `["79", "80", "111", "114", "116", "117", "118", "121"]` |
| **9. Témoins** | `b-1-r.3.1`: `["76", "115", "117", "120", "122", "123"]` |
| **10. Fin du mandat** | `b-1-r.3.1`: `["48", "49", "50", "51", "52", "65", "96", "97"]`; `cpc`: `["192", "194"]` |
| **11. Cessation d'exercice** | `b-1-r.5`: `["74", "75", "76", "77", "78", "79", "80", "81", "82"]` |

## Obligations

* **Rappeler, jamais attester :** Dire qu'une vérification est due; ne jamais écrire qu'elle a été accomplie sans preuve directe.
* **Distinguer devoir écrit et usage :** Ne jamais présenter une coutume de courtoisie comme une règle du Code.
* **Usages d'IA (5 points d'ancrage) :** Compétence technologique (`21 al. 2`), supervision et jugement non délégués (`20, 35`), confidentialité infonuagique (`60–63`; `Règl. 17, 29`), aucune heure fictive si l'outil accélère (`99, 101, 102(2°)`), sincérité et vérification officielle des autorités (`112, 116`).
* **Bureau du syndic (`Code 70`) :** Mentionner le recours consultatif au syndic devant un doute sérieux sur la confidentialité ou un conflit aigu.

## Silences et paires confondables

### Les 19 silences du texte (*Ce que le texte ne dit pas*)
1. **Méthode de recherche de conflits :** aucune procédure ni moment précis imposés (`64, 71, 83, 87` imposent le résultat).
2. **Convention d'honoraires écrite :** exigée seulement pour intérêts sur souffrance (`103`), forfait (`104`), disponibilité acquise (`Règl. 54(2)/55`).
3. **Honoraires conditionnels / pourcentage :** `Code 109` est marqué « (Inopérant) ».
4. **Contenu complet du dossier :** `Règl. 13–14, 22` (identification, nature du mandat, pièces de vérification); `Règl. 16` (procédures / correspondance / autres).
5. **Délai de conservation des pièces d'identité :** délai général de 7 ans après fermeture (`Règl. 18`).
6. **Règles techniques courriel / chiffrement / IA :** aucune norme technique précise hors `Code 21, 60–63, 116` et `Règl. 15, 17, 22, 29, 30`.
7. **Délais de grâce entre confrères :** usages professionnels non codifiés dans `112–113`.
8. **Autorités défavorables :** aucune règle déontologique n'oblige à les citer (`116–117` visent l'erreur et la preuve).
9. **Demandes ex parte :** rien dans `121` (communications hors tribunal avec le juge).
10. **Exactitude des allégations de procédure :** seules `116` et `117` encadrent erreur et preuve.
11. **Préparation des témoins :** rien hors fausseté, identité et rémunération (`115, 117, 122–123`).
12. **Divulgation d'offres de règlement au tribunal :** `43` traite seulement de la transmission au client.
13. **Cessation obligatoire pour conflit en cours :** hors mandat commun (`85`), `49` ne nomme pas le conflit (`48(4)` = faculté).
14. **Droit de rétention pour honoraires impayés :** `96` renvoie aux « cas prévus par la loi » sans les énumérer.
15. **Définitions comptables liminaires :** relire `Règl. 1–10` via `lois` en cas de doute.
16. **Praticien seul et `Code 104` :** l'art. 104 mentionne « au sein d'un cabinet ».
17. **Point de départ des 10 jours de `192 C.p.c.` :** court de la notification de la **mise en demeure**, jamais du retrait de l'avocat.
18. **Cadence de reddition de compte (`40`) et réponse (`39`) :** seulement « périodiquement ou sur demande » et « disponibilité raisonnable ».
19. **Forme du consentement en mandat commun (`84`) :** consentement après 3 informations, sans exigence d'écrit.

### Paires de numéros à ne pas confondre

| Paire | Distinction essentielle |
|---|---|
| `Code 48` vs `49` | `48` : faculté (« peut » cesser; inclut conflit `48(4)`). `49` : obligation (« cesse »; ne nomme pas le conflit). |
| `Code 64` vs `87` / `88` | `64` : secret d'un autre client. `87` : ne pas agir contre un ancien client (`88` : autre avocat du cabinet). |
| `Code 83 / 84 / 85` | `83` : intérêts opposés. `84` : consentement informé préalable. `85` : différend en cours de mandat commun. |
| `Code 99 / 100 / 101 / 102` | `99` : info financière préalable + variations. `100` : explication relevé. `101` : justes. `102` : 9 critères. |
| `Code 53` vs `57` | `53` : accès/copie du dossier. `57` : restitution d'une pièce confiée (demande écrite). |
| `Code 116` vs `119` | `116` : ne pas tromper le **tribunal**. `119` : ne pas tromper **partie / avocat**. |
| `Code 120` vs `121` | `120` : partie représentée (`al. 1`) et témoin (`al. 2`). `121` : juge hors audience. |
| `Règl. 13–14` vs `20–27` | `13–14` : **identification** dans *tout* dossier. `20–27` : **vérification** d'identité (mouvements de fonds hors transfert électronique, sauf dispenses `21`). |
| `Règl. 18 / 31 / 32 / 82` | 7 ans : `18` et `31` dès fermeture; `32` fin d'exercice financier; `82` dossiers non repris. |
| `Règl. 50 / 54 / 56 / 58 / 62` | `50` général; `62` particulier; `54` sommes interdites au général; `56/58` retraits permis et modalités. |
| `Règl. 57 / 69 / 70 / 71 / 72` | `70` reçu *toutes* espèces; `69` plafond `7 500 $`; `71` déclaration 30 j si `>= 7 500 $`; `57/72` retrait/remboursement en espèces. |
| `Code 51` vs `C.p.c. 194` | Cumulatifs : `51` (avis client/partie/tribunal) + `194` (greffier; autorisation si instruction fixée). |
