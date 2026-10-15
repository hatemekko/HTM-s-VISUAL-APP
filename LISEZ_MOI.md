# Parcours — visite architecturale de Hatem Ellouze

Application Python / Streamlit avec visualiseur Three.js. Le projet de bureaux et ses 11 rendus sont préchargés. Aucun abonnement ou appel à une IA n’est nécessaire.

## Ce qui fonctionne

- Exploration de la maquette : rotation, zoom et déplacement.
- Sélection des 12 caméras exportées de SketchUp.
- Galerie plein écran et navigation précédent/suivant au clavier ou avec les boutons.
- Points dorés dans la 3D quand une image a été associée à une caméra.
- Espace administrateur protégé côté serveur : titres, imports, ordre des rendus et associations.
- Export ZIP de toutes les données, stockage S3 facultatif pour conservation durable.

Les rendus sont des images fixes, pas des panoramas. La 3D est une maquette de repérage simplifiée, sans éclairage photoréaliste. Les 61 textures externes du DAE initial n’ont pas été fournies. L’import DAE produit une maquette monochrome optimisée (jusqu’à environ 650 000 triangles). Pour conserver vos matériaux et détails, fournissez un GLB optimisé. Des petits détails peuvent disparaître lors de la simplification.

**Les 11 images ne sont pas automatiquement affectées aux 12 caméras : cette correspondance doit être validée dans l’administration.** La galerie et les caméras fonctionnent déjà séparément. Les vues axonométriques peuvent rester en galerie sans point associé.

## 1. Essayer sur votre ordinateur Windows

