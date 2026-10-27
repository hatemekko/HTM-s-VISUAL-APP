# Consignes de retouche V2 — par scène

Pour chaque scène : panorama SketchUp actuel en base (géométrie), référence ci‑dessous pour les matériaux et le mobilier, **Hall (Atrium_chaleureux)** pour la cohérence de palette.

## Consigne commune
Panorama équirectangulaire 2:1 complet, raccord gauche/droite parfait. Sortie la plus grande possible (visez 4096 × 2048 ; si l'outil sort moins, voir « Résolution » plus bas). Ne rien déplacer : murs, portes, vitrages, escaliers, plafonds identiques. Pierre beige polie avec reflets nets, chêne clair, murs blancs chauds, cadres noirs mats, éclairage indirect chaud en gorge, spots encastrés. Pas de blancs brûlés, textures fines (veinage du chêne, grain de la pierre, trame des tissus), ombres de contact. Aucun texte, aucun logo, distorsion sphérique conservée aux pôles.

## Scènes
| Scène | Référence | À reprendre précisément |
|---|---|---|
| Accueil | `Gemini_Generated_Image…jpeg` | Banque blanche avec liseré LED, 2 suspensions rondes en rotin, écrans, bureaux vitrés à cadres noirs, rails noirs à spots au plafond, olivier en vase |
| Salon | `Salon_contemporain…` | 3 œuvres abstraites beige/brun/noir (cadres chêne), appliques linéaires, canapé modulaire lin gris‑beige, pouf rond, fauteuil taupe, suspensions en gélule, tapis chiné |
| Cuisine | `Intérieur_moderne…cuisine_ouverte` | Kitchenette gris béton, frigo américain inox, crédence chêne, suspensions cuivre, chaises blanches pieds bois, vases blancs et vert sauge, rail noir |
| Couloir RDC | `Couloir_de_bureau_moderne_vitré` | Salle de réunion vitrée (table chêne, sièges résille noirs, écran de projection), consoles en pierre avec vase, appliques, olivier, portes chêne, moquette dans les bureaux |
| Hall (reprographie) | `Hall_moderne_avec_escalier_flottant` | Marches noyer sur limon inox, main courante inox, colonne chêne, traceur, fenêtre avec vue, placard chêne à poignées noires |
| Pied de l'escalier | `Hall_moderne_avec_escalier_suspendu` | Marches noyer épaisses, balustrade inox, coin café + photocopieur, grand placard chêne, couloir vitré en fuite |
| Palier | `Couloir_moderne_et_chandelier_sculptural` | Lustre sculptural noir/cuivre, garde‑corps métal gris, bureau meublé derrière le vitrage, baie avec paysage, plafond à pan coupé |
| Café étage | `Couloir_de_bureau_avec_espace_café` | Portes chêne, bureau meublé derrière le vitrage (ordinateur, siège noir), machine à café, photocopieur, traceur, plafond à pan coupé éclairé |

## Résolution (cause du flou au zoom)
Les panoramas font 1774 × 887 : à 72° de champ, l'écran affiche ~5 px par degré, alors que vos références en offrent ~18. Aucun réglage du viewer ne peut recréer ce détail. Pistes, par efficacité :
1. **Upscale ×2 hors outil de génération** (Real‑ESRGAN, Topaz Gigapixel, Magnific) sur chaque PNG, puis re‑export en 3548 × 1774 ou 4096 × 2048.
2. **Rendu direct depuis SketchUp** (V‑Ray, Enscape, D5, Twinmotion) en panorama 360° 4096 × 2048 : c'est la meilleure qualité, et ça garantit la géométrie.
3. Garder « Rendu détaillé » pour les angles clés, avec les références actuelles (maintenant zoomables).

Après remplacement des images dans `data/`, relancer : `python pack.py Visite_interactive_Hatem.html`.
