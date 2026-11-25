# Recherche législative et réglementaire (`lois`)

Encadre l'interrogation du corpus législatif et réglementaire québécois et fédéral via `lois`. **Aucun champ de recherche libre `query` (`lois.find_relevant`, `lois.search_text`) ne doit recevoir de noms de clients ou faits identifiants.**

## Sources et outils

| Capacité | `lois` (LégisQuébec / Justice Canada / PDF QCCS, QCCQ, AMF) | Limite critique |
|---|---|---|
| **Texte intégral** | **Oui**, verbatim, consolidation courante | Vérifier toujours et reporter la `date de consolidation` |
| **Recherche par sujet** | **Oui** (`search_text` hybride + note marginale fédérale pondérée + `find_relevant`) | Corpus fermé (**110 textes indexés**) : un résultat vide ne prouve jamais l'inexistence d'une règle |
| **Quarantaine (8 domaines)** | Défaut `['core']` sur `list_laws`, `find_relevant`, `search_text` (sans `law`) | Ouvrir `domains=['core', '<silo>']` ou `['all']` dès que la matière touche un silo sectoriel ; inspecter le radar `other_domains` |
| **Historique / versions** | **Non** (pas de versions abrogées ni ancien C.p.c. c. C-25) | Confirmer la loi applicable dans le temps (fait générateur en droit substantiel vs date courante en procédure) |
| **Règlements, directives & orientations** | `list_laws(fonction=..., forum=...)`, `related_laws(rel_type=...)`, `resolve_reference` | Directives C.S./C.Q. (`fonction='directive'`) et AMF (`fonction='orientation'`) en `fr`-only ; aucun recueil unifié de directives QCCA (`c-25.01-r.0.2.01` seul au corpus) |

