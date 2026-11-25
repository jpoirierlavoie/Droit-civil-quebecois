# Recherche législative et réglementaire (`lois`)

Encadre l'interrogation du corpus législatif et réglementaire québécois et fédéral via `lois`. **Aucun champ de recherche libre `query` (`lois.find_relevant`, `lois.search_text`) ne doit recevoir de noms de clients ou faits identifiants.**

## Sources et outils

| Capacité | `lois` (LégisQuébec / Justice Canada / PDF QCCS, QCCQ, AMF) | Limite critique |
|---|---|---|
| **Texte intégral** | **Oui**, verbatim, consolidation courante | Vérifier toujours et reporter la `date de consolidation` |
| **Recherche par sujet** | **Oui** (`search_text` hybride + `find_relevant`) | Corpus fermé (**110 textes indexés** : lois, règlements, directives QCCS/QCCQ et orientations AMF) : un résultat vide ne prouve jamais l'inexistence d'une règle |
| **Historique / versions** | **Non** (pas de versions abrogées ni ancien C.p.c. c. C-25) | Confirmer la loi applicable dans le temps (fait générateur en droit substantiel vs date courante en procédure) |
| **Règlements, directives & orientations** | `list_laws(fonction=...)`, `related_laws(rel_type=...)`, `resolve_reference` | Directives C.S./C.Q. (`fonction='directive'`) et AMF (`fonction='orientation'`) en `fr`-only ; directives C.A.Q. hors vague 1 à vérifier à la source |

* **Directives de pratique et corpus AMF (`source='pdf'`, vague 1, `110` textes au total, `fr`-only) :**
  * **Cour supérieure et Cour du Québec (`fonction='directive'`, `unit='paragraphe'`, `par.`/`dir.`, textes non législatifs) :** `qccs-dist-mtl`, `qccs-div-mtl`, `qccs-div-qc`, `qccq-regles-simplifiees`, `qccq-mtl-prat-civile`, `qccq-mtl-prat-admin`, `qccq-daa-jurisprudence` *(Division administrative et d'appel de la C.Q.)*. **Aucune directive de la Cour d'appel (`QCCA`) ne figure dans la vague 1** (pour la C.A.Q., seul `c-25.01-r.0.2.01` est dans `lois` ; les directives C.A.Q. / *Avis du greffier* se vérifient à la source).
  * **Valeurs mobilières (AMF, `V-1.1`) :** Règlements édictés `v-1.1-r.10` (31-103), `v-1.1-r.21` (45-106) et `v-1.1-r.24` (51-102) (`fonction='reglement'`, `enabling='v-1.1'`, `source='pdf'`) et *Instructions générales* `amf-ig-31-103`, `amf-ig-45-106`, `amf-ig-51-102` (`fonction='orientation'`, indicatives et sans force de loi).
  * **Préséance, interprétation, renvois et annexes :** `related_laws` (et automatiquement `get_article` / `get_division` / `search_text`, en prose et `structuredContent`) expose `rel_type='preseance-sur'` (`qccs-dist-mtl` prime `qccs-div-mtl`) et `rel_type='interprete'` (`amf-ig-*` → `v-1.1-r.*`), ainsi que les hyperliens d'annexes (`articles.links` / `structuredContent.links` sur `kind='annexe'`, `ps:*`). `resolve_reference` distingue strictement `"Règlement 45-106"` de `"IG 45-106"` et refuse toute citation ambiguë (ex. `"Directives C.S."` sans division ni district).
  * **Textes publiés en français seulement (`langs: ['fr']`) :** Un appel `lang='en'` sur un texte PDF `fr`-only renvoie une erreur explicite (*published in French only (`langs: ['fr']`)*) ; dans `search_text`, les résultats sémantiques se replient sur le français et sont marqués `[fr]`.
* **Restriction de loi dans `search_text` :** Éviter de filtrer sur une seule loi sans certitude : une recherche filtrée qui renvoie un faux ami bloque l'élargissement automatique au corpus et crée un faux négatif silencieux.

## Séquence

1. Appeler **en parallèle** `lois.find_relevant(query)` et `lois.search_text(query)` — `find_relevant` pouvant omettre certains textes ciblés que `search_text` remonte d'emblée (p. ex. `490 C.p.c.`, `1726–1731 C.c.Q.`) —, ou `lois.list_laws(fonction='loi'|'regles-procedure'|'tarif'|'reglement'|'directive'|'orientation', subject=..., forum=...)` si le texte exact est inconnu (requête en concepts abstraits, zéro nom ni fait identifiant).
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
