# Correctif de chargement des panoramas

La visite intègre ses images WebP directement dans le HTML de l’iframe. Cette méthode évite les URL `/app/static/` qui pouvaient être inaccessibles dans l’iframe Streamlit et réduit l’envoi bien en dessous de 200 Mo.

Les neuf panoramas restent en 4096 × 2048 pixels. Les rendus détaillés et axonométries sont inclus. Les mêmes scènes, repères et boutons sont conservés. La compression WebP peut légèrement modifier les pixels, mais ne crée pas de nouveaux détails à partir des images agrandies.

Installation : publier l’intégralité du contenu de ce dossier à la racine du dépôt GitHub de l’application, puis redémarrer Streamlit. Le contenu du dossier `static/data/` est indispensable.
