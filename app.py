from flask import Flask, render_template, request, redirect, url_for, session 
from flask_pymongo import PyMongo
import re
from services import plant_model 
from PIL import Image 
import io 
import os 
from werkzeug.utils import secure_filename
import numpy as np
import uuid
from datetime import datetime
import pymongo
import copy
import sys
from werkzeug.datastructures import FileStorage

#sys.setrecursionlimit(10000)

app = Flask(__name__)
app.secret_key = '\x8a\xc8\x12\xf8)\x83\xe9u\xcb`ZS\xce\x04\x966wYZd\xe5\x89\xe6\x81'

UPLOAD_FOLDER = 'static/uploads/'

app.config["MONGO_URI"] = "mongodb://localhost:27017/Plant_Diagnosis"
#app.config["MONGO_URI"] = "mongodb+srv://varshajenni:varsha99@cluster0.a6igs.mongodb.net/Plant_diagnosis?retryWrites=true&w=majority"

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

mongo = PyMongo(app)

app.debug = True


@app.route("/")
def home_page():
    return render_template("home_page.html")


@app.route("/farmer_signup", methods =['GET', 'POST'])
def farmer_signup():
	msg = ''
	if request.method == 'POST' and 'Username' in request.form and 'Password' in request.form and 'Email' in request.form:
		username = request.form['Username']
		password = request.form['Password']
		email = request.form['Email']
		name = request.form['Name']
		address = request.form['Address']
		phno = request.form['Phno']
		gender = request.form['Gender']
		print('hi')
		account = mongo.db.Farmer.find_one({"Username": username})
		if account: 
			msg = 'Account already exists !'
		elif not re.match(r'[^@]+@[^@]+\.[^@]+', email): 
			msg = 'Invalid email address !'
		elif not re.match(r'[A-Za-z0-9]+', username): 
			msg = 'Username must contain only characters and numbers !'
		elif not username or not password or not email: 
			msg = 'Please fill out the form !'
		else: 
			mongo.db.Farmer.insert_one({"Username": username, "Password": password, "Email": email,"Name": name, "Address": address, "Phno": phno, "Gender": gender})
			msg = 'You have successfully registered !'
			
	elif request.method == 'POST': 
		msg = 'Please fill out the form !'
		 
	return render_template('farmer_signup.html', msg = msg)


@app.route("/farmer_login", methods =['GET', 'POST'])
def farmer_login():
	msg = ''
	if request.method == 'POST' and 'Username' in request.form and 'Password' in request.form:
		username = request.form['Username']
		password = request.form['Password']
		

		account = mongo.db.Farmer.find_one({"Username": username, "Password" : password})
		if account: 
			session['Farmer_loggedin'] = True
			session['Farmer_Username'] = account['Username'] 
			session['Farmer_Email'] = account['Email'] 
			msg = 'Logged in successfully !'
			return render_template("upload_image.html", msg = msg) 
		else: 
			msg = 'Incorrect username / password !'
			
	elif request.method == 'POST': 
		msg = 'Please enter username and password!'
		 
	return render_template('farmer_login.html', msg = msg) 

@app.route("/upload_image", methods =['GET', 'POST'])
def upload_image():
	if session['Farmer_loggedin']:
		msg = ''
		if request.method == 'POST':
			diseases = {0: 'Apple___healthy', 1 : 'Tomato___Target_Spot', 2: 'Cherry_(including_sour)___healthy', 3:'Tomato___Tomato_Yellow_Leaf_Curl_Virus', 4: 'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot', 5:'Tomato___Late_blight', 6: 'Squash___Powdery_mildew', 7: 'Strawberry___Leaf_scorch', 8: 'Tomato___healthy', 9: 'Cherry_(including_sour)___Powdery_mildew', 10: 'Raspberry___healthy', 11: 'Pepper,_bell___healthy', 12: 'Corn_(maize)___healthy', 13: 'Apple___Cedar_apple_rust', 14: 'Strawberry___healthy', 15: 'Grape___Black_rot', 16: 'Grape___healthy', 17: 'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)', 18: 'Tomato___Leaf_Mold', 19: 'Tomato___Early_blight', 20: 'Grape___Esca_(Black_Measles)', 21: 'Tomato___Tomato_mosaic_virus', 22: 'Potato___Early_blight', 23: 'Apple___Apple_scab', 24: 'Blueberry___healthy', 25: 'Soybean___healthy', 26: 'Soybean___healthy', 27: 'Potato___healthy', 28: 'Tomato___Bacterial_spot', 29: 'Peach___healthy', 30: 'Potato___Late_blight', 31: 'Peach___Bacterial_spot', 32: 'Tomato___Spider_mites Two-spotted_spider_mite', 33: 'Pepper,_bell___Bacterial_spot', 34: 'Corn_(maize)___Common_rust_', 35: 'Tomato___Septoria_leaf_spot', 36: 'Orange___Haunglongbing_(Citrus_greening)', 37: 'Corn_(maize)___Northern_Leaf_Blight'}
			file = request.files['file']
			#file1 = copy.deepcopy(file)

			image = file.read()
			image = Image.open(io.BytesIO(image)) 

			unique_filename = str(uuid.uuid4()) + '.jpg'
			datetime_now = datetime.now()

			pred = plant_model.make_predictions(image)
			pred = diseases[pred]
			

			#mongo.save_file(unique_filename, image)
			mongo.db.Images.insert({'Farmer_Username': session['Farmer_Username'], 'Image': unique_filename, 'datetime': datetime_now, 'Expert_Username': ' ', 'response': ' ', 'Disease': pred})

			
			

			#filename = secure_filename(file.filename)
			im = np.reshape(image, [256, 256, 3])
			im = Image.fromarray(im)
			im.save('static/uploads/'+ unique_filename)
			

			 
			
			
			return redirect(url_for('farmer_request', pred = pred, filename = unique_filename)) 

		return render_template("upload_image.html")

