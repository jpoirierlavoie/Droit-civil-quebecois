# Ententes judiciaires (expertise commune, acquiescement, confidentialité, homologation)

[NON VALIDÉ PAR LA PRATIQUE]

Encadre les ententes judiciaires conclues en cours d'instance : protocole d'expertise commune (`232–234`, `535.15 C.p.c.`), acquiescement à la demande (`217–219`) et avis de règlement (`220`), entente de confidentialité / d'échange documentaire, et demande d'homologation (`527–528 C.p.c.`).

## Objet et destinataire

Parties représentées (ou non représentées avec avertissement exprès quant à l'absence de conseil indépendant) et tribunal saisi lorsque l'entente produit un effet judiciaire (mise au greffe, jugement sur acquiescement, avis de règlement `220`) ou vise l'approbation / homologation (`527–528 C.p.c.`, `2633 C.c.Q.`). Contrôler la dénomination, le `NEQ`/`LEI` et les liens officiels (`portails_officiels`) des personnes morales signataires via `outils.registre_search`/`registre_get_entity` et valider au REQ avant signature (`REGISTRE_GLEIF_DECLARATIF_CONSOLIDATION` n'établit pas le pouvoir de lier une société affiliée).

## Mentions obligatoires

Charger `lois.get_articles(law="cpc", numbers=["12", "108", "217", "218", "219", "220", "232", "233", "234", "339", "527", "528", "535.15"])` et vérifier selon l'objet :
* **Identification judiciaire :** Cour, district, chambre, numéro de dossier exact (`outils.greffe_parse_number`), désignation complète des parties et des procureurs;
* **Expertise commune (`232–233`, `535.15` — obligatoire si `< 50 000 $` sauf autorisation contraire) :** Identité et qualification de l'expert choisi d'un commun accord, questions précises soumises, documents/lieux accessibles, délai de remise du rapport, montant/plafond des honoraires et partage entre parties (avertir que sous `233 al. 2`, à défaut de dépôt au greffe exigé par l'expert, toutes les parties demeurent **tenues solidairement** envers l'expert commun);
* **Acquiescement à la demande (`217–219`) :** Portée totale ou partielle, réserves expresses le cas échéant, **mandat spécial joint obligatoirement** lorsque signé par le procureur (`217 al. 2`), sort des intérêts `1619 C.c.Q.` et des frais de justice (`339`), et renvoi à l'effet devant le greffier spécial (`218` : jugement immédiat si sans réserve; si avec réserves, délai de **`15 jours`** au demandeur pour accepter ou refuser, le silence emportant présomption d'acceptation sous réserve de relèvement avant jugement);
* **Entente de confidentialité documentaire :** Catégories de pièces visées, usage strictement limité à l'instance en cours, liste des personnes autorisées (parties, procureurs, experts liés par engagement), modalités de destruction ou restitution après jugement final, et réserve de compatibilité avec `12` / `108 C.p.c.`;
* **Règlement hors cour (`220`) / Homologation (`527–528`) :** Mention si le règlement est total ou partiel, si un jugement d'homologation est demandé (`528` : le tribunal ne vérifie que la légalité de l'acte) et demande de libération de la date d'audience / suspension des échéances.

## Structure

1. **Intitulé judiciaire :** Cartouche complet + titre exact (`ENTENTE SUR EXPERTISE COMMUNE` / `ACTE D'ACQUIESCEMENT À LA DEMANDE` / `ENTENTE DE CONFIDENTIALITÉ ET DE COMMUNICATION` / `DEMANDE EN HOMOLOGATION` / `AVIS DE RÈGLEMENT HORS COUR`);
2. **Préambule sobre :** Rappel chronologique bref du litige et du stade procédural (sans argument ni reconnaissance hors l'objet exprès);
3. **Clauses opératoires numérotées :** Rédigées au **présent de l'indicatif** civiliste, précisant obligations, échéances fermes, modalités de paiement ou dépôt au greffe, sort des frais de justice (`339`) et mécanisme de suivi;
4. **Signatures :** Date, lieu, signatures des procureurs (avec **mandat spécial annexé** pour tout acquiescement `217 al. 2`) et, lorsque requis (consentement à jugement, renonciation, entente de confidentialité engageant la partie), signatures des parties elles-mêmes.

## Clauses ou formules à proscrire

* **Confondre contrat privé de confidentialité et ordonnance judiciaire (`12 C.p.c.`) :** Une entente privée entre parties **n'oblige pas le tribunal et ne scelle pas le dossier de cour** — seule une ordonnance rendue en vertu de l'art. `12 C.p.c.` sur demande motivée permet le huis clos, l'anonymisation ou le dépôt sous pli confidentiel.
* **Omettre le mandat spécial sur acquiescement (`217 al. 2`)** ou laisser ambiguë l'étendue des frais de justice (`339`), des intérêts (`1619 C.c.Q.`) ou de la poursuite contre les codéfendeurs (`219`).
* **Imposer une transaction déguisée sans concessions réciproques** ou sans consulter `contrat-transaction-quittance.md` si l'entente éteint le litige au sens des art. `2631–2637 C.c.Q.` (sans clause de *consideration* à `1,00 $` ni termes *shall* / *without prejudice* non expliqués).

## Contrôle

1. Relire via `lois` les articles applicables (`217–220`, `232–234`, `527–528`, `535.15 C.p.c.`, `12`, `108`, `339`).
2. Valider via `gestion-du-mandat` (`conformite-echeanciers-cpc.md` et `outils.calendrier_deadlines`) les délais critiques : `15 jours` d'acceptation/refus sur acquiescement avec réserves (`218 al. 2`) et **`>= 5 jours`** de préavis sur demande en homologation/approbation contestée (`527`).
3. Vérifier s'il y a plusieurs défendeurs (`219` : risque de jugements contradictoires) et si l'entente comporte une quittance ou transaction complète (`2631 C.c.Q.`).
4. Exécuter `outils.terminologie_scan`.
