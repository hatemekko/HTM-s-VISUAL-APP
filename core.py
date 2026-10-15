from pathlib import Path
import json, io, zipfile, tempfile, os
import xml.etree.ElementTree as ET
import numpy as np

MAX_ARCHIVE = 350 * 1024**2

def extract_zip(raw, dest):
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        if sum(i.file_size for i in z.infolist()) > MAX_ARCHIVE:
            raise ValueError('Archive décompressée trop volumineuse (350 Mo maximum).')
        for i in z.infolist():
            p = (dest / i.filename).resolve()
            if not p.is_relative_to(dest.resolve()) or i.filename.startswith('/'):
                raise ValueError('Chemin interdit dans le ZIP.')
        z.extractall(dest)

def cameras_from_dae(path):
    root = ET.parse(path).getroot(); ns={'c':root.tag.split('}')[0][1:]}
    unit=root.find('c:asset/c:unit',ns); scale=float(unit.get('meter','1')) if unit is not None else 1
    up=root.findtext('c:asset/c:up_axis',default='Y_UP',namespaces=ns)
    rot=np.eye(4)
    if up=='Z_UP':rot[:3,:3]=[[1,0,0],[0,0,1],[0,-1,0]]
    defs={c.get('id'):c for c in root.findall('.//c:library_cameras/c:camera',ns)}
    out=[]
    def walk(node,parent):
        mat=parent.copy()
        for el in node:
            tag=el.tag.split('}')[-1]; m=np.eye(4)
            if tag=='matrix':m=np.fromstring(el.text,sep=' ').reshape(4,4)
            elif tag=='translate':m[:3,3]=np.fromstring(el.text,sep=' ')
            elif tag=='scale':m[:3,:3]=np.diag(np.fromstring(el.text,sep=' '))
            elif tag=='rotate':
                import trimesh
                v=np.fromstring(el.text,sep=' ');m=trimesh.transformations.rotation_matrix(np.deg2rad(v[3]),v[:3])
            else:continue
            mat=mat@m
        camera=node.find('c:instance_camera',ns)
        if camera is not None:
            c=defs.get(camera.get('url','').lstrip('#')); world=rot@mat;pos=world[:3,3]*scale
            fov=50.0
            if c is not None:
                yf=c.findtext('.//c:yfov',namespaces=ns)
                if yf:fov=float(yf)
                else:
                    xf=c.findtext('.//c:xfov',namespaces=ns);ar=c.findtext('.//c:aspect_ratio',default='1.777778',namespaces=ns)
                    if xf:fov=float(np.rad2deg(2*np.arctan(np.tan(np.deg2rad(float(xf))/2)/float(ar))))
            out.append({'id':camera.get('url').lstrip('#'),'name':node.get('name','Vue').replace('skp_camera_',''),'position':pos.tolist(),'target':(pos-world[:3,2]*3).tolist(),'fov':fov})
        for ch in node.findall('c:node',ns):walk(ch,mat)
    vs=root.find('.//c:visual_scene',ns)
    if vs is not None:
        for node in vs.findall('c:node',ns):walk(node,np.eye(4))
    return out,scale,rot

def convert_model(raw,name):
    import trimesh
    with tempfile.TemporaryDirectory() as td:
        td=Path(td)
        if name.lower().endswith('.zip'):
            extract_zip(raw,td);files=list(td.rglob('*.dae'))+list(td.rglob('*.glb'))
            if len(files)!=1:raise ValueError('Le ZIP doit contenir exactement une maquette DAE ou GLB et ses textures.')
            p=files[0]
        else:
            p=td/('model'+Path(name).suffix.lower());p.write_bytes(raw)
        if p.suffix.lower() not in ('.dae','.glb'):raise ValueError('Exporter le fichier SketchUp en DAE ou GLB.')
        cams=[]
        if p.suffix.lower()=='.dae':
            cams,scale,rot=cameras_from_dae(p)
            scene=trimesh.load(p,force='scene')
            parts=scene.dump()
            for mesh in parts:
                if mesh.visual.kind=='texture':
                    try: mesh.visual=mesh.visual.to_color()
                    except Exception: mesh.visual=trimesh.visual.ColorVisuals(mesh=mesh,face_colors=[205,201,192,255])
            vertices=[];faces=[];colors=[];offset=0
            for m in parts:
                vertices.append(np.asarray(m.vertices)*scale@rot[:3,:3].T)
                faces.append(np.asarray(m.faces)+offset)
                colors.append(m.visual.vertex_colors)
                offset+=len(m.vertices)
            merged=trimesh.Trimesh(vertices=np.concatenate(vertices),faces=np.concatenate(faces),vertex_colors=np.concatenate(colors),process=False)
            merged.merge_vertices()
            if len(merged.faces)>650000:
                merged=merged.simplify_quadric_decimation(face_count=650000)
            merged.visual=trimesh.visual.ColorVisuals(mesh=merged,face_colors=[205,201,192,255])
            scene=trimesh.Scene(merged)
            blob=scene.export(file_type='glb')
        else:
            scene=trimesh.load(p,force='scene');blob=raw if not name.lower().endswith('.zip') else p.read_bytes()
        if not scene.geometry:raise ValueError('Aucune géométrie trouvée.')
        return blob,cams

def snapshot(root):
    b=io.BytesIO()
    with zipfile.ZipFile(b,'w',zipfile.ZIP_DEFLATED) as z:
        for p in root.rglob('*'):
            if p.is_file():z.write(p,p.relative_to(root))
    return b.getvalue()

def atomic_write(path,raw):
    path.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(dir=path.parent)
    try:
        with os.fdopen(fd,'wb') as f:f.write(raw)
        os.replace(tmp,path)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)