@app.route("/farmer_request/<pred>/<filename>", methods =['GET', 'POST'])
def farmer_request(pred, filename):
	if session['Farmer_loggedin']: 
		fname = 'uploads/' + filename
		f = open('static/'+fname, 'rb')
		file = FileStorage(f)
		mongo.save_file(filename, file)
		if request.method == 'POST':
			experts = mongo.db.Expert.find({}).sort([("no_of_request", pymongo.ASCENDING)])

			Expert_Username = experts[0]['Username']
			no_of_request = experts[0]['no_of_request'] + 1

			mongo.db.Expert.update_one({'Username' : Expert_Username}, {'$set': {'no_of_request': no_of_request}})
			mongo.db.Images.update_one({'Image': filename}, {'$set': {'Expert_Username': Expert_Username}})
			return render_template("upload_image.html") 

		return render_template("request.html", pred = pred, filename  = fname)

		
@app.route("/diagnosis_history", methods = ['GET', 'POST'])
def diagnosis_history():
	if session['Farmer_loggedin']:
		content = mongo.db.Images.find({'Farmer_Username': session['Farmer_Username']}).sort("datetime", pymongo.DESCENDING)
		return render_template("diagnosis_history.html", content = content)



@app.route('/farmer_logout') 
def farmer_logout(): 
    session.pop('Farmer_loggedin', None) 
    session.pop('Farmer_Username', None) 
    session.pop('Farmer_Email', None) 
    return redirect(url_for('farmer_login')) 


@app.route("/expert_login", methods =['GET', 'POST'])
def expert_login():
	msg = ''
	if request.method == 'POST' and 'Username' in request.form and 'Password' in request.form:
		username = request.form['Username']
		password = request.form['Password']
		

		account = mongo.db.Expert.find_one({"Username": username, "Password" : password})
		if account: 
			session['Expert_loggedin'] = True
			session['Expert_Username'] = account['Username'] 
			session['Expert_Email'] = account['Email'] 
			msg = 'Logged in successfully !'
			return redirect(url_for('view_requests')) 
		else: 
			msg = 'Incorrect username / password !'
			
	elif request.method == 'POST': 
		msg = 'Please enter username and password!'
		 
	return render_template('expert_login.html', msg = msg) 


@app.route('/expert_logout') 
def expert_logout(): 
    session.pop('Expert_loggedin', None) 
    session.pop('Expert_Username', None) 
    session.pop('Expert_Email', None) 
    return redirect(url_for('expert_login')) 


@app.route("/view_requests", methods =['GET', 'POST'])
def view_requests():
	if session['Expert_loggedin']:
		img_data = mongo.db.Images.find({'Expert_Username': session['Expert_Username'], 'response': ' ' })
		if request.method == 'POST':
			img = request.form['submit_button']
			response = request.form[img]
			mongo.db.Images.update_one({'Image': img, 'Expert_Username': session['Expert_Username']}, {'$set':{'response': response}})
			img_data = mongo.db.Images.find({'Expert_Username': session['Expert_Username'], 'response': ' ' })
			return render_template("view_requests.html" , content = img_data)

		

		return render_template("view_requests.html" , content = img_data)


@app.route("/view_image/<fname>")
def view_image(fname):
	return mongo.send_file(fname)



	
if( __name__ == "__main__"):
	app.run(debug=True,use_reloader=True)