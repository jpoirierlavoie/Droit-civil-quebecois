# Exécution des jugements et oppositions à la saisie (`C.p.c.` Livre VIII)

À charger **avec `references/fondamentaux-actes.md`**. Encadre les actes liés à l'exécution forcée (instructions à l'huissier, avis d'exécution, saisie en mains tierces `711–716`, interrogatoire après jugement `688–689`, demandes de facilitation `657` / coordonnées `684 al. 2` / entrée forcée `686`) et aux oppositions à la saisie ou à la vente (`735–741 C.p.c.`) sous le Livre VIII C.p.c.

## Vecteur législatif

* `law="cpc"` : `numbers=["30", "344", "355", "656", "657", "659", "660", "661", "680", "681", "682", "684", "686", "688", "689", "694", "696", "698", "699", "711", "712", "713", "714", "716", "735", "736", "737", "738", "739", "740", "741"]`
* `law="c-25.01-r.0.2.1"` : `numbers=["31"]`

## Conditions et préalables

1. **Caractère exécutoire du jugement (`656`, `355`, `660–661 C.p.c.`) :**
   * Vérifier que le jugement est passé en force de chose jugée (expiration du délai de `30 jours` ordinaire ou aux petites créances, ou **`10 jours`** pour tout jugement rendu par défaut `656 al. 2`) **ou** que la loi (`660` : p. ex. frais `<= 15 000 $`, abus, séquestre, expulsion hors bail) ou le jugement (`661 al. 1`) ordonne l'exécution provisoire malgré appel — **attention (`661 al. 2`)** : si l'exécution provisoire facultative n'a pas été ordonnée par le jugement lui-même, elle ne peut plus l'être qu'en appel ;
   * Pour une décision administrative déposée au greffe (`656 al. 1`), vérifier le titre attributif de force exécutoire ;
   * En appel sur quantum uniquement (`355 al. 2`), possibilité de demander l'exécution à hauteur du montant non contesté.
