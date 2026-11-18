# Exécution des jugements et oppositions à la saisie (`C.p.c.` Livre VIII)

[FICHE À RÉDIGER]

À charger **avec `references/fondamentaux-actes.md`**. Encadre les actes liés à l'exécution forcée (avis d'exécution, interrogatoire après jugement, demande d'annulation / opposition à saisie ou vente, mainlevée) sous le Livre VIII C.p.c.

## Vecteur législatif

* `law="cpc"` : `numbers=["656", "660", "661", "681", "684", "735", "736", "737", "738"]` *(compléter la liste exacte via `lois.get_structure(law="cpc")`)*

## Conditions et préalables

`[FICHE À RÉDIGER]` — Vérifier si le jugement est exécutoire (expiration du délai d'appel `656` ou exécution provisoire `660–661`), si une mise en demeure de payer a été transmise, et vérifier la nature des biens saisissables ou insaisissables.

## Forum et compétence

`[FICHE À RÉDIGER]` — Tribunal qui a rendu le jugement ou tribunal du domicile / lieu de saisie selon les dispositions du Livre VIII C.p.c.

## Structure obligatoire

`[FICHE À RÉDIGER]` — Actes de demande en exécution (interrogatoire après jugement `684`, ordonnance spéciale) ou demande en **opposition à la saisie / à la vente (`735–738 C.p.c.`)** exposant les motifs d'extinction, d'insaisissabilité, d'irrégularité ou de propriété d'un tiers.

## Pièces jointes et formalités

`[FICHE À RÉDIGER]` — Jugement exécutoire, état des frais et calcul actualisé des intérêts `art. 1619 C.c.Q.` via `outils.interets_1619`, procès-verbal d'exécution de l'huissier, déclaration sous serment si opposition fondée sur faits hors dossier.

## Particularités et pièges

`[FICHE À RÉDIGER]` — Délai court de `15 jours` en opposition (`736 C.p.c.` `[À VÉRIFIER VIA LOIS]`); distinction entre opposition du débiteur et opposition d'un tiers propriétaire; suspension provisoire de l'exécution sur dépôt/signification d'opposition régulière.

## Conclusions types

`[FICHE À RÉDIGER]` — Annulation / mainlevée de saisie, suspension de vente ou autorisation d'exécution forcée avec les frais de justice.

## Délais (renvoi)

Articles à vérifier et chiffrer via `gestion-du-mandat` (`conformite-echeanciers-cpc.md` et `outils.calendrier_deadlines`) : `656` (exécution après délai d'appel), `736` (opposition à saisie/vente).
