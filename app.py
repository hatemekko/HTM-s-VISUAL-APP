from pathlib import Path
import os, json, time, hmac, base64, uuid, io, threading
import streamlit as st
import streamlit.components.v1 as components
from PIL import Image
from core import convert_model, snapshot, atomic_write, extract_zip

BASE=Path(__file__).parent
ROOT=Path(os.environ.get('PROJECT_DATA_DIR',str(BASE/'data')))
ROOT.mkdir(parents=True,exist_ok=True)
st.set_page_config(page_title='Parcours · Hatem Ellouze',page_icon='◈',layout='wide')

def secret(k,default=''):
    if os.environ.get(k):return os.environ[k]
    try:return st.secrets.get(k,default)
    except FileNotFoundError:return default

@st.cache_resource
def lock():return threading.RLock()

def s3_client():
    import boto3
    return boto3.client('s3',endpoint_url=secret('S3_ENDPOINT') or None,aws_access_key_id=secret('S3_ACCESS_KEY'),aws_secret_access_key=secret('S3_SECRET_KEY'),region_name=secret('S3_REGION','auto'))

@st.cache_resource
def restore_cloud():
    if secret('S3_BUCKET'):
        from botocore.exceptions import ClientError
        try:
            response=s3_client().get_object(Bucket=secret('S3_BUCKET'),Key=secret('S3_KEY','parcours/project.zip'))
            with lock():extract_zip(response['Body'].read(),ROOT)
        except ClientError as e:
            if e.response['Error']['Code'] not in ('NoSuchKey','404'):raise
    return True

try:restore_cloud()
except Exception:
    st.error('Impossible de lire le stockage distant. Vérifiez sa configuration avant de modifier le projet.');st.stop()

def project():
    p=ROOT/'project.json'
    return json.loads(p.read_text()) if p.exists() else {'title':'Mon projet','subtitle':'Visite architecturale','cameras':[],'views':[]}

def authorized():return time.time()<st.session_state.get('admin_until',0)
def require_admin():
    if not authorized():raise PermissionError('Connexion administrateur requise.')
def save(p):
    require_admin()
    with lock():
        atomic_write(ROOT/'project.json',json.dumps(p,ensure_ascii=False,indent=2).encode())
        if secret('S3_BUCKET'):
            try:s3_client().put_object(Bucket=secret('S3_BUCKET'),Key=secret('S3_KEY','parcours/project.zip'),Body=snapshot(ROOT),ContentType='application/zip')
            except Exception:
                st.error('Enregistré localement, mais sauvegarde distante échouée. Téléchargez votre sauvegarde avant de quitter.');return False
    st.success('Projet enregistré. Les visiteurs le verront après actualisation.');return True

st.markdown('''<style>.stApp{background:#f5f2ec}header[data-testid="stHeader"]{background:#f5f2ec}h1{font-family:Georgia,serif!important;font-weight:400!important}div[data-testid="stSidebar"]{background:#e9e4da}.block-container{padding-top:2rem}div.stButton>button{border-radius:24px}</style>''',unsafe_allow_html=True)
with st.sidebar:
    st.caption('HATEM ELLOUZE · ARCHITECTURE')
    page=st.radio('Espace',['Visite','Administration'])
    st.divider();st.caption('Une maquette à explorer. Des ambiances à découvrir.')
