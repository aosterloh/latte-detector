# Latte Art Detector - 

Python Flask App that uses Vertex AI AutoML Vision to detect if your latte art is pro or not. 

## Steps
1. Get images of latte art
2. Label them into "Beginner" and "Pro" according to your liking in Vertex AI according to 
   https://cloud.google.com/vertex-ai/docs/training-overview
3. Train the model according to the AutoML documentation and create an endpoint
4. Enter the project and end point IDs in the app.py of the flask app
5. Deploy on Cloud Run
6. Make a cappucino 
7. Take a picture and see if you are a pro

![Alt text](ss1.jpeg?raw=true "Latte Art Detector")
