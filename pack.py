from pathlib import Path
import base64,copy,json,mimetypes
BASE=Path(__file__).parent

def payload(project,root,editor=False,start=None):
    p=copy.deepcopy(project)
    def src(rel):
        f=(root/rel).resolve()
        if not f.is_relative_to(root.resolve()):raise ValueError('Chemin de fichier non autorisé')
        return 'data:'+ (mimetypes.guess_type(f.name)[0] or 'image/jpeg')+';base64,'+base64.b64encode(f.read_bytes()).decode()
    for s in p['scenes']:
        s['src']=src(s['image'])
        if s.get('detail_image'):s['detailSrc']=src(s['detail_image'])
        if s.get('thumbnail'):s['thumb']=src(s['thumbnail'])
    for g in p.get('gallery',[]):g['src']=src(g['image'])
    p['editor']=editor
    if start:p['start']=start
    return p

def html(project,root,editor=False,start=None):
    return (BASE/'viewer.html').read_text().replace('__PAYLOAD__',json.dumps(payload(project,root,editor,start),ensure_ascii=False).replace('<','\\u003c'))

if __name__=='__main__':
    import sys
    root=BASE/'data';out=Path(sys.argv[1]) if len(sys.argv)>1 else BASE/'Visite_interactive.html'
    out.write_text(html(json.loads((root/'tour.json').read_text()),root))
    print(str(out.resolve()))
