# Politique de sécurité et de confidentialité (`SECURITY.md`)

## Signalement d'une vulnérabilité ou d'un incident de confidentialité

**Ne jamais ouvrir d'issue GitHub publique** pour signaler une faille de sécurité, une fuite de secret ou un enjeu touchant le secret professionnel.

- **Canal privé prioritaire :** [Avis de sécurité privé GitHub](https://github.com/jpoirierlavoie/droit-civil-quebecois/security/advisories/new)
- **Courriel de contact :** `jason@poirierlavoie.ca`
- **Délai d'accusé de réception :** dans les **72 heures**.

### Portée

Cette politique couvre le greffon **`droit-civil-quebecois`** ainsi que les dépôts d'infrastructure associés (`MCP-Legislation`, `MCP-Jurisprudence`, `MCP-Outils`, `MCP-Socle`).

---

## Secrets et authentification

1. **Aucune donnée d'authentification dans le dépôt :** `.mcp.json`, `mcp_config.json` et `gemini-extension.json` référencent uniquement les variables d'environnement `${MCP_LEGISLATION_SECRET}` et `${MCP_JURISPRUDENCE_SECRET}` (marquées `sensitive: true` dans `gemini-extension.json`).
2. **Isolation des serveurs MCP :**
   - **`lois`** (`https://legislation.poirierlavoie.ca/mcp`) : authentification par secret partagé (`Authorization: Bearer`) en comparaison à temps constant SHA-256 ; garde non-oracle **HTTP 404** avant même la validation de méthode HTTP lorsqu'un jeton valide est absent.
   - **`juris`** (`https://jurisprudence.poirierlavoie.ca/mcp`) : authentification par secret partagé (`Authorization: Bearer`) en comparaison à temps constant SHA-256 ; réponse **HTTP 401** (`WWW-Authenticate: Bearer`) sans jeton valide.
   - **`outils`** (`https://outils.poirierlavoie.ca/mcp`) : serveur public en lecture seule sur données officielles et calculs déterministes ; aucun secret ni aucun jeton client requis.
3. **Protection du transport et des entrées :** validation stricte des schémas JSON (`additionalProperties: false`), limitation de la taille des requêtes HTTP (`> 64 Kio` -> `413 Payload Too Large`), liste blanche d'en-têtes `Host` (protection contre le *DNS rebinding*) et rejet des requêtes JSON-RPC groupées ou à identifiant structuré.

---

## Secret professionnel et posture de journalisation

### Règles impératives des compétences (`SAFETY-KERNEL` v3)

Toutes les compétences du greffon imposent les règles suivantes :

- **Zéro information nominative dans les recherches externes :** ne jamais inclure de noms de parties, faits identifiants, numéros de dossier ou extraits de pièces confidentielles dans une requête web ou de recherche doctrinale.
- **Présomption `CONFIDENTIEL` par défaut :** aucun document ou élément probant non analysé n'est considéré public par défaut ; tout indice de privilège (secret professionnel `9 Charte`, litige, règlement `s.p.`, confidentialité `108 C.p.c.`) est signalé avant toute communication.
- **Dé-identification des précédents internes :** tout précédent tiré d'un autre dossier et fourni par l'avocat doit être dé-identifié sans importer aucun fait, nom ni pièce dans le dossier courant, avec alerte de conflit le cas échéant.

### Journalisation côté serveurs MCP et scripts locaux

- **`MCP-Outils` (`outils`) :** exécution **entièrement sans état ni journalisation applicative** des requêtes clients (aucune conservation des calculs `calendrier_deadlines`, `interets_1619`, `greffe_parse_number`, `registre_search`, `adresse_verify` ou `terminologie_scan`).
- **`MCP-Legislation` (`lois`) et `MCP-Jurisprudence` (`juris`) :** ces Workers Cloudflare utilisent une base D1 avec une table de télémétrie technique (`search_log`) enregistrant des empreintes de requêtes de recherche (`find_relevant`, `search_text`, `find_case`) à des fins de diagnostic et de pertinence. **En conséquence, ne jamais soumettre d'éléments nominatifs, identifiants client ou faits confidentiels dans les paramètres de recherche libre `query`.**
- **Scripts locaux Python :** `skills/analyse-et-strategie/scripts/inspecter_piece.py`, `skills/gestion-du-mandat/scripts/calcul_delai.py`, `skills/production-et-conformite/scripts/controler_document.py` et `skills/production-et-conformite/scripts/verifier_cotes.py` n'utilisent que la bibliothèque standard Python, ne réalisent aucun appel réseau et n'écrivent aucun fichier hors du journal de garde explicitement demandé par `--journal`.
