from flask import Flask, render_template, request,send_from_directory
import sqlite3
import logging, os
from werkzeug.utils import secure_filename
#import db


app = Flask(__name__)

@app.route("/")
def index():
	con = sqlite3.connect('tables.db')
	cur = con.cursor()
	liste_posts= [row for row in cur.execute('SELECT * FROM post')]
	return render_template("index.html",err=None,Pswd=True,list_post=liste_posts)


@app.route("/admin",methods=["GET","POST"])
def admin():
    if request.method == "POST":
        mdp = request.form.get("mdp")
        pswd= mdp=="admin"
        return render_template("page_admin.html",err="Mot de passe incorrect",Pswd=pswd)
    err=""
    pswd=False
    return render_template("page_admin.html",err=err,Pswd=pswd)


file_handler = logging.FileHandler('server.log')
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
PROJECT_HOME = os.path.dirname(os.path.realpath(__file__))
UPLOAD_FOLDER = '{}/static/images/uploads/'.format(PROJECT_HOME)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000 #Taille maximum des images : 16 Mo
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_new_folder(local_dir):
    newpath = local_dir
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    return newpath

@app.context_processor		#pour pouvoir utiliser os dans les pages templates (ici pour aller chercher les images d'un certain projet)
def handle_context():
    return dict(os=os)




@app.route("/ajout",methods=["POST"])			
def ajout_projet():
	'''Route d'ajout d'un post dans la BD'''
	titre=request.form.get("titre")
	contenu=request.form.get("contenu")
	
	con = sqlite3.connect('tables.db')
	cur = con.cursor()
	liste_id_oqp= [row [0]for row in cur.execute('SELECT id FROM post')]			#Liste des id_projets déjà pris
	id_post=0
	for i in range(1000,2000):																	#Attribution du plus petit id_projet disponible et valide
		if not i in liste_id_oqp and id_post==0:
			id_post=i
	cur.execute('INSERT INTO post (id,title,body) VALUES(?,?,?)',(id_post,titre,contenu))
	con.commit()																				#Insertion du projet dans la table
	
	app.logger.info(PROJECT_HOME)
	if request.method == 'POST' and request.files['image']:
		app.logger.info(app.config['UPLOAD_FOLDER'])
		img=request.files['image']
		img_name = secure_filename(str(id_post)+".png")
		create_new_folder(app.config['UPLOAD_FOLDER'])
		saved_path = os.path.join(app.config['UPLOAD_FOLDER'], img_name)
		app.logger.info("saving {}".format(saved_path))
		img.save(saved_path)
		return send_from_directory(app.config['UPLOAD_FOLDER'],img_name, as_attachment=True)

	#liste_posts= [row for row in cur.execute('SELECT * FROM post')]
	return render_template("page_admin.html",err=None,Pswd=True)					

if __name__ == "__main__":
    
    #db.init_app(app)
    #os.system("flask init-db")
    app.run(debug=True)