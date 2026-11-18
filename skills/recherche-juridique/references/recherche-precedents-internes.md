# Exploitation de précédents et procédures d'autres dossiers (savoir-faire interne)

[NON VALIDÉ PAR LA PRATIQUE]

Encadre la recherche de leçons apprises et de modèles tirés d'autres dossiers fournis par l'avocat, dans le respect strict du secret professionnel et des règles de conflit d'intérêts.

## Sources et outils

* **Source unique permise :** Documents fournis directement par l'avocat dans la session (procédures déposées, jugements, mémoires, notes d'analyse). **Aucun accès ni recherche automatique vers d'autres dossiers n'existe.**
* **Hiérarchie de fiabilité :**
  1. **Jugements rendus et actes de procédure déposés au greffe** (publics, tranchés ou formalisés — rang supérieur);
  2. **Plans d'argumentation et cahiers remis au tribunal**;
  3. **Notes internes ou mémoires de travail** (rang inférieur : reflètent une hypothèse d'avocat, non une décision judiciaire).
* **Outils d'ancrage :** `lois.get_articles` (vérifier si les textes invoqués dans le précédent sont toujours en vigueur à la date courante), `juris.verify_citations` (contrôler l'état des arrêts cités dans le précédent).

## Séquence

1. **Dé-identification obligatoire à l'entrée :** Avant toute extraction réutilisable, masquer ou écarter noms des parties, numéros de dossier de cour, montants identifiants, adresses, pièces et faits particuliers de l'ancien dossier. **Ne jamais transporter aucun fait, nom ni pièce de l'autre dossier dans le dossier courant.**
2. **Alerte de conflit d'intérêts :** Vérifier immédiatement si une partie, un témoin clé, un adversaire ou un enjeu du précédent fourni évoque un lien avec le dossier courant susceptible de déclencher un conflit (`Code de déontologie`, `b-1-r.3.1` art. 64, 71, 87–88) — si oui, déclencher le signalement déontologique avant toute utilisation.
3. **Extraire uniquement le savoir-faire transférable :**
   * structure et plan de la procédure ou du mémoire;
   * arguments juridiques et moyens retenus ou écartés;
   * issue obtenue (succès, rejet, nuance du jugement) et ce qui a fonctionné ou échoué;
   * objections adverses rencontrées et parades efficaces.
4. **Revalider le droit au texte courant :** Un précédent même récent peut citer une règle modifiée (p. ex. seuil art. 35 C.p.c., régime simplifié art. 535.1 s.); relire chaque texte via `lois` et chaque arrêt via `juris`.

## Statuts de lecture

* Tout principe tiré d'un précédent interne porte la mention d'origine (**jugement / acte déposé** vs **note interne du cabinet**).
* Les citations jurisprudentielles reprises d'un précédent restent au statut `Rapportée` jusqu'à vérification via `juris.verify_citations` et lecture du texte intégral officiel pour le Palier 3.

## Modes d'échec

* **Fait ou nom importé par contagion :** Bloquer et purger immédiatement toute donnée factuelle étrangère au dossier courant.
* **Précédent antérieur au C.p.c. de 2016 ou non vérifié :** Signaler les termes ou articles obsolètes (« requête », ancien C.p.c. `c. C-25`) et réancrer sur les textes courants via `lois`.
* **Indice de conflit d'intérêts :** Suspendre l'exploitation et diriger vers le contrôle des conflits (`gestion-du-mandat` / `conformite-ouverture-conflits-mandat`).
