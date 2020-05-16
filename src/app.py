import hashlib
from flask import Flask, render_template, request, redirect, url_for,send_from_directory, make_response
from werkzeug.utils import secure_filename
from pymongo import MongoClient
import os


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'upload'

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
client = MongoClient('localhost', 27017)


db=client.users

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def home():    
    return render_template("index.html") 

	
@app.route('/cabinet',methods=['POST'])
def login():
	check=0
	user_name=request.form['user_name']
	user_password=request.form['user_password']
	user_password=hashlib.md5(user_password.encode()).hexdigest()
	for user in db.info.find({"login":user_name,"password":user_password}):
		if user.get("password")==user_password:
			check=1
		else:
			check=0
	if check==1:
			avatar=request.cookies.get('url')
			avatar_url="upload"+"/"+avatar
			return render_template('cabinet.html',user_name=user_name,avatar_url=avatar_url)
	else:
			return render_template('index.html',error="Invalid login or password")
@app.route('/logout',methods=['POST'])
def logout():
	return render_template('index.html')

@app.route('/register')
def reg():
	return render_template('registration.html')
	
@app.route('/upload', methods=['GET','POST'])
def upload():
	if request.method == 'POST':
		if 'file' not in request.files:
			flash('No file part')
			return redirect(request.url)
		file = request.files['file']
		if file.filename == '':
			flash('No selected file')
			return redirect(request.url)
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			response=make_response(redirect(url_for('uploaded_file',
                                    filename=filename))	)
			response.set_cookie('url',filename) 
			return response
		
@app.route('/upload/<filename>')
def uploaded_file(filename):
	return send_from_directory(app.config['UPLOAD_FOLDER'],filename)
@app.route('/newuser',methods=['POST'])
def newuser():
	user_name=request.form['user_name']
	user_password=request.form['user_password']
	user_password=hashlib.md5(user_password.encode()).hexdigest()
	user_email=request.form['user_email']
	db.info.insert({"login": user_name, "password": user_password, "e-mail":user_email})
	return render_template('cabinet.html',user_name=user_name)
	
@app.errorhandler(405)
def page_not_found(e):
	return render_template('405.html')
	
if __name__ == "__main__":    
    app.run()
	