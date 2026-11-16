# Correspondance juridique, contrats, transactions et quittances

Encadre la correspondance du praticien et les actes juridiques civils et commerciaux. **Vérifier les textes via `lois.get_articles` et les entités/adresses via `outils` avant toute version finale.**

## 1. Mise en demeure (`art. 1594–1597, 1605 C.c.Q.`)

Lire `lois.get_articles(law="ccq", numbers=["1594", "1595", "1597", "1605", "1619"])` si la demeure ou la résolution extrajudiciaire est en jeu.
* **Vérification préalable :** Contrôler s'il y a déjà eu mise en demeure (une deuxième lettre sur le même défaut affaiblit la première et brouille le point de départ des intérêts) et vérifier si la demeure joue de plein droit (`1594`, `1597`).
* **Structure :**
  1. Mention de transmission (à la demande : `PAR COURRIEL`, `PAR HUISSIER`, `PAR COURRIER RECOMMANDÉ` — préférer huissier quand la date de réception fixe les intérêts ou la résolution).
  2. **Réserve critique :** Ne **jamais** inscrire `SOUS TOUTES RÉSERVES`, `UNDER ALL RESERVES` ni `WITHOUT PREJUDICE` sur une mise en demeure qu'on entend **produire au tribunal** pour établir la demeure; en anglais, distinguer `UNDER ALL RESERVES` (réserve de droits) de `WITHOUT PREJUDICE` (pourparlers transactionnels).
  3. `Objet : Mise en demeure — [objet factuel succinct]` (pas le grief).
  4. Corps sobre (`<= 1 page` sauf dossier technique complexe) : mandat → chronologie factuelle sans qualificatifs émotifs → écart entre l'obligation due et l'exécution → **demande vérifiable** (somme exacte ou reprise précise; chiffrer les intérêts art. 1619 via `outils.interets_1619` ou conclure avec intérêts/indemnité depuis la mise en demeure) → **délai suffisant** proportionnel à la nature de l'obligation (`1595` — le « 10 jours » n'est pas une règle légale) → annonce sobre des procédures sans menace excessive. **Zéro citation d'article ni de jurisprudence.**

## 2. Lettres au confrère, au client et au tribunal

| Destinataire | Appel & clôture | Règles propres |
|---|---|---|
| **Confrère / consœur** | `Maître,` / `Cher confrère,` (`Yours truly,`) | Ferme, courtois. Rédiger les lettres qui consignent un engagement ou un refus comme si un juge allait les lire. Ne pas argumenter le fond. Isoler ce qui est offert `SOUS TOUTES RÉSERVES` / `WITHOUT PREJUDICE` de ce qui est affirmé ouvertement. |
| **Client** | `Madame,` / `Monsieur,` | Seule correspondance où le droit s'explique sans jargon technique non défini. Trois éléments : (1) ce qui est arrivé, (2) portée, risques et incertitudes, (3) décision/action requise avec échéance. Marquer `CONFIDENTIEL ET PRIVILÉGIÉ`. |
| **Tribunal / Greffe** | `Madame la Juge,` / `Monsieur le Juge,` / `Madame, Monsieur,` | Bref, purement factuel (n° de cour complet, nature, objet transmis). **Zéro argumentation**; copier obligatoirement toutes les autres parties. |

*Interdits français en correspondance :* « sous huitaine/quinzaine », « courrier du », « LRAR », « recommandé avec accusé de réception », « tribunal de céans », « par ministère d'avocat », « je vous prie de bien vouloir agréer… l'expression de ma considération distinguée ». En anglais : éviter `cease and desist`, `Sincerely yours`, `kindly`, `please be advised that`, `herein`/`hereto`.

## 3. Contrats, transactions et quittances (`C.c.Q.`)

*Vecteur `law="ccq"` :* `numbers=["1379", "1385", "1432", "1434", "1435", "1436", "1437", "1438", "1474", "1604", "1605", "1606", "1621", "1622", "1733", "2631", "2633", "3148"]`.

* **Identification :** Vérifier la dénomination exacte et le NEQ via `outils.registre_search`/`registre_get_entity` (sans valeur de certificat : confirmer au REQ avant signature/signification) et l'adresse civique via `outils.adresse_verify`.
* **Formation & style civiliste :** Le contrat se forme par le seul échange de consentement (`1385`) — **supprimer toute clause de *consideration* (« moyennant 1,00 $ »)** et les doublets (`null and void`, `terms and conditions`, *shall*). Éviter les définitions pléthoriques; rédiger les obligations au **présent de l'indicatif** en précisant clairement **obligation de moyens vs obligation de résultat** (jamais « meilleurs efforts »). L'ambiguïté s'interprète contre le stipulant et toujours en faveur de l'adhérent/consommateur (`1432`).
* **Limites d'ordre public / impératives :**
  * *Résolution vs résiliation (`1604, 1606`)* : restitution rétroactive (résolution) vs pour l'avenir seulement (résiliation); exclue si défaut de peu d'importance malgré toute clause contraire.
  * *Limitation de responsabilité (`1474`)* : inopérante pour faute intentionnelle/lourde (matériel) et **totalement interdite** pour préjudice corporel ou moral.
  * *Vices cachés (`1733`)* : vendeur professionnel ne peut s'exonérer à l'aveugle; « tel que vu » limité au non-professionnel.
  * *Contrat d'adhésion (`1379, 1435–1437`)* : clauses externes nulles si non portées à la connaissance; clauses illisibles ou abusives nulles/réductibles.
  * *Dommages punitifs (`1621`)* : impossibles à créer par contrat (remplacer *liquidated damages* par une **clause pénale**, `1622`).
  * *Divisibilité (`1438`)* : supplétive par défaut (*severability* mal rédigée nuit souvent).
* **Transaction & Quittance (`2631–2637`) :** Exige des **concessions réciproques** visibles (une renonciation purement unilatérale n'est pas une transaction). Circonscrire le différend (dossier, faits, période), décider entre quittance limitée vs générale, régler frais/honoraires, confidentialité, incidence fiscale, homologation éventuelle et **mention explicite d'absence d'aveu de responsabilité**.
