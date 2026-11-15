# Security, Privacy & Professional Secrecy Policy / Politique de sécurité, confidentialité et secret professionnel

> **Français :** Pour signaler une **vulnérabilité de sécurité** OU un **enjeu de confidentialité, de vie privée ou de secret professionnel** (privilège avocat-client / privilège relatif au litige), **n'ouvrez jamais d'issue publique ni de discussion sur GitHub**. Écrivez directement au mainteneur :
> **Jason Poirier Lavoie, avocat (Québec)** — `jason@poirierlavoie.ca` (accusé de réception sous **72 heures**, divulgation coordonnée).
> **Ne joignez jamais** de dossiers clients réels, de pièces protégées par le secret professionnel, de renseignements nominatifs confidentiels ni de jetons/secrets actifs à un premier envoi ; utilisez des exemples fictifs ou anonymisés.
>
> **English:** To report a **security vulnerability** OR a **privacy, confidentiality, or legal privilege / professional secrecy issue**, **do not open a public GitHub issue or pull request**. Email the maintainer privately:
> **Jason Poirier Lavoie, Lawyer (Québec)** — `jason@poirierlavoie.ca` (acknowledgement within **72 hours**, coordinated disclosure).
> **Never include** live client files, privileged communications, unredacted identifying facts, or active bearer tokens/secrets in an initial report; use synthetic or anonymized examples first.

---

## Portée du dépôt (`pratique-civile-quebecoise`)

Ce dépôt héberge le greffon multiplateforme **Pratique civile québécoise** (Claude Code, Claude Desktop, claude.ai, Google Antigravity, Gemini CLI) :
- Les cinq compétences juridiques sous `skills/` (`recherche-juridique`, `redaction-juridique`, `analyse-documentaire`, `calendrier-procedural`, `deontologie-professionnelle`) et l'outillage local (`skills/calendrier-procedural/scripts/calcul_delai.py`) ;
- Les manifestes clients (`.mcp.json`, `mcp_config.json`, `gemini-extension.json`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `plugin.json`) ;
- Les scripts de vérification et d'évaluation (`verifier.py`, `verifier_tout.py`, `evals/`).

### Hors portée
- Attaque volumétrique (DoS) sur les services d'hébergement tiers, ingénierie sociale, ou vulnérabilités propres aux plateformes clientes hôtes (Anthropic, Google, GitHub, Cloudflare).
- Pour un incident visant spécifiquement un serveur MCP, vous pouvez également consulter la politique propre du dépôt concerné (`MCP-Legislation`, `MCP-Jurisprudence`, `pratique-civile-outils`, `MCP-Socle-Juridique`) — tous convergent vers la même adresse de contact confidentielle (`jason@poirierlavoie.ca`).

---

## Signalement d'un enjeu de sécurité, de vie privée ou de secret professionnel

Merci de préciser, sans exposer de données confidentielles réelles :
1. **Nature du signalement** : faille technique (manifeste, script Python, contournement d'isolation, injection) **ou** exposition / fuite potentielle de renseignements confidentiels, personnels ou couverts par le secret professionnel (`art. 9` *Charte des droits et libertés de la personne*, `art. 131` *Loi sur le Barreau*).
2. **Composant concerné** : compétence (`SKILL.md` / `references/`), script, manifeste ou flux vers un connecteur MCP.
3. **Scénario minimal de reproduction** (avec données fictives) et **impact potentiel**.
4. **Correctif ou mesure d'atténuation suggérée**, le cas échéant.

---

## Posture de confidentialité, de journalisation et de secret professionnel des connecteurs déclarés

Ce greffon est conçu pour garder le contrôle du dossier chez l'avocat tout en limitant ce qui sort vers les outils MCP externes :

1. **Isolation du gestionnaire de dossiers** : les compétences emploient un contrat d'information abstrait en 12 besoins et ne dépendent d'aucun logiciel de gestion de dossiers. Les documents du dossier sont classés selon quatre niveaux de protection (`0` à `3`, dont le secret professionnel et le privilège relatif au litige) dans `analyse-documentaire`.
2. **Responsabilité de l'environnement hôte** : les faits d'un client confiés au modèle d'IA hôte demeurent soumis aux garanties contractuelles (DPA / absence d'entraînement) configurées par le cabinet auprès du fournisseur d'IA. Les compétences demandent à l'utilisateur ou rappellent l'obligation déontologique (`deontologie-professionnelle`) avant de transmettre des éléments nominatifs vers l'extérieur.
3. **Flux vers les trois connecteurs MCP distants** :
   - **`MCP-Legislation`** (`https://legislation.poirierlavoie.ca/mcp`) : protégé par secret partagé (`Bearer ${MCP_LEGISLATION_SECRET}`). En lecture seule sur les lois du Québec et du Canada. La table D1 `search_log` enregistre les chaînes de recherche en texte clair (sans identifiant d'auteur, mais sans purge automatique) : formuler des requêtes juridiques abstraites, sans nom de client ni faits identifiants ; côté client applicatif, privilégier l'en-tête `Authorization: Bearer` (évite l'exposition du secret dans les journaux d'URL `?key=`).
   - **`MCP-Jurisprudence`** (`https://jurisprudence.poirierlavoie.ca/mcp`) : protégé par secret partagé (`Bearer ${MCP_JURISPRUDENCE_SECRET}`). L'outil `jurisprudence_parse_citation` fonctionne entièrement hors ligne (`openWorldHint: false`). Les neuf autres outils interrogent l'API REST de CanLII (`openWorldHint: true`) et alimentent une table D1 `search_log` : rechercher par `jurisprudence_find_case` le nom d'une partie à un dossier actif (non encore publié) révèle cet intérêt de recherche à CanLII et inscrit ce nom dans `search_log`.
   - **`pratique-civile-outils`** (`https://outils.poirierlavoie.ca/mcp`) : public, sans état, sans base de données ni journalisation applicative (`observability.enabled = false`, `logs.enabled = false`), zéro appel sortant (`openWorldHint: false`). Néanmoins, par prudence déontologique, éviter d'inscrire des noms de clients ou numéros de dossiers confidentiels dans les libellés libres (`label`) envoyés à `calendrier_compute_deadlines` ou `interets_compute_1619`.
4. **Protection des secrets dans le dépôt** : `.mcp.json`, `mcp_config.json` et `gemini-extension.json` n'emploient que des références de variables d'environnement (`${MCP_LEGISLATION_SECRET}`, `${MCP_JURISPRUDENCE_SECRET}`), marquées `sensitive: true` sous Gemini CLI, sans chargement par défaut de `GEMINI.md` dans les sessions utilisatrices (`"contextFileName": []`). `verifier.py` rejette toute chaîne hexadécimale suspecte (`≥ 32` caractères).
