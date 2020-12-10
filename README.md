

<!-- PROJECT LOGO -->
<br />
<p align="center">
  
  <img src="https://img.icons8.com/color/80/000000/hips.png"/>
  
  <h1 align="center">My_Guard</h1>

  <p align="center">
    Automated Security Task
    <br />
    <a href="https://github.com/othneildrew/Best-README-Template"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://docs.google.com/document/d/1KF65t9N9TMkO4DHqI02kcHO1DgoCmEi7_cdcJBLKTSE/edit?usp=sharing">View Demo</a>
  </p>
</p>


<p align="center">
  <img src="https://github.com/ADI-KOTKAR/My_Guard/blob/master/images/home.PNG">
</p>

<!-- TABLE OF CONTENTS -->


## Table of Contents

* [About the Project](#about-the-project)
* [Resources](#resources)
* [Getting Started](#getting-started)
* [Workflow](#workflow)
* [Contact](#contact)


<!-- ABOUT THE PROJECT -->
## About The Project


**My_Guard** is built by keeping Automated Security Task in mind. Its a Python-Flask based web application intended to be used in Raspberry Pi Desktop. 
  Its main motive is to assist security services in giving accurate results, allow eligible visitors to enter any society or space and also maintain the logs regarding this.       **My_Guard** being a Web App can installed across any platforms. 

## Resources
1. **Framework** : Flask
- [Flask Documentation (1.1.x)](https://flask.palletsprojects.com/en/1.1.x/)
2. **Database** : *MongoDB Atlas*
- [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
- [Python  MongoDB Tutorial using PyMongo](https://youtu.be/rE_bJl2GAY8)
- [PyMongo - Read the Docs](https://pymongo.readthedocs.io/en/stable/)
3. **AWS  Python SDK - Boto3**
- [Boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- [Amazon S3](https://aws.amazon.com/s3/)
- [Amazon Rekognition](https://aws.amazon.com/rekognition/?blog-cards.sort-by=item.additionalFields.createdDate&blog-cards.sort-order=desc)
- [Amazon CloudWatch](https://aws.amazon.com/cloudwatch/)


<!-- GETTING STARTED -->
## Getting Started
#### Clone the Repo
```
git clone https://github.com/ADI-KOTKAR/My_Guard.git
````

#### Create Free Accounts
Create free accounts of *MongoDB Atlas* and *AWS*. 

####  Python 3 
Install Python 3 in your system. [click here](https://www.python.org/downloads/)

#### Create a Virtual Environment.
- Installing virtualenv package of Python.
```
pip install virtualenv
```
- Creating a virtual environment named 'venv'.
```
virtualenv venv
```
- Activate the environment (Windows).
```
venv\Scripts\activate
```

#### Installing Dependencies in Virtual Environment
- Make sure environment is activated. `(env)`
- Using Requirements File. **(Recommended)**
```
pip install -r requirements.txt
```
- Individually installing packages.
	##### ***Flask | Flask-PyMongo | bcrypt | boto3 | dnspython***
```
pip install Flask Flask-PyMongo bcrypt boto3 dnspython
```
#### File Configuration
1.  Generate AWS **credentials** (csv file) by following this [link](https://www.youtube.com/watch?v=Jtr0gyM9rCI). Create **.env** files in the root directory and the directories shown below.
```
📦app  
 ┣ 📂Enter  
 ┃ ┣ 📂images   
 ┃ ┣ 📂templates   
 ┃ ┣ 📂__pycache__   
 ┃ ┣ 📜.env  
 ┃ ┣ 📜enter.py  
 ┃ ┗ 📜__init__.py  
 ┣ 📂Register  
 ┃ ┣ 📂templates  
 ┃ ┣ 📂__pycache__   
 ┃ ┣ 📜.env  
 ┃ ┣ 📜register.py  
 ┃ ┗ 📜__init__.py 
 ┗ 📜extensions.py
```
Mention the credentials generated in the **.env** file.
```
USER_NAME = your_username
ACCESS_KEY_ID = your_access_key_id
SECRET_ACCESS_KEY = your_secret_access_key
CONSOLE_LOGIN_LINK = your_console_login_link
```
2. Connect your MongoDB Atlas Cluster with your project by getting the  **MONGO_URI** [(Reference link)](https://youtu.be/rE_bJl2GAY8). Create a file named `settings.py` mentioning the uri.
```
import os
MONGO_URI = "your_mongo_uri"
``` 


If you have made it so far then you are genius enough to configure this application for any OS.

#### Running Application
Make sure environment is activated, Now run:
```
python main.py
```
Open the localhost link - [http://127.0.0.1:5000/](http://127.0.0.1:5000/) , this will open the App on your browser.

## Workflow

#### Register Visitor
1.  User sends his name and image through the registration form on application.

2.  After verifying all fields, the image is uploaded on Amazon S3 Bucket

3.  The form details along with timestamp are inserted in the MongoDB Atlas database. A user ID is generated after a successful transaction.

4.  The Amazon CloudWatch sends a snapshot of metrics for monitoring the API request

#### Entry of Visitor

1.  Registered User sends his ID, temperature, entry_type (IN/OUT), and image through the entry form on application.

2.  If temperature is invalid, then the entry is denied, else further details are verified and response is inserted in the database.

3.  If ID is not found (verified from S3 Bucket), then entry is denied, else further details are verified and response is inserted in the database.

4.  If Face is not Recognized (verified from Rekognition), then entry is denied and response is inserted in the database.

5.  If above all conditions are successfully verified then the user is allowed to enter and response is inserted in the database.

6.  The Amazon CloudWatch sends a snapshot of metrics for monitoring the API request.

## Contact




