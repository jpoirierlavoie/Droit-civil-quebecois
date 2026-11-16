# Force probante, recevabilité, privilèges et caviardage

Évalue ce qu'une pièce prouve en droit civil québécois, ce qui limite sa recevabilité et qui peut la voir. **Lire les textes via `lois.get_articles` avant toute conclusion formelle.**

## 1. Vecteurs `lois.get_articles` à charger au Palier 2–3

* **Preuve & intégrité technologique :**
  * `law="ccq"` : `numbers=["2803", "2804", "2811", "2813", "2814", "2818", "2819", "2821", "2822", "2826", "2828", "2831", "2832", "2833", "2835", "2837", "2838", "2839", "2840", "2843", "2850", "2852", "2854", "2855", "2857", "2858", "2860", "2862", "2863", "2864", "2865", "2869", "2870"]`
  * `law="c-1.1"` (LCJTI) : `numbers=["5", "7", "12", "16"]`
  * `law="cpc"` : `numbers=["246", "248", "250", "251", "262", "292", "293"]`
* **Protection, accès et confidentialité :**
  * `law="cpc"` : `numbers=["4", "11", "12", "16", "108", "163", "606"]`
  * `law="c-12"` (`9`), `law="b-1"` (`131`), `law="c-26"` (`60.4`), `law="p-39.1"` (Loi 25, selon l'élément nominatif repéré).

## 2. Grille de force probante et recevabilité (`C.c.Q.`)

Un acte de procédure allègue et **ne prouve rien**. Pour toute pièce probatoire, analyser dans cet ordre :
1. **Moyen de preuve (`2811`) :** Écrit, témoignage (y compris déclaration écrite `292 C.p.c.` ou `2869–2870`), présomption, aveu (`2852` judiciaire vs extrajudiciaire apprécié), élément matériel (`2854–2855` photo/enregistrement exigeant preuve distincte d'authenticité sauf `art. 5 al. 3` LCJTI).
2. **Qualification de l'écrit :**
   * *Acte authentique / notarié (`2813–2821`)* : fait preuve à l'égard de tous des faits que l'officier avait mission de constater (vérifier si extrait certifié officiel REQ/Registre foncier/RDPRM ou simple impression d'écran).
   * *Acte sous seing privé (`2826–2829`)* : opposé au signataire apparent, **tenu pour reconnu** s'il n'est pas contesté par déclaration sous serment avant l'inscription (`262 C.p.c.`).
   * *Écrit d'entreprise non signé (`2831`)* : doit être **habituellement utilisé dans le cours des activités** (distinguer une comptabilité courante d'un chiffrier reconstitué pour le litige).
   * *Autre écrit (`2832`)* / *Papier domestique (`2833`)* : un écrit non signé (courriel, capture) impose à celui qui l'invoque d'en prouver l'auteur (`2835`).
3. **Obstacles de recevabilité à vérifier :**
   * *Original / copie (`2860`; LCJTI `12, 16`)* : demander où est l'original si seule une copie circule.
   * *Intégrité technologique (`2838–2840`; LCJTI `7`)* : dispensée de preuve sauf preuve d'altération (relever capture recadrée, fil tronqué, horodatage incohérent).
   * *Preuve testimoniale d'un acte juridique (`2862`) vs contradiction d'un écrit (`2863–2865`)* : la preuve testimoniale d'un acte juridique est plafonnée à `1 500 $`, sauf commencement de preuve (`2865`) ou à l'égard d'un acte fait dans le cours des activités d'une entreprise (`2862 al. 2`); indépendamment de la valeur en litige, le témoignage ne peut jamais contredire ou changer les termes d'un écrit constatant un acte juridique (`2863`, sous réserve de l'interprétation sous `2864` ou du commencement de preuve sous `2865`).
   * *Ouï-dire (`2843, 2869–2870`)* : une lettre ou un rapport relatant les dires d'un tiers ne prouve pas leur véracité sans consentement ou autorisation avec garanties sérieuses.
   * *Preuve obtenue illégalement (`2858`)* : rejet d'office si atteinte aux droits fondamentaux + déconsidération (et rejet **sans** critère de déconsidération en cas de violation du secret professionnel).
4. **Conclusion en 2 points :** Ce que la pièce **prouve** vs ce qu'elle **ne prouve pas** + `Statut du fait` (`Établi`, `Rapporté`, `Déduit`, `[À CONFIRMER]`).

## 3. Régime de protection asymétrique et caviardage

**Asymétrie :** Sous-estimer une protection risque une divulgation fautive; la surestimer ne coûte que du temps. **L'absence de marque de confidentialité ne rend jamais un document `PUBLIC`.** En cas de doute, cumuler les régimes et retenir le plus élevé :

| Niveau | Régimes | Exemples d'indices positifs (jamais d'absence) |
|---|---|---|
| **3 (Max)** | **Secret professionnel** (`c-12` 9; `b-1` 131; `c-26` 60.4; `2858 al. 2`) | En-tête d'avocat, avis juridique au client, relation avocat-client |
| **2** | **Privilège relatif au litige** (*Blank*, *Lizotte*) / **Règlement** (`cpc` 4, 163, 606) / **Enquête interne** | Projet annoté, notes de stratégie, échange avec expert non communiqué, offre chiffrée, *without prejudice*, *sous toutes réserves* transactionnel |
| **1** | **Secret commercial** / **Confidentiel (défaut résiduel)** | Procédés, listes de prix (`art. 12 C.p.c.` nécessaire — ne confère pas d'immunité de production), correspondance externe ordinaire, tout document non coté |
| **0** | **Public** (`cpc` 11, sous réserve de `12` et `16`) | **Uniquement** si cote (`P-1`, `D-2`), timbre de greffe ou preuve de dépôt/notification au dossier (sans restriction `12`/`16 C.p.c.`) |

**Trois alertes systématiques :**
* **Renonciation / intérêt commun :** Si un document coté `P-n` porte des marques de secret ou de règlement, signaler le risque de renonciation (ou la préservation par intérêt juridique commun entre co-défendeurs/assureur).
* **Mention apposée par routine :** Un tampon « privilégié » sur une facture ou lettre banale ne crée pas le secret; le signaler.
* **Caviardage / pli cacheté requis (`art. 108, 12, 16 C.p.c.`; Loi 25 `p-39.1`) :** Signaler avant toute communication/dépôt : NAS, compte bancaire/carte de crédit, dossier médical/psychosocial, identité de mineur ou victime (`16 C.p.c.`), secret commercial critique (`12 C.p.c.`).
