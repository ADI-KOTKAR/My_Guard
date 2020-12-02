import boto3
import csv
import os
import random
import string
import shutil
import time
import datetime
from dotenv import load_dotenv
from flask import Blueprint, current_app, render_template, url_for, redirect, request, session, flash
from werkzeug.utils import secure_filename
from ..extensions import mongo

register = Blueprint("register", __name__, static_folder="images", template_folder="templates")

@register.route("/")
def register_details():
    return render_template("register_details.html")

@register.route("/form-result", methods=['POST','GET'])
def register_form_result():
    if request.method == 'POST':
        name = request.form['name']
        user_id = str('MG-'+''.join(random.choices(string.ascii_uppercase + string.digits, k = 4)) )
        if 'file' not in request.files:
            flash('No image found')
        file = request.files['image']
        
        if file.filename == '':
            flash('No image selected')
        
        if file:
            filename = secure_filename(str(user_id)+".jpg")
            file.save(os.path.join(current_app.config['REGISTER_IMAGES_FOLDER'], filename))
            image = str(user_id)+".jpg"
            #AWS Bucket upload
            load_dotenv()
            s3 = boto3.resource('s3',
                            aws_access_key_id = os.getenv("ACCESS_KEY_ID"),
                            aws_secret_access_key = os.getenv("SECRET_ACCESS_KEY"),
                            region_name='us-east-2')
            data = open(os.path.join(current_app.config['REGISTER_IMAGES_FOLDER'], filename), 'rb')
            s3.Bucket('adis-aws-bucket').put_object(Key=str(image), Body=data)
        result = request.form
        timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')

        # MongoDB Atlas
        user_entry = {
            "_id": user_id,
            "name": name,
            "timestamp": timestamp
        }
        user_collection = mongo.db.users
        user_collection.insert_one(user_entry)
        
        return render_template("register_form-result.html",
                                result = result, 
                                file=image, 
                                user_id=user_id, 
                                name=name, 
                                timestamp=timestamp)

@register.route("/users")
def users():
    # Mongo DB Atlas - Users
    results = mongo.db.users.find({})
    return render_template("users.html", results=results)

