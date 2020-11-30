import boto3
import csv
from csv import writer
import os
import random
import string
import shutil
import time
import datetime
from dotenv import load_dotenv
from flask import Blueprint, current_app, render_template, url_for, redirect, request, session, flash
from werkzeug.utils import secure_filename

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
        
        # Writing in CSV
        with open(os.path.join(current_app.config['REGISTER_IMAGES_FOLDER'], 'registered_users.csv'), 'a+', newline='') as write_obj:
            csv_writer = writer(write_obj)
            csv_writer.writerow([user_id, name, timestamp])
        
        return render_template("register_form-result.html",
                                result = result, 
                                file=image, 
                                user_id=user_id, 
                                name=name, 
                                timestamp=timestamp)

@register.route("/users")
def users():
    rows = []
    with open(os.path.join(current_app.config['REGISTER_IMAGES_FOLDER'], 'registered_users.csv'), 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)
        
        for row in csvreader:
            rows.append(row)

        total_records = csvreader.line_num

    return render_template("users.html", users=rows, total_records=total_records)