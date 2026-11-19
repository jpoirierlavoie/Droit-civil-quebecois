# Mémoire d'appel et exposé en Cour d'appel (`C.p.c.` & `c-25.01-r.0.2.01`)

Encadre la rédaction du mémoire d'appel (`372–373 C.p.c.`) et de l'exposé (`374 C.p.c.`) devant la Cour d'appel du Québec.

## Destinataire et format

**Appeler `lois.get_articles` avant toute rédaction :**
* `law="cpc"`, `numbers=["372", "373", "374", "376"]`
* `law="c-25.01-r.0.2.01"` (*Règlement de la Cour d'appel du Québec en matière civile*) : inspecter la structure (`get_structure`) pour charger les exigences exactes de format, typographie, nombre de pages maximal, marges, pagination et confection des annexes *(les directives et avis de la Cour d'appel `QCCA` sont hors corpus Vague 1 de `110` textes et doivent être vérifiés directement à la source)*.

## Structure

* **Exposé (`374 C.p.c.`) :** Pour appels en matière familiale, intégrité/état/capacité, non contentieux, saisie, jugement en cours d'instance ou sur gestion; format abrégé soumis au règlement et à la décision de gestion.
* **Mémoire d'appel (`372–373 C.p.c.`) :**
  1. **Partie I — Les faits** *(ou énoncé commun si déposé, `372 al. 2`, sobre et appuyé aux renvois exacts aux annexes)*;
  2. **Partie II — Les questions en litige** *(avec identification explicite de la **norme d'intervention** applicable à chaque question)*;
  3. **Partie III — L'argumentation** *(structurée question par question, analyse des erreurs du jugement entrepris)*;
  4. **Partie IV — Les conclusions** *(dispositif précis recherché, y compris les frais de justice)*;
  5. **Partie V — Les sources** *(liste des autorités citées, classées selon le règlement)*;
  6. **Annexes :** Annexe I (jugement entrepris et avis), Annexe II (actes de procédure et textes légaux), Annexe III (pièces et dépositions pertinentes).

## Discipline de citation

Appliquer strictement `arg-citations.md` : citations neutres vérifiées via `juris.verify_citations`, paragraphes majoritaires vérifiés sur texte intégral lu en session, et marqueur `[RATIO / PAR. X À INSÉRER APRÈS LECTURE DE <citation + lien CanLII>]` si le texte complet manque.

## Pièges

* **Absence de norme d'intervention** ou confusion entre erreur de droit (norme de la décision correcte) et erreur de fait / mixte (erreur manifeste et déterminante).
* **Annexe III non sélective** ou non conforme aux renvois exacts de la Partie I / III; dépassement du nombre de pages réglementaire (`c-25.01-r.0.2.01`).

## Contrôle

1. Vérifier les paramètres typographiques et de pagination via `production-et-conformite` (`controler_document.py` avec les seuils lus de `c-25.01-r.0.2.01` — ou, sans Python local sur `claude.ai`, Gemini App `/mcp/oauth` ou Deep Research, divulguer explicitement les vérifications octets/XML/PDF omises et les reporter au bon de travail manuel) et le cahier des procédures/annexes (`production-et-conformite` : `cahier-des-procedures.md`).
2. Vérifier le délai de dépôt du mémoire (`373` : `3 mois` pour l'appelant, caducité si expiré sans prolongation demandée *avant* échéance) via `gestion-du-mandat`.
3. Exécuter `outils.terminologie_scan`.
