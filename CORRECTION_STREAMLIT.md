# Correction de l’erreur MessageSizeError

Cette version ne transmet plus toutes les images en base64 dans un seul message Streamlit.
Les images HD sont accessibles séparément via `/app/static/data/...`, grâce à `enableStaticServing = true`.

Démarrer avec :

```bash
pip install -r requirements.txt
streamlit run app.py
```

Pour Streamlit Community Cloud, déployez **tout le dossier** avec `.streamlit/config.toml` et `static/data/`.
La résolution des panoramas n’a pas été réduite. L’upscaling antérieur ne crée cependant pas de détails photographiques nouveaux.

Le mode export HTML autonome reste disponible depuis l’administration ; ce fichier peut être très lourd car il embarque les images.
