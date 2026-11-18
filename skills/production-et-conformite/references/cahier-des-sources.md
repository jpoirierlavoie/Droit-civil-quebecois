# Confection du cahier des sources (`Book of Authorities`)

Prépare l'index et la structure du cahier des sources accompagnant un plan d'argumentation, un exposé ou un mémoire d'appel.

## Règles applicables

Vérifier les exigences particulières du tribunal et du district via `lois` (`c-25.01-r.0.2.1` C.S., `c-25.01-r.9` `art. 38, 78` C.Q., `c-25.01-r.0.2.01` `art. 60` C.A.Q.) — notamment page couverture, extraits accompagnés des pages précédente et suivante si requis en appel (`art. 60 R.C.A.Q.`), repérage visuel des passages cités (surlignement jaune, soulignement ou trait vertical en marge) et dépôt électronique avec hyperliens CanLII/LégisQuébec.

* **Correspondance 1:1 :** Chaque autorité citée au plan d'argumentation ou au mémoire — et rien d'autre — figure au cahier, classée en trois onglets : **1. Législation**, **2. Jurisprudence**, **3. Doctrine**.
* **Authentification préalable (`juris`) :** Chaque arrêt passe obligatoirement par `juris.verify_citations` et `juris.get_case` (récupérant l'hyperlien officiel CanLII et la citation neutre exacte).

## Contrôles automatisés

1. Exécuter `python scripts/controler_document.py <cahier.pdf> --exiger-couche-texte --exiger-signets --json` une fois le PDF assemblé dans les outils du cabinet pour vérifier OCR, présence de signets par onglet et validité des URI extraits.
2. Vérifier la liste de citations par `juris.verify_citations` avant l'assemblage.

## Contrôles humains

* **Structure du cahier généré :**
  * **Page couverture et index (`ONGLET 1 : … par. X à Y` / `TAB 1 : …`) :** `| Onglet | Autorité & citation complète | Paragraphes ou articles pertinents | Statut de lecture | Hyperlien CanLII / LégisQuébec |` (respecter la langue de l'acte principal dans les en-têtes d'onglets et l'ordre civiliste Législation → Jurisprudence → Doctrine);
  * Fiche par onglet : reproduction de l'article consolidé (`lois`) ou extraits vérifiés majoritaires `[par. X–Y]` tirés du texte intégral officiel fourni et lu en session (PDF ou document complet CanLII/SOQUIJ/CAIJ; jamais un sommaire ou aperçu web) ; **surligner en jaune** (ou marquer selon le règlement du tribunal) les passages précis cités au plan ou à la plaidoirie;
  * Séparation matérielle : en papier, prévoir une page intercalaire par onglet ; en PDF électronique, créer un **signet (`/Outlines`)** par onglet pointant à la première page de l'autorité (ou inclure la page couverture puis les décisions complètes/extraits surlignés);
  * Si la décision complète n'a pas encore été lue intégralement en session, maintenir le marqueur explicite **`[EXTRAITS [PAR. X] ET COPIE PDF À JOINDRE DE <citation + lien CanLII>]`**.
* **Conformité 1:1 avec l'écrit :** Aucune décision fantôme non citée au plan/mémoire, et aucune décision citée au plan absente du cahier (vérifier également l'exactitude de la mention `article` vs `section` en anglais).

## Bon de travail

Émettre le bon de travail d'assemblage pour l'outil PDF du cabinet : ordre des onglets (`Législation`, `Jurisprudence`, `Doctrine`), insertion des textes officiels/PDF complets manquants, mise en évidence des paragraphes cités (surlignement/trait en marge selon le règlement du tribunal), création des signets par onglet et contrôle OCR final.