* **Quarantaine par domaine (Phase 0 — 8 domaines, paramètre `domains`, `jurisdiction` et `forum`) :**
  * **Comportement par défaut (`['core']`) :** `list_laws`, `find_relevant` et `search_text` (lorsque `law` est omis) interrogent le tronc commun `core` (`ccq`, `cpc`, règlements et directives de pratique C.S./C.Q./C.A.Q., `c-12`, `i-16`, `ca-i-21`, `ca-c-5`, `t-16`, `j-3*`, `t-15.01*`, `p-40.1`, `s-31.1`, `c-38`, `ca-c-44`, `ca-b-3`, `ca-c-36`, `ca-d-3.4`, `p-39.1`, `ca-p-8.6`, `b-1*`, `c-26`…). Les correspondances présentes dans des silos exclus déclenchent automatiquement le radar `other_domains` (`structuredContent.other_domains`).
  * **Sept silos sectoriels à ouvrir explicitement (`domains=['core', '<silo>']` ou `domains=['all']`) :**
    * `cours-federales` : *Loi sur les Cours fédérales* (`ca-f-7`) et *Règles des Cours fédérales* (`ca-dors-98-106`), isolées pour éviter les collisions avec le C.p.c. ;
    * `financier` : valeurs mobilières et AMF (`v-1.1*`, `amf-ig-*`, `d-9.2*`, `e-6.1*`, `i-13.2.2`, `i-14.01`, `t-11.002`, `a-32.1`, `c-67.3`, `e-12.000001`, `a-33.01`) ;
    * `construction-immobilier` : bâtiment/RBQ, GCR et courtage immobilier (`b-1.1*`, `c-73.2*`) ;
    * `municipal-environnement` : municipalités, fiscalité, expropriation, contrats publics et AMP (`c-19`, `c-27.1`, `f-2.1`, `c-37.01`, `e-15.1.0.1`, `e-25`, `c-65.1`, `c-65.01`, `a-33.2.1`) ;
    * `travail` : normes du travail, *Code canadien du travail*, fonction publique et divulgation (`n-1.1`, `ca-l-2`, `e-6`, `f-3.1`, `d-11.1`, `p-33.01`) ;
    * `penal` : procédure pénale, confiscation, police et déontologie policière (`c-25.1`, `c-52.2`, `p-13.1*`) ;
    * `propriete-intellectuelle` : droit d'auteur (`ca-c-42`) et marques de commerce (`ca-t-13`).
  * **Filtres `jurisdiction` et `forum` (`find_relevant`, `search_text`) :** `jurisdiction='qc'|'ca'` restreint l'ordre de gouvernement ; `forum` (p. ex. `'Cour supérieure'`, `'Cour du Québec'`, `'Cour d\'appel'`) écarte les règlements et directives propres aux autres tribunaux tout en conservant les lois substantielles transversales.
  * **Accès directs ouverts à tout le corpus :** `get_article`, `get_articles`, `get_structure`, `get_division`, `resolve_reference`, `related_laws` et `search_text(law=...)` ignorent la quarantaine par défaut (tout élargissement automatique depuis `search_text(law=...)` reste dans le domaine de la loi demandée ou dans `domains` explicite).
* **Directives de pratique et corpus AMF (`source='pdf'`, `fr`-only) :**
  * **Cour supérieure et Cour du Québec (`fonction='directive'`, `unit='paragraphe'`, `par.`/`dir.`, textes non législatifs) :** `qccs-dist-mtl`, `qccs-div-mtl`, `qccs-div-qc`, `qccq-regles-simplifiees`, `qccq-mtl-prat-civile`, `qccq-mtl-prat-admin`, `qccq-daa-jurisprudence` *(Division administrative et d'appel de la C.Q.)*. Aucun recueil unifié de directives de la Cour d'appel (`QCCA`) n'existe à l'instar de la C.S. ou de la C.Q. ; la pratique civile en appel demeure régie par `c-25.01-r.0.2.01` *(dans `lois`)* et les *Avis du greffier* publiés sur le site de la Cour.
  * **Valeurs mobilières (AMF, `V-1.1`, domaine `financier`) :** Règlements édictés `v-1.1-r.10` (31-103), `v-1.1-r.21` (45-106) et `v-1.1-r.24` (51-102) (`fonction='reglement'`, `enabling='v-1.1'`, `source='pdf'`) et *Instructions générales* `amf-ig-31-103`, `amf-ig-45-106`, `amf-ig-51-102` (`fonction='orientation'`, indicatives et sans force de loi).
  * **Préséance, interprétation, renvois et annexes :** `related_laws` (et automatiquement `get_article` / `get_division` / `search_text`, en prose et `structuredContent`) expose `rel_type='preseance-sur'` (`qccs-dist-mtl` prime `qccs-div-mtl`) et `rel_type='interprete'` (`amf-ig-*` → `v-1.1-r.*`), ainsi que les hyperliens d'annexes (`articles.links` / `structuredContent.links` sur `kind='annexe'`, `ps:*`). `resolve_reference` distingue strictement `"Règlement 45-106"` de `"IG 45-106"` et refuse toute citation ambiguë (ex. `"Directives C.S."` sans division ni district).
  * **Textes publiés en français seulement (`langs: ['fr']`) :** Un appel `lang='en'` sur un texte PDF `fr`-only renvoie une erreur explicite (*published in French only (`langs: ['fr']`)*) ; dans `search_text`, les résultats sémantiques se replient sur le français et sont marqués `[fr]`.
* **Restriction de loi dans `search_text` :** Éviter de filtrer sur une seule loi sans certitude : une recherche filtrée qui renvoie un faux ami bloque l'élargissement automatique au domaine et crée un faux négatif silencieux.

## Séquence

1. Appeler **en parallèle** `lois.find_relevant(query, domains=..., jurisdiction=..., forum=...)` et `lois.search_text(query, domains=..., jurisdiction=..., forum=...)` — cibler le ou les domaines pertinents dès l'appel (`['core', 'municipal-environnement']`, `['cours-federales']`, `['all']`, etc.) et inspecter `other_domains` au retour pour détecter d'éventuelles pistes dans un silo exclu ; utiliser `lois.list_laws(domains=..., jurisdiction=..., fonction=..., subject=..., forum=...)` si le texte exact est inconnu (requête en concepts abstraits, zéro nom ni fait identifiant).
2. `lois.get_structure(law)` (ou `lois.get_division(..., include_text=false)`) pour repérer les numéros d'articles ou paragraphes (`unit='paragraphe'`) sans charger tout un chapitre.
3. `lois.get_articles(law, numbers=[...])` en **un seul appel groupé** pour tous les articles d'une même loi, plutôt que `N` appels séquentiels `get_article`.
4. `lois.related_laws(law, rel_type=...)` pour vérifier les règlements d'application (`c-25.01-r.0.2.1`, `c-25.01-r.9`, `c-25.01-r.0.2.01`, `t-16-r.10`), la préséance entre directives (`rel_type='preseance-sur'`) et l'interprétation AMF (`rel_type='interprete'`).
5. `lois.resolve_reference(citation)` (reconnaît `par.`/`dir.` QCCS/QCCQ et `"IG 45-106"`) ou `lois.get_article(law, article, lang="en")` pour obtenir l'équivalent anglais officiel exact (hors PDF `fr`-only).

## Statuts de lecture

* **Texte officiel consolidé (`lois`) :** Article ou paragraphe lu intégralement via `lois.get_article` / `get_articles` / `get_division` avec sa **date de consolidation** relevée en session (en distinguant règle édictée `reglement` / `regles-procedure` et texte non législatif `directive` / `orientation`).
* **`[À VÉRIFIER VIA LOIS]` :** Réservé uniquement au Palier 1 exploratoire; **interdit** au Palier 2 ou 3.
* **Texte hors corpus :** Si une loi récente, directive de Cour d'appel (`QCCA`) ou règle sectorielle manque aux **110** textes de la vague 1 de `lois` (par ex. le *Règlement sur les critères de fixation de loyer*, `RLRQ, c. T-15.01, r. 2`, absent de `lois` qui ne contient que `t-15.01`), indiquer explicitement l'absence au corpus et demander à l'avocat de fournir le texte officiel (LégisQuébec, Justice Canada, tribunal ou AMF). Pour les barèmes et calculs TAL post-2026 vérifiés sur `RLRQ, c. T-15.01, r. 2`, ainsi que les taux BdC et séries IPC StatCan hors ligne, employer `outils.loyer_tal`, `outils.taux_boc_rates` et `outils.indice_ipc`.

## Modes d'échec

* **`401`, `403`, `404`, `429`, `QUOTA_EPUISE`, `INDÉTERMINÉE` ou `INTERROMPU` sur `lois` :** Sur un code HTTP **`403`** déclenché par un champ de recherche libre `query` (faux positif du pare-feu applicatif sur guillemets ou opérateurs), reformuler d'abord avec des termes juridiques neutres sans ponctuation ni opérateur, ou interroger directement par `get_structure` / `get_article` ; si le `403` persiste — ou pour tout autre code d'échec —, **arrêt obligatoire sur le volet législatif** : nommer `lois` et la cause, inviter l'avocat à rétablir l'accès sur `acces.poirierlavoie.ca/moi` ou à fournir le texte officiel, et **ne jamais basculer sur la mémoire ni sur le web**.
* **`hybride_desactive: true` sur `lois.search_text` :** Lorsque le compte titulaire a désactivé la recherche vectorielle hybride (`hybride_permis = 0` dans `acces.poirierlavoie.ca/moi`), `search_text` s'exécute strictement en mode lexical `FTS5` local ; combiner alors synonymes exacts du texte et `find_relevant`.
* **Contradiction web vs `lois` :** Le texte officiel retourné par `lois` l'emporte sans discussion; signaler la divergence.
