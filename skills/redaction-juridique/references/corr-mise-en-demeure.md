# Mise en demeure (`art. 1594–1597, 1605 C.c.Q.`)

Encadre la rédaction d'une mise en demeure civile ou commerciale en français ou en anglais. **Lire `lois.get_articles(law="ccq", numbers=["1594", "1595", "1597", "1605", "1619"])` avant toute version finale.**

## Objet et destinataire

* **Destinataire :** Identifier la partie débitrice exactement (personne morale via `outils.registre_search`/`registre_get_entity` avec `lei`/`portails_officiels` et adresse ou lot indicatif via `outils.adresse_verify`, à valider au REQ — et au Registre foncier s'il y a enjeu immobilier — avant signification). Si la partie adverse est représentée par avocat dans le dossier, **adresser la correspondance à l'avocat (`Code 120 al. 1`)**, ou signifier l'acte à la partie avec copie au procureur selon le contexte légal.
* **Vérification préalable :** Contrôler s'il y a déjà eu mise en demeure (une deuxième lettre sur le même défaut affaiblit la première et brouille le point de départ des intérêts) et vérifier si la demeure joue de plein droit (`1594`, `1597`).

## Mentions obligatoires

1. **Mention de transmission :** `PAR COURRIEL`, `PAR HUISSIER` ou `PAR COURRIER RECOMMANDÉ` *(préférer huissier quand la date de réception fixe le départ des intérêts `1619` ou la résolution extrajudiciaire `1605`)*.
2. **Objet :** `Objet : Mise en demeure — [objet factuel succinct]` (énoncer l'objet factuel, pas le grief).
3. **Sommation vérifiable :** Exposer l'obligation due, le défaut précis, ce qui est exigé (somme exacte ou reprise/exécution précise; chiffrer les intérêts `1619` ou `prime_plus_margin` via `outils.interets_1619`, la conversion de devise via `outils.taux_boc_rates`, l'indexation contractuelle via `outils.indice_ipc`, ou les critères d'avis de modification de bail résidentiel `1942/1955 C.c.Q.` `< 2026-01-01` vs `>= 2026-01-01` via `outils.loyer_tal`) et un **délai suffisant** proportionnel à la nature de l'obligation (`1595 C.c.Q.` — le « 10 jours » n'est pas une règle légale).

## Structure

Corps sobre (`<= 1 page` sauf dossier technique complexe) :
1. En-tête de transmission + coordonnées destinataire (`[À CONFIRMER]` si incomplet);
2. `Objet : Mise en demeure — [...]`;
3. Annonce du mandat de représentation;
4. Chronologie factuelle sobre et sans qualificatifs émotifs;
5. Écart entre l'obligation convenue/légale et l'inexécution constatée;
6. Sommation précise + **délai raisonnable et suffisant (`1595`)** + annonce sobre des recours judiciaires à défaut d'exécution (sans menace ni adjectif excessif);
7. Formule de clôture courtoise (`Veuillez agir en conséquence.` / `Yours truly,`).

## Clauses ou formules à proscrire

* **Réserve critique (`UNDER ALL RESERVES` vs `WITHOUT PREJUDICE`) :** Ne **jamais** inscrire `WITHOUT PREJUDICE` sur une mise en demeure qu'on entend **produire au tribunal** pour établir la demeure (cet en-tête vise les pourparlers transactionnels et en bloque la production). Ne pas inscrire `SOUS TOUTES RÉSERVES` par automatisme sur une mise en demeure pure; lorsque la réserve expresse de tous les droits et recours est requise en anglais, utiliser exclusivement **`UNDER ALL RESERVES`** (jamais `WITHOUT PREJUDICE` ni *Subject to all reservations*).
* **Zéro citation d'article de loi ni de jurisprudence** dans la mise en demeure (sauf exigence statutaire expresse d'un avis légal particulier).
* **Formules interdites :** « sous huitaine / quinzaine », « courrier du », « LRAR », « recommandé avec accusé de réception », *cease and desist*, *Sincerely yours*, *please be advised that*, « sous peine de procédures immédiates sans autre avis » si un préavis légal impératif s'applique.

## Contrôle

1. Relire `1594–1597`, `1605`, `1619 C.c.Q.` via `lois`.
2. Vérifier entité et adresse via `outils.registre_search` / `registre_get_entity` / `adresse_verify` (sans confondre `lot_source` parent et lot privatif).
3. Vérifier l'absence d'articles/arrêts cités dans le corps, l'absence de `WITHOUT PREJUDICE`, et exécuter `outils.terminologie_scan`.
4. Renvoyer la relecture finale de forme à `production-et-conformite` (`controle-correspondance.md`) si un envoi formel suit.