p=project()
if page=='Administration':
    st.title('Atelier du projet')
    pwd=secret('ADMIN_PASSWORD')
    if len(pwd)<12:
        st.info('Configurez ADMIN_PASSWORD (au moins 12 caractères) dans les secrets Streamlit pour activer l’administration. Aucun mot de passe par défaut.');st.stop()
    if not authorized():
        with st.form('login'):
            entered=st.text_input('Mot de passe administrateur',type='password')
            submit=st.form_submit_button('Se connecter')
        if submit:
            if time.time()<st.session_state.get('retry_after',0):st.error('Veuillez patienter avant de réessayer.')
            elif hmac.compare_digest(entered.encode(),pwd.encode()):
                st.session_state.admin_until=time.time()+1800;st.rerun()
            else:
                st.session_state.retry_after=time.time()+3;st.error('Mot de passe incorrect.')
        st.stop()
    if st.button('Se déconnecter'):st.session_state.admin_until=0;st.rerun()
    st.caption('Session de 30 minutes. Seul cet espace permet de modifier le projet.')
    if not secret('S3_BUCKET'):st.warning('Stockage local actif. Sur Streamlit Cloud, téléchargez une sauvegarde après vos changements : les fichiers importés peuvent disparaître au redémarrage. Configurez S3 pour une conservation automatique durable (guide inclus).')
    a,b,c,d=st.tabs(['Présentation','Maquette','Rendus et positions','Sauvegarde'])
    with a:
        with st.form('presentation'):
            title=st.text_input('Nom du projet',p['title']);sub=st.text_input('Sous-titre',p.get('subtitle',''))
            if st.form_submit_button('Enregistrer la présentation'):
                p.update(title=title,subtitle=sub);save(p)
    with b:
        st.write('Importez un **GLB**, un **DAE**, ou un **ZIP contenant un DAE et ses textures**. Le DAE est converti en maquette légère avec couleurs simplifiées ; le GLB conserve ses matériaux.')
        st.caption('Le fichier .skp seul n’est pas lisible par le navigateur. Exportez-le depuis SketchUp. Limite : 200 Mo par fichier, 350 Mo décompressés.')
        model=st.file_uploader('Maquette pour la visite',type=['dae','glb','zip'])
        if st.button('Importer et remplacer la maquette',disabled=model is None):
            require_admin()
            try:
                with st.spinner('Conversion et optimisation de la maquette…'):
                    blob,cams=convert_model(model.getvalue(),model.name)
                    with lock():
                        require_admin();atomic_write(ROOT/'model.glb',blob);p['cameras']=cams
                        for v in p['views']:v['camera_id']=None
                        save(p)
                st.info(f'{len(cams)} caméras importées. Associez à nouveau les rendus aux caméras dans le troisième onglet.')
            except Exception as e:st.error(f'Import impossible : {str(e)[:250]}')
        skp=st.file_uploader('Source SketchUp à conserver (facultatif, non affichée)',type=['skp'])
        if st.button('Conserver le fichier source',disabled=skp is None):
            require_admin();atomic_write(ROOT/'source.skp',skp.getvalue());save(p)
    with c:
        st.write('Les rendus sont déjà intégrés. Leur association aux caméras est à vérifier : aucun emplacement n’a été deviné.')
        files=st.file_uploader('Ajouter des rendus',type=['jpg','jpeg','png'],accept_multiple_files=True)
        if st.button('Ajouter les images',disabled=not files):
            require_admin()
            try:
                for f in files:
                    im=Image.open(f);im.verify();im=Image.open(f).convert('RGB');im.thumbnail((2000,2000));out=io.BytesIO();im.save(out,format='JPEG',quality=90)
                    uid=uuid.uuid4().hex;rel=f'images/{uid}.jpg';atomic_write(ROOT/rel,out.getvalue());p['views'].append({'id':uid,'title':Path(f.name).stem,'image':rel,'camera_id':None})
                save(p);st.rerun()
            except Exception as e:st.error(f'Image non valide : {str(e)[:150]}')
        if p['views']:
            selected=st.selectbox('Rendu à modifier',range(len(p['views'])),format_func=lambda i:p['views'][i]['title']);v=p['views'][selected]
            st.image(str(ROOT/v['image']),width=550)
            cams=p['cameras'];ids=[None]+[x['id'] for x in cams];names={x['id']:x['name'] for x in cams}
            with st.form('edit_view'):
                label=st.text_input('Titre du rendu',v['title']);cid=st.selectbox('Caméra correspondante',ids,index=ids.index(v.get('camera_id')) if v.get('camera_id') in ids else 0,format_func=lambda x:names.get(x,'Non associée · galerie seulement'))
                order=st.number_input('Position dans le parcours',1,len(p['views']),selected+1)
                if st.form_submit_button('Enregistrer cette vue'):
                    v.update(title=label,camera_id=cid);p['views'].pop(selected);p['views'].insert(int(order)-1,v);save(p);st.rerun()
            st.caption('Pour identifier une caméra, ouvrez la visite et sélectionnez son nom dans « Caméras SketchUp ». Revenez ensuite l’associer ici.')
            confirm=st.checkbox('Confirmer le retrait de cette vue de la visite')
            if st.button('Retirer la vue',disabled=not confirm):
                require_admin();p['views'].pop(selected);save(p);st.rerun()
        with st.expander('Ajouter un point de vue à une maquette GLB'):
            st.caption('Coordonnées en mètres, axe vertical Y. Les caméras DAE sont importées automatiquement.')
            with st.form('camera'):
                name=st.text_input('Nom du point');pos=st.text_input('Position x,y,z','0,1.6,0');target=st.text_input('Point regardé x,y,z','0,1.6,-3')
                if st.form_submit_button('Ajouter le point'):
                    try:
                        xyz=[float(x) for x in pos.split(',')];t=[float(x) for x in target.split(',')]
                        import math
                        if len(xyz)!=3 or len(t)!=3 or not all(math.isfinite(x) for x in xyz+t) or xyz==t:raise ValueError()
                        p['cameras'].append({'id':uuid.uuid4().hex,'name':name or 'Point de vue','position':xyz,'target':t,'fov':50});save(p);st.rerun()
                    except ValueError:st.error('Saisissez trois nombres finis séparés par des virgules, avec deux points distincts.')
    with d:
        if st.button('Préparer la sauvegarde complète'):
            require_admin();st.session_state.backup=snapshot(ROOT)
        if 'backup' in st.session_state:st.download_button('Télécharger le projet ZIP',st.session_state.backup,'projet_visite.zip','application/zip')
        st.caption('Pour conserver les modifications sur GitHub : décompressez cette sauvegarde dans le dossier data/ du dépôt. Le ZIP ne contient pas le mot de passe.')
else:
    st.caption('PARCOURS / VISITE VIRTUELLE')
    st.title(p['title']);st.write(p.get('subtitle',''))
    if not (ROOT/'model.glb').exists():st.info('La maquette sera disponible après son import par l’administrateur.')
    elif not p['views']:st.info('La maquette est disponible ; les rendus seront ajoutés par l’administrateur.')
    if (ROOT/'model.glb').exists():
        payload={'model':base64.b64encode((ROOT/'model.glb').read_bytes()).decode(),'cameras':p['cameras'],'views':[]}
        for v in p['views']:
            f=ROOT/v['image']
            if f.exists():payload['views'].append({**v,'src':'data:image/jpeg;base64,'+base64.b64encode(f.read_bytes()).decode()})
        html=(BASE/'viewer.html').read_text().replace('__PAYLOAD__',json.dumps(payload,ensure_ascii=False).replace('<','\\u003c'))
        components.html(html,height=790,scrolling=True)
        st.caption('Les rendus sont des images fixes. La maquette permet de se repérer ; elle ne reproduit pas leur éclairage photoréaliste. Les points dorés apparaissent après association des vues par l’administrateur.')