2. **Contrôle patrimonial et insaisissabilités (`684`, `688`, `694`, `696`, `698–699 C.p.c.`) :** Identifier employeur, institutions financières, biens meubles et immeubles (`outils.registre_search` / `registre_get_entity` avec `lei` et `portails_officiels` REQ/Corporations Canada/ISC-PISC ; `outils.adresse_verify(lot_number=..., matricule=...)` à titre de repérage RQA indicatif — **sans jamais substituer le RQA à l'Index des immeubles du Registre foncier du Québec ni au RDPRM**, art. `3030 al. 2, 3032 C.c.Q.`) et vérifier les biens soustraits à la saisie (`694` : meubles nécessaires jusqu'à `7 000 $`, instruments de travail personnels ; `696` : titres hors entreprise, régimes de retraite, indemnités corporelles ou morales ; `698–699` : portion insaisissable des revenus — pour laquelle le **travailleur autonome** ou le salarié d'un employeur hors Québec doit conclure une entente d'échelonnement avec l'huissier ou faire un dépôt volontaire, `699`).
3. **Ouverture et qualité en opposition à la saisie ou à la vente (`735 C.p.c.`) :** Vérifier l'existence d'un motif légal : biens insaisissables, dette éteinte, prix proposé non commercialement raisonnable, irrégularité causant un préjudice sérieux, droit de revendication d'un tiers propriétaire, ou omission/imposition d'une charge grevant le bien (`735 al. 1, 3–4`). **Limite de qualité (`735 al. 2`) :** les autres créanciers du débiteur ne peuvent pas s'opposer à la saisie elle-même, mais uniquement **à la vente projetée** si le prix proposé n'est pas commercialement raisonnable ou s'il existe un risque d'irrégularités graves.

## Forum et compétence

Toutes les demandes, contestations ou oppositions en matière d'exécution sont présentées comme demandes en cours d'instance, **instruites et jugées sans délai** (`659 al. 1 C.p.c.`, `c-25.01-r.0.2.1 art. 31 a)–b)`), dans le district du tribunal qui a rendu le jugement (`659 al. 2` — l'huissier pouvant toutefois saisir le tribunal ou le greffier spécial du district du lieu d'exécution, notamment sous `686`). Si l'exécution vise plusieurs jugements joints (`682`) rendus par des paliers différents, la compétence appartient à la Cour du Québec ou, **dès qu'un jugement de la Cour supérieure est visé, à la Cour supérieure (`659 al. 3`)**.

## Structure obligatoire

* **Instructions à l'huissier, Avis d'exécution et Saisie en mains tierces (`680–682`, `711–716 C.p.c.`) :** Instructions détaillées identifiant débiteur, créance actualisée, paiements partiels, biens/employeur/tiers-saisis visés et provisions versées (`680`) ; dépôt par l'huissier de l'**avis d'exécution unique** conforme au modèle ministériel (`681` — toute nouvelle mesure ou jonction d'un autre créancier passe par un **avis modifié**, `682`). En saisie en mains tierces (`711–716`), le tiers-saisi devient gardien (`712`) et déclare à l'huissier dans les **`10 jours`** ce qu'il doit ou détient (`711 al. 1`).
* **Demandes incidentes après jugement (`657`, `684 al. 2–3`, `686`, `688–689`, `711 al. 2`, `714 C.p.c.`) :**
  * *Interrogatoire après jugement (`688–689`)* : convocation du débiteur (sans autorisation judiciaire dès que le jugement est exécutoire) ou demande d'autorisation d'interroger un tiers non consentant (`688 al. 2`) ; à défaut d'entente sur le moment et le lieu, **citation à comparaître devant le tribunal signifiée au moins `5 jours` à l'avance (`689 al. 1`)** ;
  * *Coordonnées du débiteur (`684 al. 2–3`)* : demande présentée **par l'huissier** afin d'ordonner à un tiers ou organisme public de lui fournir les coordonnées résidentielles et professionnelles du débiteur (exécutoire malgré les lois sur la confidentialité, **sous réserve du respect du secret professionnel**, `684 al. 3`) ;
  * *Contestation de déclaration ou évaluation de rémunération (`711 al. 2`, `714`)* : contestation de la déclaration du tiers-saisi dans les **`10 jours`** (`711 al. 2`), ou demande sur préavis d'au moins **`5 jours`** afin de fixer la juste rémunération du débiteur travaillant gratuitement ou à rabais (`714`, jugement sans appel) ;
  * *Facilitation (`657`) ou entrée forcée (`686`)* : ordonnance propre à faciliter l'exécution (`657`) ou autorisation du greffier spécial du lieu d'exécution pour employer la force (`686`).
* **Opposition à la saisie ou à la vente (`735–736 C.p.c.`) :** Cartouche complet + `OPPOSITION À LA SAISIE [OU À LA VENTE] ET DEMANDE EN ANNULATION / MAINLEVÉE` énonçant la qualité de l'opposant, la date de notification du procès-verbal ou de l'avis (`736`), les motifs détaillés sous `735` et le titre/preuve à l'appui + Avis de présentation + Déclaration sous serment (`101 al. 3`, `105`).

## Pièces jointes et formalités

