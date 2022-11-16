# Train and use a Latte Art Detector on Google Cloud
## With Vertex AI and Cloud Run

Python Flask App that uses Vertex AI AutoML Vision to detect if your latte art is pro or not. 
More info at https://medium.com/@aosterloh34/making-better-coffee-using-artificial-intelligence-f253aa45c0aa


## Steps
1. Get images of latte art
2. Label them into "Beginner" and "Pro" according to your liking in Vertex AI according to 
   https://cloud.google.com/vertex-ai/docs/training-overview
3. Train the model according to the AutoML documentation and create an endpoint
4. Enter the project and end point IDs in the app.py of the flask app
5. Deploy on Cloud Run
6. Make a cappucino 
7. Take a picture and see if you are a pro

![Alt text](coffee.gif?raw=true "Latte Art Detector")
