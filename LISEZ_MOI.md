# Parcours — Hatem Ellouze

Neuf panoramas réalistes, seize passages cliquables et deux axonométries fixes. Le départ est l’accueil.

## Ouvrir la visite immédiatement

Téléchargez `Visite_interactive_Hatem.html` et ouvrez-le dans Chrome ou Edge. Toutes les images sont incluses : ce fichier fonctionne sans serveur ni connexion. Vous pouvez transmettre ce fichier à la cliente.

- Faites glisser avec la souris ou le doigt pour regarder à 360°.
- Cliquez sur les repères ronds pour rejoindre l’espace indiqué.
- « Monter à l’étage » et « Descendre au hall » relient les niveaux.
- « Retour » retrouve le point précédent et son angle de vue.
- « Espaces » ouvre les neuf points ; « Axonométries » ouvre les deux images.
- Molette ou + / − pour zoomer ; « Plein écran » pour agrandir.

Les déplacements se font entre points fixes ; ce n’est pas une marche continue dans la maquette 3D.

## Installer sur GitHub et Streamlit

1. Décompressez l’archive de l’application.
2. Placez tout le contenu du dossier `Parcours_Hatem_360` dans votre dépôt GitHub, y compris le dossier `data/` et `.streamlit/config.toml`.
3. Dans Streamlit Community Cloud, déployez ce dépôt avec `app.py` comme fichier principal.
4. Dans les secrets de l’application, définissez votre propre mot de passe d’au moins douze caractères :

```toml
ADMIN_PASSWORD = "votre-mot-de-passe-personnel"
```

Ne mettez pas ce mot de passe dans GitHub. Il n’y a aucun mot de passe par défaut. L’administration reste fermée tant que le secret n’est pas configuré.

5. Transmettez l’URL Streamlit à la cliente. La visite se consulte sans mot de passe ; les modifications exigent une connexion administrateur.

Pour lancer sur votre ordinateur :

```bash
pip install -r requirements.txt
streamlit run app.py
```

En local, placez le secret dans `.streamlit/secrets.toml` (exclu par `.gitignore`).

## Administrer le projet

Dans la barre latérale, ouvrez « Administration » et connectez-vous.

- **Panoramas** : remplacer une image, renommer un point, choisir le départ ou ajouter un panorama équirectangulaire 2:1.
- **Passages** : choisir la scène de départ, centrer l’aperçu sur le passage, copier les coordonnées affichées, choisir la destination puis enregistrer. Ajouter aussi le passage de retour depuis l’autre scène.
- **Axonométries** : ajouter des images fixes.
- **Sources SketchUp** : conserver un fichier SKP et/ou DAE. L’import conserve la source ; il ne génère pas automatiquement de rendu.
- **Exporter** : télécharger le HTML autonome actualisé et une sauvegarde du dossier `data/`.

Après chaque modification, téléchargez la sauvegarde et remplacez le dossier `data/` dans GitHub. Le disque de Streamlit Cloud est temporaire : les modifications non sauvegardées peuvent disparaître lors d’un redémarrage. Un stockage permanent distant n’est pas configuré dans cette version.

La génération IA n’est pas intégrée au serveur : les panoramas sont préparés puis importés. Les visiteurs n’ont aucun contrôle d’import ou d’édition.

## Vérifications et limites

Les bases ont été calculées depuis les caméras intérieures du DAE puis retouchées avec les références fournies. Le hall validé est réutilisé. La retouche IA peut introduire de petits écarts de géométrie ou de mobilier entre les vues ; ces images ne remplacent pas la maquette ou les plans d’exécution.

Contrôles effectués : décodage et format des images, accès aux neuf scènes, seize liens aller-retour, logique JavaScript de chargement/navigation/retour et projection des repères, compilation Python. Les interactions n’ont pas été testées dans un navigateur réel dans cet environnement. Ouvrez la visite sur l’appareil prévu avant la présentation cliente.

Pour réexporter depuis les sources :

```bash
python pack.py Visite_interactive_Hatem.html
```

Le HTML ne contient ni sources SketchUp ni mot de passe administrateur.

## Mise à jour du 19 octobre

Le raccord de plafond signalé au-dessus de la cuisine a été retouché. Le bouton « Rendu détaillé » de chaque scène ouvre le rendu de référence fourni, en image fixe, avec affichage à taille réelle. Cela permet de consulter davantage de détails sur un angle donné, sans modifier la navigation 360°.

Les panoramas restent en 1774 × 887 pixels : la retouche n’a pas fourni de résolution native supérieure. Le flou au fort zoom 360° n’est donc pas résolu. Les vues détaillées ne sont pas de nouveaux panoramas haute résolution.

Pour installer la mise à jour, remplacer app.py, pack.py, viewer.html et le dossier data/ complet dans le dépôt. Les secrets administrateur restent dans Streamlit.
