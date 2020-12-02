import csv
import os
import boto3
import time
from datetime import date
from dotenv import load_dotenv
from flask import Flask, render_template
from app.Register.register import register
from app.Enter.enter import enter
from app.extensions import mongo

REGISTER_IMAGES_FOLDER =  'app\\Register\\images'
ENTER_IMAGES_FOLDER = 'app\\Enter\\images'
METRICS_FOLDER = 'metrics'

app = Flask(__name__, static_folder = "metrics")
app.secret_key = "base1234"
app.config['REGISTER_IMAGES_FOLDER'] = REGISTER_IMAGES_FOLDER
app.config['ENTER_IMAGES_FOLDER'] = ENTER_IMAGES_FOLDER
app.config['METRICS_FOLDER'] = METRICS_FOLDER
app.config.from_object('settings')
app.register_blueprint(register, url_prefix="/register")
app.register_blueprint(enter, url_prefix="/enter")

mongo.init_app(app)

@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/metrics")
def metrics():
    # AWS Cloudwatch
    metric_json = '{'\
        '"view": "timeSeries",'\
        '"stacked": true,'\
        '"metrics": ['\
        '    [ "AWS/Rekognition", "SuccessfulRequestCount" ],'\
        '    [ ".", "ResponseTime", "Operation", "CompareFaces", { "accountId": "058981865517" } ]'\
        '],'\
        '"legend": {'\
        '    "position": "bottom"'\
        '},'\
        '"yAxis": {'\
        '    "left": {'\
        '        "showUnits": true'\
        '    }'\
        '},'\
        '"setPeriodToTimeRange": true,'\
        '"width": 1263,'\
        '"height": 250,'\
        '"start": "-P1D",'\
        '"end": "P0D"'\
    '}'

    load_dotenv()
    client = boto3.client('cloudwatch',
                        aws_access_key_id = os.getenv("ACCESS_KEY_ID"),
                        aws_secret_access_key = os.getenv("SECRET_ACCESS_KEY"),
                        region_name='us-east-2')

    response = client.get_metric_widget_image(
        MetricWidget=metric_json
    )

    filename = "metrics_graph_"+str(time.time())+".jpg"

    with open(os.path.join(app.config['METRICS_FOLDER'], filename), "wb") as fh:
        fh.write(response['MetricWidgetImage'])

    return render_template("metrics.html", timestamp=date.today().strftime("%B %d, %Y"), filename=filename)


if __name__ == "__main__":
    app.run(debug=True)
