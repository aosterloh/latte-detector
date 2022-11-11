
# Replace endpoint and project ID below

from flask import Flask, flash, request, redirect, url_for, render_template
import urllib.request
import os
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
 
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def cleanup():
    path = 'static/uploads'
    for file_name in os.listdir(path):
        f = path + file_name
        if os.path.isfile(f):
            print('Deleting file:', f)
            os.remove(f)
         
         
# resize as vertex ai does not like files over 1.5MB
def resize(im):
    fn = "static/uploads/" + im
    print("fn")
    image = Image.open(fn)  
    h, w = image.size
    #flash(w)
    #flash(h)
    if (h > 800) or (w > 800):
        aspect_ratio = h/w
        new_w = 800
        new_h = (new_w * aspect_ratio)
        new_h = int(new_h)
        flash("Resizing")
        newsize = (new_w, new_h)
        resize = image.resize(newsize, Image.LANCZOS)
        resize.save(fn)

def predict_image_classification_sample(
    project: str,
    endpoint_id: str,
    filename: str,
    location: str,
    api_endpoint: str,    
):
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

    return result[0]
 
@app.route('/')
def home():
    cleanup()
    return render_template('index.html')
 
@app.route('/', methods=['POST'])
def upload_image():
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
        # Replace endpoint and project ID
        skill = predict_image_classification_sample(
        project="7803*******",
        endpoint_id="871602*******",
        location="europe-west4",
        filename=fn,
        api_endpoint="europe-west4-aiplatform.googleapis.com")

        message = 'Your barista Skill level is: ' + skill
        flash(message)
        return render_template('index.html', skill=skill)
    else:
        #flash('Allowed image types are - png, jpg, jpeg, gif')
        return redirect(request.url)
 
@app.route('/display/<filename>')
def display_image(filename):
    print('display_image filename: ' + filename)
    return redirect(url_for('static', filename='uploads/' + filename), code=301)
 
if __name__ == "__main__":
    app.run(port=int(os.environ.get("PORT", 8080)),host='0.0.0.0',debug=True)
