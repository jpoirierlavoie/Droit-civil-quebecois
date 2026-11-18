# Politique de sécurité et de confidentialité (`SECURITY.md`)

## Signalement d'une vulnérabilité ou d'un incident de confidentialité

**Ne jamais ouvrir d'issue GitHub publique** pour signaler une faille de sécurité, une fuite de secret ou un enjeu touchant le secret professionnel.

- **Canal privé prioritaire :** [Avis de sécurité privé GitHub](https://github.com/jpoirierlavoie/droit-civil-quebecois/security/advisories/new)
- **Courriel de contact :** `jason@poirierlavoie.ca`
- **Délai d'accusé de réception :** dans les **72 heures**.

### Portée

Cette politique couvre le greffon **`droit-civil-quebecois`** (`v2.1.0`) ainsi que les dépôts d'infrastructure associés : [`MCP-Acces`](https://github.com/jpoirierlavoie/MCP-Acces) (`acces.poirierlavoie.ca`), [`MCP-Legislation`](https://github.com/jpoirierlavoie/MCP-Legislation), [`MCP-Jurisprudence`](https://github.com/jpoirierlavoie/MCP-Jurisprudence), [`MCP-Outils`](https://github.com/jpoirierlavoie/MCP-Outils) et [`MCP-Socle`](https://github.com/jpoirierlavoie/MCP-Socle).

---

## Secrets, authentification à double montage et BYOK CanLII

1. **Aucune donnée d'authentification dans le dépôt :** `.mcp.json`, `mcp_config.json` et `gemini-extension.json` référencent uniquement les variables d'environnement `${MCP_LEGISLATION_SECRET}` et `${MCP_JURISPRUDENCE_SECRET}` (marquées `sensitive: true` dans `gemini-extension.json`). Les jetons individuels CSPRNG de 256 bits (`43` car. `base64url`, émis sur `acces.poirierlavoie.ca/moi`) sont affichés une seule fois et stockés uniquement par empreinte `SHA-256` dans la base partagée `DB_IDENTITE` (`mcp-identite`).
2. **Isolation et double montage des serveurs MCP :**
   - **`lois`** (`https://legislation.poirierlavoie.ca/mcp` & `/mcp/oauth`) et **`juris`** (`https://jurisprudence.poirierlavoie.ca/mcp` & `/mcp/oauth`) :
     - **Montage direct `/mcp`** (`Claude Code`, `Claude Desktop`, `Antigravity`, `Gemini CLI`, `claude.ai` `?key=`, `Gemini API Deep Research`) : comparaison `SHA-256` à temps constant et refus **uniformément en HTTP `404` à corps vide sans en-tête `WWW-Authenticate`** avant même la vérification de méthode HTTP (`G7`, `G23`).
     - **Montage OAuth 2.1 `/mcp/oauth`** (`gemini.google.com`, Vertex AI Gemini Enterprise, connecteurs OAuth `claude.ai`) : code d'autorisation **PKCE `S256` obligatoire**, découverte RFC 9728 sur `/.well-known/oauth-protected-resource/mcp/oauth` (la racine `/.well-known/oauth-protected-resource` demeure en `404`), rejet `401` avec `WWW-Authenticate` pointant vers `https://acces.poirierlavoie.ca`.
   - **`juris` — Clé API CanLII personnelle obligatoire (BYOK strict, `G8`, `G10`, `G38`) :** réservé aux membres en règle du Barreau du Québec. La clé API CanLII de chaque praticien est vérifiée en direct à l'admission (`/demande`) puis scellée par chiffrement d'enveloppe (`HKDF-SHA256` + `AES-256-GCM`) dans `DB_IDENTITE.coffre_clef` (ou transmise ponctuellement via l'en-tête `X-Clef-CanLII`). Aucune retombée sur la clé opérateur n'existe pour les comptes titulaires, et le contrôle BYOK bloque même la lecture du cache D1 partagé lorsqu'aucune clé active n'est présente (`[CLEF_ABSENTE]` / `[CLEF_REFUSEE]`). Aucun horodatage exact `fetched_at` n'est exposé dans la prose rendue (`G38`).
   - **`outils`** (`https://outils.poirierlavoie.ca/mcp`) : serveur public en lecture seule sur données officielles et calculs déterministes ; aucun secret ni jeton requis (`RATE_LIMITER` 60 req/60 s/IP).
3. **Protection du transport et gouvernance contre les rafales :** validation stricte des schémas JSON (`additionalProperties: false`), limite de corps HTTP (`> 64 Kio` -> `413`), liste blanche `Host` et `Origin` (anti-*DNS rebinding*), limitation pré-authentification par IP avec laissez-passer sur empreintes actives et quarantaine d'échecs isolée (`G32`), limitation post-authentification par `titulaire_id` (`300/min` `lois`, `180/min` `juris`) et quotas journaliers UTC (`1 500` `local`, `200` `sortant`, `150` `semantique`).

---

## Secret professionnel, zéro-journalisation et Deep Research

### Règles impératives des compétences (`SAFETY-KERNEL`)

Toutes les compétences du greffon imposent les règles suivantes :

- **Zéro information nominative dans les recherches externes :** ne jamais inclure de noms de parties, faits identifiants, numéros de dossier ou extraits de pièces confidentielles dans une requête web ni dans un champ de recherche libre `query` (`lois.find_relevant`, `lois.search_text`).
- **Présomption `CONFIDENTIEL` par défaut :** aucun document ou élément probant non analysé n'est considéré public par défaut ; tout indice de privilège (secret professionnel `9 Charte`, litige, règlement `s.p.`, confidentialité `108 C.p.c.`) est signalé avant toute communication.

### Posture zéro-journalisation côté serveurs MCP et option locale `hybride_permis`

- **Journaux d'invocation Cloudflare désactivés (`G37`) :** `observability.enabled = false` et `observability.logs.invocation_logs = false` sur `MCP-Legislation`, `MCP-Jurisprudence`, `MCP-Acces` et `MCP-Outils`. Aucun Worker n'écrit de texte de requête, citation, argument d'outil ni `request.url` (protégeant notamment `?key=`) dans `console.*` (`G9`).
- **Zéro écriture de requêtes dans D1 (`S13`, `S14`, `G13`) :** `MCP-Outils` est strictement sans écriture (`PRAGMA query_only = ON`) ; `MCP-Legislation` et `MCP-Jurisprudence` ont retiré toute écriture d'exécution dans `search_log` et `api_usage`, ne conservant dans `DB_IDENTITE` que des compteurs journaliers agrégés (`compteur_jour`) et des événements techniques à énumération fermée horodatés à la minute (`evenement_technique`, purgés automatiquement à 90 jours).
- **Désactivation libre-service de Workers AI (`hybride_permis`, `S19`) :** chaque titulaire peut désactiver le repérage sémantique dans `https://acces.poirierlavoie.ca/moi` ; `lois.search_text` reste alors strictement cantonné à l'index lexical FTS5 local sur D1.
- **Prudence particulière en mode Deep Research :** les boucles autonomes (`claude.ai` Research et `gemini-api` `deep-research-preview-04-2026`, dont l'exécution en arrière-plan impose `store=True`) effectuent des recherches web ouvertes et conservent la transcription côté fournisseur. **Ne soumettre exclusivement que des questions juridiques abstraites et anonymisées**, idéalement préfixées du préambule `SAFETY-KERNEL`, sous compte d'entreprise couvert par une entente de traitement de données.
- **Scripts locaux Python :** `skills/analyse-juridique/scripts/inspecter_piece.py` et `skills/administration-litige/scripts/calcul_delai.py` n'utilisent que la bibliothèque standard Python, ne réalisent aucun appel réseau et n'écrivent aucun fichier hors du flux standard choisi par l'utilisateur.
