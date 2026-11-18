# Privilèges, confidentialité et caviardage (régime asymétrique)

Évalue qui peut voir une pièce, quel régime de protection s'applique et quels renseignements doivent être caviardés ou déposés sous pli cacheté avant toute communication. **Lire les textes via `lois.get_articles` avant toute conclusion formelle.**

## Qualification

Vecteurs à charger via `lois.get_articles` :
* `law="cpc"` : `numbers=["4", "11", "12", "16", "108", "163", "606"]`.
* `law="c-12"` (`9`), `law="b-1"` (`131`), `law="c-26"` (`60.4`), `law="ccq"` (`2858 al. 2`), `law="p-39.1"` (Loi 25, selon l'élément nominatif repéré).

**Principe d'asymétrie :** Sous-estimer une protection risque une divulgation fautive; la surestimer ne coûte que du temps. **L'absence de marque de confidentialité ne rend jamais un document `PUBLIC`.** En cas de doute, cumuler les régimes et retenir le plus élevé :

| Niveau | Régimes | Exemples d'indices positifs (jamais d'absence) |
|---|---|---|
| **3 (Max)** | **Secret professionnel** (`c-12` 9; `b-1` 131; `c-26` 60.4; `2858 al. 2`) | En-tête d'avocat, avis juridique au client, relation avocat-client |
| **2** | **Privilège relatif au litige** (*Blank*, *Lizotte*) / **Règlement** (`cpc` 4, 163, 606) / **Enquête interne** | Projet annoté, notes de stratégie, échange avec expert non communiqué, offre chiffrée, *without prejudice*, *sous toutes réserves* transactionnel |
| **1** | **Secret commercial** / **Confidentiel (défaut résiduel)** | Procédés, listes de prix (`art. 12 C.p.c.` nécessaire — ne confère pas d'immunité de production), correspondance externe ordinaire, tout document non coté |
| **0** | **Public** (`cpc` 11, sous réserve de `12` et `16`) | **Uniquement** si cote (`P-1`, `D-2`), timbre de greffe ou preuve de dépôt/notification au dossier (sans restriction `12`/`16 C.p.c.`) |

## Authentification et intégrité

Exécuter `scripts/inspecter_piece.py` sur les fichiers locaux afin de révéler les commentaires Word (`COMMENTAIRES_WORD`), marques de révision (`MARQUES_DE_REVISION`), `Bcc` (`COPIE_CONFORME_INVISIBLE`) ou brouillons (`BROUILLON_PROBABLE`) susceptibles d'exposer des avis internes ou privilégiés.

## Recevabilité

* **Secret professionnel (`2858 al. 2 C.c.Q.`) :** Tout élément de preuve obtenu en violation du secret professionnel est rejeté **d'office sans critère de déconsidération**.
* **Privilège de règlement (`cpc` 4, 163, 606) :** Les offres, concessions et pourparlers en vue d'un règlement ne sont pas recevables en preuve au fond (sauf exceptions reconnues comme l'existence même d'une transaction).

## Force probante

L'étiquette juridique d'une protection dépend de la substance et du contexte de création du document, non d'une simple mention apposée mécaniquement :
* **Renonciation / intérêt commun :** Si un document coté `P-n` porte des marques de secret ou de règlement, signaler le risque de renonciation (ou la préservation par intérêt juridique commun entre co-défendeurs/assureur).
* **Mention apposée par routine :** Un tampon « privilégié » sur une facture ou lettre banale ne crée pas le secret; le signaler.

## Protection

**Caviardage / pli cacheté requis (`art. 108, 12, 16 C.p.c.`; Loi 25 `p-39.1`) :** Signaler obligatoirement avant toute communication ou dépôt :
* numéro d'assurance sociale (NAS), numéro de compte bancaire ou carte de crédit;
* dossier médical ou psychosocial;
* identité de mineur ou victime (`16 C.p.c.`);
* secret commercial critique nécessitant une ordonnance de confidentialité (`12 C.p.c.`).

## Ce que la pièce ne prouve pas

* Une mention « confidentiel » ou « privilégié » ne prouve pas à elle seule l'existence d'un privilège opposable au tribunal.
* L'absence de mention de confidentialité sur un courriel ou fichier `.docx` ne prouve jamais qu'il est public ni communicable sans caviardage.
