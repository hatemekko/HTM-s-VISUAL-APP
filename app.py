from pathlib import Path
import os,json,time,hmac,uuid,io,zipfile,copy,math
import streamlit as st
import streamlit.components.v1 as components
from PIL import Image
from pack import html, html_streamed
BASE=Path(__file__).parent
ROOT=Path(os.environ.get('PROJECT_DATA_DIR',str(BASE/'static'/'data')))
ROOT.mkdir(parents=True,exist_ok=True)
st.set_page_config(page_title='Parcours · Hatem Ellouze',page_icon='◈',layout='wide')
st.markdown('<style>.block-container{padding-top:1rem;padding-bottom:0}header[data-testid="stHeader"]{background:transparent}.stApp{background:#171a14;color:#eee}h1{font-family:Georgia,serif}</style>',unsafe_allow_html=True)
def read():return json.loads((ROOT/'tour.json').read_text())
def authorized():return time.time()<st.session_state.get('admin_until',0)
def require_admin():
    if not authorized():raise PermissionError('Connexion requise')
def save(p):
    require_admin();tmp=ROOT/'tour.tmp';tmp.write_text(json.dumps(p,ensure_ascii=False,indent=2));tmp.replace(ROOT/'tour.json')
def img_write(upload,folder,panorama=False):
    require_admin()
    if upload.size>25*1024*1024:raise ValueError('Image limitée à 25 Mo.')
    im=Image.open(upload);im.load()
    if panorama and abs(im.width/im.height-2)>.05:raise ValueError('Un panorama équirectangulaire doit avoir un rapport 2:1.')
    im=im.convert('RGB');im.thumbnail((4096,2048) if panorama else (2400,2400))
    rel=f'{folder}/{uuid.uuid4().hex}.jpg';path=ROOT/rel;path.parent.mkdir(exist_ok=True);im.save(path,quality=93);return rel
def backup():
    out=io.BytesIO()
    with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
        for f in ROOT.rglob('*'):
            if f.is_file():z.write(f,f.relative_to(ROOT))
    return out.getvalue()
with st.sidebar:
    st.caption('HATEM ELLOUZE · ARCHITECTURE')
    mode=st.radio('Espace',['Visite','Administration'])
p=read()
if mode=='Visite':
    components.html(html_streamed(p,ROOT),height=850,scrolling=False)
    st.stop()
st.title('Administration de la visite')
try:pwd=os.environ.get('ADMIN_PASSWORD') or st.secrets.get('ADMIN_PASSWORD','')
except FileNotFoundError:pwd=''
if len(pwd)<12:
    st.info('Définissez ADMIN_PASSWORD avec au moins 12 caractères dans les secrets Streamlit pour activer cet espace. Aucun mot de passe n’est inclus dans la visite.');st.stop()
if not authorized():
    with st.form('login'):
        typed=st.text_input('Mot de passe',type='password');submit=st.form_submit_button('Se connecter')
    if submit:
        if time.time()<st.session_state.get('retry_after',0):st.error('Patientez quelques secondes.')
        elif hmac.compare_digest(typed.encode(),pwd.encode()):st.session_state.admin_until=time.time()+1800;st.rerun()
        else:st.session_state.retry_after=time.time()+5;st.error('Mot de passe incorrect.')
    st.stop()
if st.button('Se déconnecter'):st.session_state.admin_until=0;st.rerun()
st.caption('Session de 30 minutes. Les visiteurs ne peuvent pas modifier la visite.')
st.info('Après une modification, téléchargez la sauvegarde et remplacez le dossier data/ de votre dépôt GitHub. Le disque Streamlit Cloud n’est pas un stockage permanent.')
a,b,c,d,e=st.tabs(['Panoramas','Passages','Axonométries','Sources SketchUp','Exporter'])
with a:
    selected=st.selectbox('Point de vue',range(len(p['scenes'])),format_func=lambda i:p['scenes'][i]['title']);s=p['scenes'][selected]
    with st.form('scene'):
        title=st.text_input('Nom',s['title']);level=st.text_input('Niveau',s['level']);start=st.checkbox('Commencer la visite ici',p['start']==s['id']);upload=st.file_uploader('Remplacer le panorama 360° (2:1)',type=['png','jpg','jpeg'])
        if st.form_submit_button('Enregistrer'):
            try:
                if upload:s['image']=img_write(upload,'panoramas',True);s.pop('thumbnail',None)
                s.update(title=title,level=level)
                if start:p['start']=s['id']
                save(p);st.success('Enregistré');st.rerun()
            except Exception as ex:st.error(str(ex))
    with st.expander('Ajouter un panorama'):
        with st.form('new'):
            title=st.text_input('Nom du nouvel espace');level=st.selectbox('Niveau du nouvel espace',['Rez-de-chaussée','Étage']);upload=st.file_uploader('Nouveau panorama 2:1',type=['png','jpg','jpeg'])
            if st.form_submit_button('Ajouter'):
                try:
                    if not upload or not title:raise ValueError('Indiquez un nom et une image.')
                    rel=img_write(upload,'panoramas',True);p['scenes'].append(dict(id=uuid.uuid4().hex,title=title,level=level,image=rel,heading=0,links=[]));save(p);st.rerun()
                except Exception as ex:st.error(str(ex))
