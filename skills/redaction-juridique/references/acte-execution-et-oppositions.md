# Exécution des jugements et oppositions à la saisie (`C.p.c.` Livre VIII)

[NON VALIDÉ PAR LA PRATIQUE]

À charger **avec `references/fondamentaux-actes.md`**. Encadre les actes liés à l'exécution forcée (instructions à l'huissier, avis d'exécution, interrogatoire après jugement `688`, demandes de facilitation `657` / entrée forcée `686`) et aux oppositions à la saisie ou à la vente (`735–741 C.p.c.`) sous le Livre VIII C.p.c.

## Vecteur législatif

* `law="cpc"` : `numbers=["344", "355", "656", "657", "660", "661", "680", "681", "682", "684", "686", "688", "694", "696", "735", "736", "737", "738", "739", "740", "741"]`

## Conditions et préalables

1. **Caractère exécutoire du jugement (`656`, `355`, `660–661 C.p.c.`) :**
   * Vérifier que le jugement est passé en force de chose jugée (expiration du délai d'appel `30 j` ordinaire, ou **`10 jours`** pour un jugement rendu par défaut `656 al. 2`) **ou** que la loi (`660` : p. ex. frais `<= 15 000 $`, abus, séquestre, expulsion hors bail) ou le jugement (`661`) ordonne l'exécution provisoire malgré appel;
   * Pour une décision administrative déposée au greffe (`656 al. 1`), vérifier le titre attributif de force exécutoire;
   * En appel sur quantum uniquement (`355 al. 2`), possibilité de demander l'exécution à hauteur du montant non contesté.
2. **Contrôle patrimonial et insaisissabilité (`684`, `688`, `694`, `696 C.p.c.`) :** Identifier employeur, institutions financières, biens meubles/immeubles (`outils.registre_search` / `registre_get_entity` avec `lei` et `portails_officiels` REQ/Corporations Canada/ISC-PISC ; `outils.adresse_verify(lot_number=..., matricule=...)` à titre de repérage RQA indicatif — **sans jamais substituer le RQA à l'Index des immeubles du Registre foncier du Québec ni au RDPRM**, art. `3030 al. 2, 3032 C.c.Q.`) et vérifier les biens soustraits à la saisie (`694` : meubles nécessaires jusqu'à `7 000 $`, instruments de travail personnels; `696` : titres, régimes de retraite, indemnités corporelles/morales).
3. **Ouverture d'une opposition à la saisie ou à la vente (`735 C.p.c.`) :** Vérifier l'existence d'un des motifs fermes : biens insaisissables, dette éteinte (paiement, compensation, remise), prix de vente non commercialement raisonnable, irrégularité causant un préjudice sérieux, revendication par tiers propriétaire, ou omission/imposition de charge grevant le bien (`735 al. 3–4`).

## Forum et compétence

Tribunal ayant rendu le jugement exécuté (ou tribunal du domicile du débiteur / lieu d'exécution selon `682` lorsqu'un autre créancier doit se joindre à un avis d'exécution déjà déposé dans un district donné); demandes de renseignement / entrée forcée (`684 al. 2`, `686`) devant le juge ou le greffier spécial selon la mesure.

## Structure obligatoire

* **Instructions à l'huissier & Avis d'exécution (`680–682`) :** Instructions détaillées identifiant débiteur, créance actualisée, paiements partiels, biens/employeur/tiers saisis visés et provisions versées à l'huissier (`680`); l'huissier complète et dépose l'**avis d'exécution unique** conforme au modèle ministériel (`681` — toute nouvelle mesure ou nouveau créancier passe par un **avis d'exécution modifié** dans le même dossier, `682`).
* **Demande après jugement (`657`, `684 al. 2`, `686`, `688 al. 2`) :** Demande en cours d'instance / post-jugement demandant soit l'interrogatoire d'un tiers récalcitrant sur le patrimoine du débiteur (`688 al. 2`), soit la communication de coordonnées professionnelles/résidentielles (`684 al. 2`), soit toute ordonnance propre à faciliter l'exécution (`657`), soit l'autorisation du greffier spécial pour employer la force (`686`).
* **Opposition à la saisie ou à la vente (`735–736 C.p.c.`) :** Cartouche complet + `OPPOSITION À LA SAISIE [OU À LA VENTE] ET DEMANDE EN ANNULATION / MAINLEVÉE` énonçant précisément la qualité de l'opposant (débiteur vs tiers revendiquant), la date de notification du procès-verbal (`736`), les motifs détaillés sous `735` et le titre/preuve à l'appui + Avis de présentation + Déclaration sous serment (`101 al. 3`, `105`).

## Pièces jointes et formalités

* Copie du jugement exécutoire + état des frais taxés/homologués (`344`) + décompte actualisé du capital et des intérêts + indemnité additionnelle (`art. 1619 C.c.Q.`, ou `mode="prime_plus_margin"` si le jugement condamne à un taux préférentiel + marge, calculés via `outils.interets_1619` et `conformite-quantum-interets-frais.md`);
* Procès-verbal d'exécution ou avis de vente de l'huissier (obligatoire en opposition);
* **Signification / notification stricte en opposition (`736 C.p.c.`) :** L'opposition doit être **signifiée à l'huissier, au débiteur, au créancier saisissant et au tiers-saisi**, et **notifiée aux autres créanciers et aux titulaires de droits inscrits** (Registre foncier / RDPRM) dans les **`15 jours`** de la notification du procès-verbal de saisie, de l'avis de vente ou de la saisie en mains tierces.

## Particularités et pièges

* **`684` vs `688 C.p.c.` :** L'art. `684` vise l'obligation d'information du débiteur envers l'huissier (et l'ordonnance de coordonnées `684 al. 2`), tandis que l'**interrogatoire après jugement** du débiteur ou d'un tiers sur le patrimoine relève de **`688 C.p.c.`** (sans autorisation judiciaire pour le débiteur une fois exécutoire; avec autorisation du tribunal pour un tiers non consentant).
* **Cinq limites majeures à l'effet suspensif de l'opposition (`737–741 C.p.c.`) :**
  1. L'opposition régulière opère sursis (`737 al. 1`), **sauf** si elle ne vise qu'à réduire la créance ou distraire une partie des biens — l'exécution continue alors sur la partie non contestée / autres biens (`737 al. 2`);
  2. L'opposition tardive notifiée avant la vente ne l'arrête pas sans ordonnance du tribunal pour cause suffisante (`737 al. 3`);
  3. En saisie de revenus (`738`), l'opposition ne suspend que la **distribution** des sommes retenues (pas la retenue elle-même, ni la distribution sur créance alimentaire hors motif exceptionnel);
  4. L'opposition visant les instructions d'un seul créancier n'arrête pas l'exécution pour les autres créanciers joints (`739`);
  5. Une seconde opposition après un premier rejet n'opère **aucun sursis** sauf faits nouveaux postérieurs et ordonnance sur préavis de **`2 jours`** (`741`).
* **Sanction de l'opposant débouté (`740 C.p.c.`) :** Condamnation automatique aux intérêts sur les sommes dues aux créanciers et aux frais de garde des biens pendant le temps du sursis.

## Conclusions types

* *(Exécution / Interrogatoire `657, 688`)* `AUTORISER [le Créancier / l'huissier] à interroger [Tiers] sur le patrimoine de [Débiteur] [ou ORDONNER à (Organisme) de communiquer les coordonnées connues de (Débiteur)] ;`
* *(Opposition `735`)* `ACCUEILLIR la présente opposition ; ANNULER la saisie [ou la vente projetée] pratiquée le [date] [quant aux biens suivants : ...] ; DONNER MAINLEVÉE de la saisie [ou DÉCLARER l'Opposant propriétaire et DISTRAIRE le bien saisi] ; ORDONNER la restitution des biens [ou sommes retenues] ; LE TOUT avec les frais de justice.`

## Délais (renvoi)

Articles à vérifier et chiffrer via `gestion-du-mandat` (`conformite-echeanciers-cpc.md` et `outils.calendrier_deadlines`) : `656 al. 2` (`30 jours` ou **`10 jours`** sur jugement par défaut avant exécution), `736` (**`15 jours`** pour signifier/notifier l'opposition), `741` (`2 jours` d'avis sur sursis d'une nouvelle opposition).
