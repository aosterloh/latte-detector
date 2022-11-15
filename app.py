from flask import Flask, flash, request, redirect, url_for, render_template
import urllib.request
from google.cloud import storage
import os
from google.cloud import vision
import io
import base64
from google.cloud import aiplatform
from google.cloud.aiplatform.gapic.schema import predict
from werkzeug.utils import secure_filename
from PIL import Image
 
app = Flask(__name__)
 
UPLOAD_FOLDER = 'static/uploads/'
 
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
 
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
img  = Image.new( mode = "RGB", size = (300, 300) )
 
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def isCoffee(fullpath):
    print("Is image even coffee?")
    client = vision.ImageAnnotatorClient()
    file_name = os.path.abspath(fullpath)
    coffee = ["tableware", "Espressino", "Flat white", "Drinkware", "Cortado", "Coffee", "Dishware" ]
    isCoffee = False

    # Loads the image into memory
    with io.open(file_name, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    # Performs label detection on the image file
    response = client.label_detection(image=image)
    labels = response.label_annotations

    for label in labels:
        #print(label.description)
        if label.description in coffee:
            print("Is Coffee: ", label.description)
            isCoffee = True
            break
    print("Is it coffee? ", str(isCoffee))
    return isCoffee

def cleanup():
    print("deleting old uploads") # get rid of local image storage next
    path = 'static/uploads/'
    for file_name in os.listdir(path):
        f = path + file_name
        print("Deleting ", f)
        if os.path.isfile(f):
            print('Deleting file:', f)
            os.remove(f)
    print("Delete done")


def upload_blob(path,file):
    """Uploads a file to the bucket."""
    print("Uploading to GCS....")
    # The ID of your GCS bucket
    bucket_name = "latte-learning"
    # The ID of your GCS object
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file)
    blob.upload_from_filename(path)
    print("Done upload")


def resize(file):
    fn = "static/uploads/" + file
    print("resizing image")
    image = Image.open(fn)  
    image.thumbnail((1200,1200))
    image.save(fn)

def predict_image_classification_sample(
    project: str,
    endpoint_id: str,
    filename: str,
    location: str,
    api_endpoint: str,    
):
    print("Prediction call")
    # The AI Platform services require regional API endpoints.
    client_options = {"api_endpoint": api_endpoint}
    # Initialize client that will be used to create and send requests.
    # This client only needs to be created once, and can be reused for multiple requests.
    client = aiplatform.gapic.PredictionServiceClient(client_options=client_options)
    with open(filename, "rb") as f:
        file_content = f.read()

    # The format of each instance should conform to the deployed model's prediction input schema.
    encoded_content = base64.b64encode(file_content).decode("utf-8")
    instance = predict.instance.ImageClassificationPredictionInstance(
        content=encoded_content,
    ).to_value()
    instances = [instance]
    # See gs://google-cloud-aiplatform/schema/predict/params/image_classification_1.0.0.yaml for the format of the parameters.
    parameters = predict.params.ImageClassificationPredictionParams(
        confidence_threshold=0.5, max_predictions=5,
    ).to_value()
    endpoint = client.endpoint_path(
        project=project, location=location, endpoint=endpoint_id
    )
    response = client.predict(
        endpoint=endpoint, instances=instances, parameters=parameters
    )
    #print("response")
    #print(" deployed_model_id:", response.deployed_model_id)
    # See gs://google-cloud-aiplatform/schema/predict/prediction/image_classification_1.0.0.yaml for the format of the predictions.
    predictions = response.predictions
    for prediction in predictions:
        pred = dict(prediction)
        result = pred["displayNames"]
    prediction=result[0]
    print("Result of prediction call: ", prediction )
    return prediction
 
@app.route('/')
def home():
    cleanup()
    print("Render index.html")
    flash ("init")
    return render_template('index.html')
 
@app.route('/result', methods=['POST'])
def upload_image():
    print("??????aost Post")
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
 
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        print('upload_image filename: ' + filename)
        fn = "static/uploads/" + filename
        
        resize(filename)
        
        if isCoffee(fn) == False:
            message = "NotCoffee"
            print("Not Coffee")
        else:
            print("Prediction Call....")
            skill = predict_image_classification_sample(
            project="78********",
            endpoint_id="871************",
            location="europe-west4",
            filename=fn,
            api_endpoint="europe-west4-aiplatform.googleapis.com")
            
            upload_blob(fn,filename)
            message = 'Your barista Skill level is: ' + skill
            print("Your barista Skill level is: ", skill)
    
        flash(message)
        return render_template('result.html')
    else:
        #flash('Allowed image types are - png, jpg, jpeg, gif')
        return redirect(request.url)
 
@app.route('/display/<filename>')
def display_image(filename):
    print('display_image filename: ' + filename)
    return redirect(url_for('static', filename='uploads/' + filename), code=301)
 
if __name__ == "__main__":
    app.run(port=int(os.environ.get("PORT", 8080)),host='0.0.0.0',debug=True)
