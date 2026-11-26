# Transaction et quittance (`art. 2631–2637 C.c.Q.`)

Encadre la rédaction d'une transaction civile ou commerciale mettant fin à un différend ou prévenant une contestation, la quittance associée et les actes procéduraux de clôture du dossier. **Lire `lois.get_articles(law="ccq", numbers=["2631", "2632", "2633", "2634", "2635", "2636", "2637"])` et `lois.get_articles(law="cpc", numbers=["213", "217", "218", "219", "220", "527", "528"])` avant toute version finale.**

## Objet et destinataire

* **Nature (`2631 C.c.Q.`) :** Contrat nommé par lequel les parties préviennent une contestation à naître, terminent un procès ou règlent les difficultés d'exécution d'un jugement au moyen de **concessions ou réserves réciproques**.
* **Identification :** Vérifier la dénomination exacte, le NEQ et la chaîne de groupe (`lei`, `portails_officiels` REQ/Corporations Canada/ISC-PISC) des personnes morales signataires via `outils.registre_search`/`registre_get_entity` (sans valeur de certificat ni preuve de contrôle juridique sous `REGISTRE_GLEIF_DECLARATIF_CONSOLIDATION` : confirmer au REQ avant signature et circonscrire expressément les sociétés affiliées visées par la quittance) et les adresses via `outils.adresse_verify`.

## Mentions obligatoires

1. **Concessions réciproques visibles (`2631`) :** Une renonciation purement unilatérale sans contrepartie/concession réciproque n'est pas une transaction et risque la requalification.
2. **Circonscription exacte du différend :** Numéro(s) de dossier de cour, faits, contrat visé et période couverte.
3. **Absence d'aveu de responsabilité :** Mention explicite que le règlement est conclu pour éviter les coûts et aléas du litige et **ne constitue aucun aveu de responsabilité ou de faute**.
4. **Sort du dossier judiciaire et mécanisme procédural de clôture :**
   * *Avis de règlement hors cour (`220 C.p.c.`)* : à déposer **sans délai** au greffe pour libérer le rôle — ne jamais confondre avec un *désistement* unilatéral (`213 C.p.c.`), qui met les frais de justice à la charge du demandeur sauf convention expresse *sans frais* ;
   * *Paiements échelonnés et homologation (`2633 al. 2 C.c.Q.`, `527–528 C.p.c.`)* : un avis de règlement seul n'est pas exécutoire par saisie forcée sans homologation (`528` : contrôle de légalité uniquement, préavis `>= 5 jours` si contesté sous `527`) — retenir la quittance finale / le désistement jusqu'à encaissement complet ou prévoir l'homologation en cas de défaut ;
   * *Acquiescement à la demande (`217–219 C.p.c.`)* : joindre obligatoirement un **mandat spécial (`217 al. 2`)** s'il est signé par le procureur, régler les intérêts (`1619 C.c.Q.`) et frais (`339`), et surveiller le délai de **`15 jours`** en cas de réserves (`218 al. 2`, présomption d'acceptation en cas de silence) ainsi que les codéfendeurs (`219`).

## Structure

1. Identification complète des parties (et représentants autorisés);
2. **Préambule (Attendus) :** exposé neutre du litige et des procédures en cours (interpréter sobrement, le préambule éclaire l'intention);
3. **Objet et concessions réciproques :** paiement (montant, modalités, chèque visé / virement en fidéicommis, délai, défaut), exécution d'obligations, ou remises;
4. **Quittance (limitée vs générale) :** distinguer la quittance limitée au litige visé de la quittance générale et finale (et vérifier les tiers / codébiteurs solidaires `1523 s.`, assureurs, recours subrogatoires);
5. **Frais et honoraires :** qui paie les frais de justice, honoraires extrajudiciaires et droits de greffe;
6. **Confidentialité et non-dénigrement** *(sous réserve des exceptions légales et fiscales)*;
7. **Incidence fiscale :** préciser le cas échéant la qualification / TPS-TVQ ou renvoi aux conseillers fiscaux;
8. **Clauses finales :** transaction au sens de `2631–2637 C.c.Q.` (autorité de la chose jugée `2633`), intégralité, droit applicable (Québec), signature en exemplaires / technologique (`c-1.1`).

## Clauses ou formules à proscrire

* **Clause de *consideration* (« moyennant la somme nominale de 1,00 $ »)** — calque de common law à supprimer (`1385`, `2631 C.c.Q.`).
* **Doublets anglais / archaïsmes :** *null and void*, *terms and conditions*, *release and forever discharge* traduits littéralement en français lourd.
* **Quittance générale aveugle :** Faire renoncer par mégarde à des droits futurs, garanties légales ou autres relations commerciales non visées par le litige sans mandat exprès du client.

## Contrôle

1. Relire `2631–2637 C.c.Q.` via `lois` et contrôler les effets à l'égard des codébiteurs/cautions le cas échéant (`1530`, `1690` C.c.Q.).
2. Vérifier que les concessions réciproques et l'absence d'aveu sont expresses.
3. Vérifier la concordance avec les règles de fidéicommis (`gestion-du-mandat` / `conformite-facturation-fideicommis.md`) pour tout chèque ou virement reçu/déboursé.
4. Exécuter `outils.terminologie_scan`.