* Copie du jugement exécutoire + état des frais vérifiés/homologués (`344`) + décompte actualisé du capital, des intérêts et de l'indemnité additionnelle (`art. 1619 C.c.Q.`, ou `mode="prime_plus_margin"` si taux préférentiel + marge, calculés via `outils.interets_1619` et `conformite-quantum-interets-frais.md`) ;
* Procès-verbal de saisie, déclaration du tiers-saisi (`711`, congé de saisie possible aux frais du saisissant sous `716` si aucune dette n'existe) ou avis de vente ;
* **Signification / notification stricte en opposition (`736 C.p.c.`) :** L'opposition doit être **signifiée à l'huissier, au débiteur, au créancier saisissant et au tiers-saisi**, et **notifiée aux autres créanciers et aux titulaires de droits inscrits** (Registre foncier / RDPRM) dans les **`15 jours`** de la notification du procès-verbal de saisie, de l'avis de vente ou de la saisie en mains tierces.

## Particularités et pièges

* **`684` vs `688–689 C.p.c.` :** L'art. `684` régit la divulgation patrimoniale due par le débiteur à l'huissier (et la demande de coordonnées présentée par l'huissier sous `684 al. 2–3`), tandis que l'**interrogatoire après jugement** enregistré du débiteur ou d'un tiers relève de **`688–689 C.p.c.`**.
* **Cinq limites majeures à l'effet suspensif de l'opposition (`737–741 C.p.c.`) :**
  1. L'opposition régulière opère sursis (`737 al. 1`), **sauf** si elle ne tend qu'à réduire la créance ou à distraire une partie des biens — l'exécution continue alors sur le solde non contesté ou les autres biens (`737 al. 2`) ;
  2. L'opposition tardive notifiée avant la vente ne l'arrête pas sans ordonnance du tribunal pour cause suffisante (`737 al. 3`) ;
  3. En saisie de revenus (`738`), l'opposition ne suspend que la **distribution** des sommes saisies (ni la retenue, ni la distribution alimentaire hors motifs exceptionnels) ;
  4. L'opposition visant les seules instructions d'un créancier n'arrête pas l'exécution pour les autres créanciers joints (`739`) ;
  5. Une nouvelle opposition après un premier rejet n'opère **aucun sursis** sauf faits postérieurs et ordonnance sur préavis de **`2 jours`** (`741`).
* **Sanction de l'opposant débouté (`740`) et appel sur permission (`30 al. 2(8°) C.p.c.`) :** L'opposant débouté est tenu des intérêts sur la somme due aux créanciers et des frais de garde pendant le sursis (`740`), et **tout jugement rendu en matière d'exécution n'est appelable que sur permission d'un juge de la Cour d'appel (`30 al. 2(8°) C.p.c.`)** (sauf la décision fixant la juste rémunération sous `714`, qui est **sans appel**).

## Conclusions types

* *(Interrogatoire / Tiers-saisi `688 al. 2, 714`)* `AUTORISER [le Créancier / l'huissier] à interroger [Tiers] sur le patrimoine de [Débiteur] [ou FIXER à (...) $ par (...) la juste rémunération du Débiteur auprès de la Tierce saisie à compter de la demande] ;`
* *(Demande de l'huissier `684 al. 2–3`)* `ORDONNER à [Organisme / Tiers], sous réserve du secret professionnel, de fournir à l'huissier instrumentant les renseignements dont il dispose sur les coordonnées résidentielles et professionnelles de [Débiteur] ;`
* *(Opposition `735`)* `ACCUEILLIR la présente opposition ; ANNULER la saisie [ou la vente projetée] pratiquée le [date] [quant aux biens suivants : ...] ; DONNER MAINLEVÉE de la saisie [ou DÉCLARER l'Opposant propriétaire et DISTRAIRE le bien saisi] ; ORDONNER la restitution des biens [ou sommes retenues] ; LE TOUT avec les frais de justice.`

## Délais (renvoi)

Articles à vérifier et chiffrer via `gestion-du-mandat` (`conformite-echeanciers-cpc.md` et `outils.calendrier_deadlines`) : `656 al. 2` (`30 jours` ou **`10 jours`** sur jugement par défaut avant exécution), `689 al. 1` (`>= 5 jours` citation à comparaître à l'interrogatoire après jugement), `711` (`10 jours` déclaration du tiers-saisi + `10 jours` contestation), `714` (`>= 5 jours` demande d'évaluation de juste rémunération), `736` (**`15 jours`** pour signifier/notifier l'opposition), `741` (`2 jours` d'avis sur sursis d'une nouvelle opposition), `30 al. 2(8°)` et `360 al. 1` (`30 jours` permission d'appeler en matière d'exécution).
