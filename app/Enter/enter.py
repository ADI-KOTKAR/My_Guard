import boto3
import botocore
import csv
import os
import shutil
import time
import datetime
from dotenv import load_dotenv
from flask import Blueprint, current_app, render_template, url_for, redirect, request, session, flash
from werkzeug.utils import secure_filename
from ..extensions import mongo

enter = Blueprint("enter",  __name__, static_folder="images", template_folder="templates")

'''
Status codes:
0 - Invalid Temperature
1 - User Not Found
2 - Face Not Recognized
3 - All Details Verified
'''

@enter.route("/")
def enter_details():
    return render_template("enter_details.html")

@enter.route("/form-result", methods=['POST','GET'])
def enter_form_details():
    if request.method == 'POST':
        user_id = request.form['id']
        _type = request.form['type']
        temp = request.form['temp']
        timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')

        # DB connection
        records_collection = mongo.db.records
        find_user = list(mongo.db.users.find({"mg_id":user_id}))
        if len(find_user) == 0:
                name = None
        else:
            for x in find_user:
                name = x['name']

        # 0 - Invalid Entry
        record_entry = {
                "mg_id": user_id,
                "name": name,
                "temperature": temp,
                "type": _type,
                "timestamp": timestamp,
                "status": "",
                "status_code": None 
            }

        if float(temp) > 97 and float(temp) < 99.5:
            temp_validity = True
        else:
            temp_validity = False
            # 0 - Invalid Temperature
            record_entry['status'] = "Denied: Invalid Temperature"
            record_entry['status_code'] = 0
            records_collection.insert_one(record_entry)
        
        if 'file' not in request.files:
            flash('No image found')
        file = request.files['image']
        
        if file.filename == '':
            flash('No image selected')
                
        if file and temp_validity:
            load_dotenv()
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
                                # 3 - Success
                                record_entry['status'] = "Allowed: All Details Verified"
                                record_entry['status_code'] = 3
                                records_collection.insert_one(record_entry)
                            else:
                                Recognition = False 

                        if not Recognition:
                            # 2 - Face not recognized
                            record_entry['status'] = "Denied: Face Not Recognized"
                            record_entry['status_code'] = 2
                            records_collection.insert_one(record_entry)   
            else:
                Recognition = False
                # 1 - User not found 
                record_entry['status'] = "Denied: User Not Found"
                record_entry['status_code'] = 1
                records_collection.insert_one(record_entry)
        
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
    # Mongo DB Atlas - Records
    results = mongo.db.records.find({})
    return render_template("records.html", results=results)