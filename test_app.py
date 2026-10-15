import os,tempfile,json,io,zipfile,unittest
from pathlib import Path
from core import extract_zip
from streamlit.testing.v1 import AppTest

class Tests(unittest.TestCase):
    def test_zip_traversal_rejected(self):
        b=io.BytesIO()
        with zipfile.ZipFile(b,'w') as z:z.writestr('../outside.txt','bad')
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):extract_zip(b.getvalue(),Path(d))
    def test_auth_and_write(self):
        with tempfile.TemporaryDirectory() as d:
            os.environ['PROJECT_DATA_DIR']=d;os.environ['ADMIN_PASSWORD']='test-only-long-password'
            try:
                at=AppTest.from_file(str(Path(__file__).with_name('app.py')),default_timeout=20).run()
                self.assertEqual(len(at.exception),0);self.assertEqual(len(at.get('file_uploader')),0)
                at.sidebar.radio[0].set_value('Administration').run()
                self.assertEqual(len(at.get('file_uploader')),0)
                at.text_input[0].set_value('wrong');at.button[0].click().run()
                self.assertEqual(len(at.get('file_uploader')),0)
                at.session_state['retry_after']=0
                at.text_input[0].set_value('test-only-long-password');at.button[0].click().run()
                self.assertEqual(len(at.exception),0);self.assertGreater(len(at.get('file_uploader')),0)
                [x for x in at.text_input if x.label=='Nom du projet'][0].set_value('Projet test')
                [b for b in at.button if b.label=='Enregistrer la présentation'][0].click().run()
                self.assertEqual(json.loads((Path(d)/'project.json').read_text())['title'],'Projet test')
                [b for b in at.button if b.label=='Se déconnecter'][0].click().run()
                self.assertEqual(len(at.get('file_uploader')),0)
            finally:
                os.environ.pop('PROJECT_DATA_DIR',None);os.environ.pop('ADMIN_PASSWORD',None)

if __name__=='__main__':unittest.main()