with b:
    ids=[s['id'] for s in p['scenes']];names={s['id']:s['title'] for s in p['scenes']}
    origin=st.selectbox('Depuis quel panorama ?',ids,format_func=lambda x:names[x]);scene=next(s for s in p['scenes'] if s['id']==origin)
    st.write('Tournez la vue pour placer le passage au centre. Copiez les coordonnées affichées, puis choisissez la destination. Ajoutez aussi le passage de retour depuis l’autre vue.')
    components.html(html_streamed(p,ROOT,editor=True,start=origin),height=560)
    with st.form('link'):
        dest=st.selectbox('Destination',[i for i in ids if i!=origin],format_func=lambda x:names[x]);coords=st.text_input('Coordonnées copiées',value='{"yaw":0,"pitch":-0.2}');label=st.text_input('Libellé du repère (facultatif)');kind=st.selectbox('Type de passage',['Passage','Monter','Descendre'])
        if st.form_submit_button('Ajouter ou remplacer ce passage'):
            try:
                v=json.loads(coords);yaw=float(v['yaw']);pitch=float(v['pitch'])
                if not math.isfinite(yaw) or not math.isfinite(pitch) or abs(pitch)>1.5:raise ValueError('Coordonnées non valides')
                scene['links']=[l for l in scene.get('links',[]) if l['to']!=dest]+[dict(to=dest,yaw=yaw,pitch=pitch,label=label or names[dest],kind={'Passage':'walk','Monter':'up','Descendre':'down'}[kind])];save(p);st.rerun()
            except Exception as ex:st.error(str(ex))
    links=scene.get('links',[])
    if links:
        ix=st.selectbox('Passage à retirer',range(len(links)),format_func=lambda i:links[i].get('label',names.get(links[i]['to'],'Passage')))
        if st.button('Retirer ce passage'):scene['links'].pop(ix);save(p);st.rerun()
with c:
    st.write('Ces images restent fixes et sont accessibles dans « Axonométries ».')
    for g in p['gallery']:st.image(str(ROOT/g['image']),caption=g['title'],width=360)
    with st.form('gallery'):
        label=st.text_input('Titre de l’image');upload=st.file_uploader('Ajouter une axonométrie',type=['png','jpg','jpeg'])
        if st.form_submit_button('Ajouter l’image'):
            try:
                if not upload or not label:raise ValueError('Indiquez un titre et une image.')
                p['gallery'].append(dict(title=label,image=img_write(upload,'galerie')));save(p);st.rerun()
            except Exception as ex:st.error(str(ex))
with d:
    st.write('Conservez ici le fichier SketchUp et son export DAE. L’import d’une maquette ou d’une photo simple ne génère pas automatiquement un panorama réaliste. Les panoramas préparés se chargent dans le premier onglet.')
    source=st.file_uploader('Source du projet',type=['skp','dae'])
    if st.button('Conserver cette source',disabled=source is None):
        require_admin();folder=ROOT/'sources';folder.mkdir(exist_ok=True);(folder/('modele'+Path(source.name).suffix.lower())).write_bytes(source.getvalue());st.success('Source conservée. Pensez à télécharger la sauvegarde.')
with e:
    if st.button('Préparer les fichiers à télécharger'):
        require_admin();st.session_state['export_html']=html(p,ROOT).encode();st.session_state['backup']=backup()
    if 'export_html' in st.session_state:
        st.download_button('Visite autonome HTML',st.session_state['export_html'],'Visite_interactive.html','text/html')
        st.download_button('Sauvegarde du dossier data/',st.session_state['backup'],'data_visite.zip','application/zip')
