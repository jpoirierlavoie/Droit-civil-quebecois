# Demande d'injonction (provisoire, interlocutoire et permanente)

[NON VALIDÉ PAR LA PRATIQUE]

À charger **avec `references/fondamentaux-actes.md`**. Encadre la rédaction des demandes d'injonction provisoire (`510 al. 2`), interlocutoire (`510–512`) et permanente (`509 s.`) en Cour supérieure.

## Vecteur législatif

* `law="cpc"` : `numbers=["33", "49", "58", "105", "360", "361", "509", "510", "511", "512", "513", "514", "515", "660"]`

## Conditions et préalables

1. Vérifier les exclusions légales (`513 C.p.c.`) : aucune injonction ne peut être prononcée pour empêcher des procédures judiciaires ni pour faire obstacle à l'exercice d'une fonction au sein d'une personne morale de droit public ou privé (hors `329 C.c.Q.`).
2. Rassembler les faits soutenant chaque critère cumulatif devant être **allégué factuellement** dans l'acte (sans réciter la jurisprudence ni plaider dans les allégations de fait) :
   * **Apparence de droit (`511 al. 1`) :** question sérieuse à trancher en injonction interlocutoire prohibitoire, ou **apparence de droit claire / forte *prima facie*** lorsqu'une injonction obligatoire ou décidant de fait le litige est recherchée;
   * **Préjudice sérieux ou irréparable (`511 al. 1`) :** atteinte non adéquatement compensable par des dommages-intérêts, ou risque qu'un état de fait ou de droit rende le jugement au fond inefficace;
   * **Prépondérance des inconvénients :** comparaison concrète des impacts sur les parties si l'injonction est accordée vs refusée;
   * **Urgence immédiate (injonction provisoire `510 al. 2`) :** péril imminent ne permettant pas d'attendre l'audition interlocutoire (exclure l'urgence auto-créée par inaction prolongée), avec plafond strict de **`10 jours`** sans consentement des parties.
3. Confirmer la capacité du demandeur à offrir un **cautionnement** ou engagement d'indemnisation (`511 al. 2`).

## Forum et compétence

Compétence exclusive de la **Cour supérieure** (`33`, `509 C.p.c.`, hors injonctions sectorielles attribuées par loi particulière). Contrôler la salle, l'heure et les directives d'urgence du district saisi (`c-25.01-r.0.2.1`; directives C.S. Vague 1 via `lois` `lang='fr'` et `outils.palais_get`).

## Structure obligatoire

1. Cartouche complet + Désignation + Titre exact : **`DEMANDE EN INJONCTION [PROVISOIRE / INTERLOCUTOIRE / PERMANENTE]`** `(Articles 509 et suivants du Code de procédure civile)` (intégrée à la demande introductive ou présentée en cours d'instance, voire avant dépôt si urgence extrême selon `510 al. 1` et `512 al. 2`);
2. Exposé chronologique sobre et numéroté (`99 C.p.c.`) : qualité des parties, droits violés ou menacés, faits établissant chacun des critères cumulatifs (apparence, préjudice, balance, et urgence distincte pour le provisoire) et absence d'obstacle sous `513`;
3. Ordonnances demandées formulées avec une précision chirurgicale : qui est visé (incluant dirigeants/représentants d'une personne morale/groupement selon `509 al. 1`), actes précis prohibés (`de ne pas faire / cesser de faire`) ou ordonnés (`d'accomplir`), territoire, durée exacte et modalités de cautionnement (`511 al. 2`);
4. Conclusions + Signature + **Avis de présentation** + **Déclaration(s) sous serment** circonstanciée(s) (`105`, `510`).

## Pièces jointes et formalités

* **Déclaration sous serment rigoureuse (`105`, `510`) :** Faits personnels précis, date, lieu, sources directes; si plusieurs témoins détiennent des faits clés (ex. constatations techniques ou financières), joindre autant de déclarations sous serment distinctes que nécessaire.
* **Signification par huissier (`509 al. 2`, `510 al. 1`, `512`) :** Signifier la demande et l'avis de présentation (sauf présentation provisoire avant signification en cas d'urgence sous `510 al. 2`); une fois prononcée, **signifier l'ordonnance elle-même** aux parties et à toutes les personnes qui y sont nommées/identifiées (si la demande introductive n'avait pas encore été déposée, la signifier dans le délai fixé par le juge selon `512 al. 2`).
* **Offre / versement du cautionnement (`511 al. 2`) :** Prévoir dès le dépôt les modalités (consignation, caution bancaire ou dispense motivée) afin d'éviter qu'une ordonnance obtenue soit paralysée faute de sûreté fournie.

## Particularités et pièges

* **Terme français *référé* strictement banni :** Toujours employer *demande d'injonction provisoire* / *interlocutoire* (`510 C.p.c.`).
* **Dispositif imprécis = ordonnance inapplicable en outrage (`58 s.`) :** Toute ambiguïté profite au débiteur visé; éviter les formules vagues (« cesser toute concurrence déloyale ») et décrire le geste concret visé.
* **Effet en appel (`514`, `515`, `361 al. 1`, `660`) :** L'injonction interlocutoire demeure en vigueur malgré un appel à moins d'être suspendue (`514`, `515`); le délai d'appel d'un jugement qui met fin à une injonction interlocutoire est réduit à **`10 jours`** (`361 al. 1`, appel sur permission `31 C.p.c.` selon le cas).

## Conclusions types

* *(Provisoire `<= 10 j`)* `PRONONCER une ordonnance d'injonction provisoire, exécutoire immédiatement et malgré tout appel, enjoignant à [la Défenderesse], à ses dirigeants, représentants, employés et ayants cause de [s'abstenir de / accomplir précisément ...], pour une durée n'excédant pas dix (10) jours à compter des présentes ;`
* *(Interlocutoire)* `PRONONCER une ordonnance d'injonction interlocutoire enjoignant à [la Défenderesse] de [objet précis] jusqu'à jugement final au fond sur la demande principale ;`
* *(Cautionnement et signification)* `[ASSUJETTIR la délivrance de l'ordonnance à un cautionnement de (...) $ / DISPENSER du cautionnement ;] ABRÉGER le délai de signification et AUTORISER la signification en dehors des heures légales / par moyen technologique si requis ;`
* *(Permanente / Frais)* `ACCUEILLIR la demande d'injonction permanente ; RENDRE PERMANENTE l'ordonnance énoncée ci-dessus ; LE TOUT avec les frais de justice.`

## Délais (renvoi)

Articles à vérifier et chiffrer via `gestion-du-mandat` (`conformite-echeanciers-cpc.md` et `outils.calendrier_deadlines`) : `510 al. 2` (durée maximale `10 jours` de l'injonction provisoire), `510 al. 1` / `512 al. 2` (signification avec avis de présentation et délai fixé si non déposée), `360–361 al. 1` (`10 jours` en appel sur jugement mettant fin à l'injonction interlocutoire).