Installer Python 3.11 ou 3.12. Décompresser l’archive, ouvrir un terminal dans le dossier contenant `app.py`, puis exécuter :

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
```

Créer le fichier `.streamlit/secrets.toml` à côté de `config.toml` :

```toml
ADMIN_PASSWORD = "REMPLACEZ_PAR_VOTRE_MOT_DE_PASSE_LONG_ET_UNIQUE"
```

Utiliser un mot de passe d’au moins 12 caractères. La valeur ci-dessus est un exemple à remplacer. Aucun mot de passe n’est intégré au code.

Puis lancer :

```powershell
.venv\Scripts\python -m streamlit run app.py
```

Ouvrir l’adresse affichée dans le terminal, habituellement http://localhost:8501. Une connexion Internet est nécessaire au chargement initial de Three.js depuis jsDelivr. WebGL doit être activé dans le navigateur.

## 2. Préparer le parcours

1. Dans « Visite », choisir une caméra dans le menu « Caméras SketchUp » et observer ce qu’elle montre.
2. Ouvrir « Administration », saisir votre mot de passe.
3. Dans « Rendus et positions », sélectionner une image, puis sa caméra correspondante.
4. Donner un titre clair, définir sa position dans le parcours, enregistrer.
5. Revenir à « Visite » : un point doré permet maintenant d’ouvrir ce rendu dans la maquette.
6. Répéter pour chaque vue. Garder les axonométries en « Non associée » si souhaité.

Les titres actuels viennent des noms de fichiers. Vous pouvez tous les modifier. Une session d’administration expire après 30 minutes. Le bouton « Se déconnecter » ferme l’accès aux imports.

## 3. Importer un autre projet

Dans l’onglet « Maquette », importer :

- **GLB** : recommandé, déjà optimisé, matériaux intégrés.
- **DAE** : conversion automatique côté serveur, couleurs simplifiées, récupération des caméras.
- **ZIP** : un seul DAE ou GLB, éventuellement accompagné des textures dans leur dossier d’origine.

Le `.skp` peut être conservé comme source dans l’administration mais ne sert pas à afficher la visite. Il faut son export DAE ou GLB. L’application ne prétend pas lire directement le format propriétaire SketchUp.

Importer un nouveau modèle retire les anciennes associations caméra/image, sans supprimer les rendus. Remplacer ensuite les images et les associer aux nouvelles caméras. Pour un GLB sans caméras, des points peuvent être saisis manuellement dans l’onglet « Rendus et positions » : coordonnées en mètres, axe vertical Y.

Les gros DAE peuvent demander beaucoup de mémoire et plusieurs minutes. Pour votre DAE de 121 Mo, privilégier une conversion sur ordinateur, puis publier le résultat déjà optimisé. Le modèle fourni dans ce dossier est déjà converti.

## 4. Mettre sur GitHub et Streamlit

1. Créer un dépôt GitHub, de préférence privé si le projet client est confidentiel.
2. Ajouter **le contenu de ce dossier** : app.py, core.py, viewer.html, requirements.txt, data/, .streamlit/config.toml et .gitignore.
3. **Ne jamais ajouter `.streamlit/secrets.toml`**. Le `.gitignore` l’exclut.
4. Sur https://share.streamlit.io, créer une application à partir de ce dépôt, choisir `app.py` comme fichier principal et Python 3.11 ou 3.12.
5. Dans les paramètres avancés / Secrets de Streamlit, ajouter votre `ADMIN_PASSWORD`, comme dans l’exemple précédent.
6. Déployer et partager l’URL de l’application avec le client. Selon les réglages de partage de votre hébergement, le client devra éventuellement être autorisé à accéder à l’application.

Le client voit la visite et peut ouvrir la page de connexion, mais aucun import ni modification n’est accessible sans authentification. Le mot de passe reste côté serveur et n’est jamais envoyé au visualiseur. Ce mot de passe protège la modification, pas la confidentialité des images présentées aux visiteurs autorisés.

## 5. Conserver les changements

### Sur votre ordinateur

Les changements sont enregistrés dans `data/`. Téléchargez régulièrement une sauvegarde depuis l’administration.

### Sur Streamlit Cloud — sans stockage supplémentaire

Les imports modifient les fichiers du serveur, **pas ceux de GitHub**. Ils peuvent être perdus lors d’un redémarrage ou redéploiement. Après chaque modification :

1. Administration → Sauvegarde → Préparer la sauvegarde complète.
2. Télécharger `projet_visite.zip`.
3. Décompresser son contenu dans `data/` du dépôt GitHub et enregistrer les modifications.

La sauvegarde contient le modèle, les images et leurs associations, mais pas le mot de passe. Le bouton de téléchargement correspond au dernier clic sur « Préparer » : recliquer après de nouveaux changements.

### Stockage automatique durable S3 / Cloudflare R2

Créer un bucket privé et des identifiants limités à ce bucket. Ajouter dans les secrets Streamlit :

```toml
S3_ENDPOINT = "https://VOTRE_ENDPOINT_COMPATIBLE_S3"
S3_BUCKET = "votre-bucket"
S3_ACCESS_KEY = "votre-cle"
S3_SECRET_KEY = "votre-secret"
S3_REGION = "auto"
S3_KEY = "parcours/project.zip"
```

Pour Amazon S3, omettre S3_ENDPOINT et renseigner la région AWS. Les sauvegardes sont privées et lues par le serveur. L’application écrit une sauvegarde complète après chaque enregistrement, puis restaure cette sauvegarde au démarrage. Le premier enregistrement crée l’objet distant. Si la sauvegarde distante échoue, un message explicite s’affiche : exporter une sauvegarde manuelle.

Cette version est prévue pour une seule instance Streamlit et un administrateur. Elle ne gère pas les éditions concurrentes entre plusieurs serveurs. Le délai après erreur de mot de passe est par session ; utiliser un mot de passe long et unique, et une protection d’hébergement supplémentaire si nécessaire.

## Vérifications et limites

La structure DAE et ses caméras ont été lues, le modèle converti et les chemins administrateur/visiteur testés avec Streamlit AppTest. La syntaxe du JavaScript a été vérifiée. Le rendu WebGL n’a pas été testé dans un navigateur graphique ici : vérifier la visite sur votre ordinateur avant de transmettre le lien au client.

L’application n’est pas encore publiée dans votre compte GitHub ou Streamlit. L’archive contient le code exécutable et les données nécessaires au déploiement.
