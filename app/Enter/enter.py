import boto3
import botocore
import csv
from csv import writer
import os
import shutil
import time
import datetime
from dotenv import load_dotenv
from flask import Blueprint, current_app, render_template, url_for, redirect, request, session, flash
from werkzeug.utils import secure_filename

enter = Blueprint("enter",  __name__, static_folder="images", template_folder="templates")

@enter.route("/")
def enter_details():
    return render_template("enter_details.html")

@enter.route("/form-result", methods=['POST','GET'])
def enter_form_details():
    if request.method == 'POST':
        user_id = request.form['id']
        _type = request.form['type']

        temp = request.form['temp']
        if float(temp) > 97 and float(temp) < 99.5:
            temp_validity = True
        else:
            temp_validity = False
        
        if 'file' not in request.files:
            flash('No image found')
        file = request.files['image']
        
        if file.filename == '':
            flash('No image selected')
                
        if file and temp_validity:
            load_dotenv()
            timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
            image = str(user_id)+"_upload"+".jpg"
            
            # Check if ID exists
            s3 = boto3.resource('s3',
                            aws_access_key_id = os.getenv("ACCESS_KEY_ID"),
                            aws_secret_access_key = os.getenv("SECRET_ACCESS_KEY"),
                            region_name='us-east-2')
            try:
                s3.Object('adis-aws-bucket', str(user_id+".jpg")).load()
            except botocore.exceptions.ClientError as e:
                if e.response['Error']['Code'] == "404":
                    # The object does not exist.
                    IDExists = False
                else:
                    # Something else has gone wrong.            
                    raise e
            else:
                # The object does exist.
                IDExists = True

            # Facial Recognition
            if IDExists:
                filename = secure_filename(str(user_id)+"_upload"+".jpg")
                file.save(os.path.join(current_app.config['ENTER_IMAGES_FOLDER'], filename))

                client = boto3.client('rekognition',
                                        aws_access_key_id = os.getenv("ACCESS_KEY_ID"),
                                        aws_secret_access_key = os.getenv("SECRET_ACCESS_KEY"),
                                        region_name='us-east-2')

                with open(os.path.join(current_app.config['ENTER_IMAGES_FOLDER'], filename), 'rb') as source_image:
                    source_bytes = source_image.read()

                compare_img = str(user_id+".jpg")
                response = client.compare_faces(
                    SourceImage={
                        'Bytes': source_bytes
                    },
                    TargetImage={
                        'S3Object': {
                            'Bucket': 'adis-aws-bucket',
                            'Name': compare_img
                        }
                    }
                )

                for key, value in response.items():
                    if key in ('FaceMatches'):
                        if len(value) == 0:
                            Recognition = False

                        for att in value:
                            if att['Similarity'] > 95:
                                Recognition = True
                                 #Writing in CSV
                                with open(os.path.join(current_app.config['ENTER_IMAGES_FOLDER'], 'entry_records.csv'), 'a+', newline='') as write_obj2:
                                    csv_writer2 = writer(write_obj2)
                                    csv_writer2.writerow([user_id, temp, timestamp, _type])

                            else:
                                Recognition = False    
            else:
                Recognition = False 
        
        else:
            IDExists = False
            Recognition = False
            timestamp = None
        
        result = request.form

        return render_template( "enter_form-result.html",
                                result = result, 
                                file=str(user_id)+"_upload"+".jpg", 
                                user_id=user_id, 
                                temp=temp, 
                                type=_type,
                                temp_validity=temp_validity,
                                IDExists=IDExists, 
                                Recognition=Recognition, 
                                timestamp=timestamp)

@enter.route("/records")
def users():
    rows = []
    with open(os.path.join(current_app.config['ENTER_IMAGES_FOLDER'], 'entry_records.csv'), 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)
        
        for row in csvreader:
            rows.append(row)

        total_records = csvreader.line_num

    return render_template("records.html", records=rows, total_records=total_records)