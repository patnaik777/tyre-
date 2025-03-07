from flask import Flask, render_template, request, jsonify
import requests
import os
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials
from azure.core.credentials import AzureKeyCredential

from PIL import Image
import sys
import time
import io

app = Flask(__name__)

# Set your Azure API endpoint and key
# subscription_key
# key ='4NKCq3onAuwguIMidkZm9tKE6ePcbBTkoZzSPlngQoybVq1gYnRAJQQJ99BBACGhslBXJ3w3AAAFACOGksB1' 
# endpoint = 'https://twvision.cognitiveservices.azure.com/'

# Initialize Azure Computer Vision client
#credential = AzureKeyCredential(key)
# client = ImageAnalysisClient(endpoint=endpoint, credential=credential)

# client = ComputerVisionClient(endpoint, AzureKeyCredential(key))

# Azure Cognitive Services subscription key and endpoint
subscription_key = '4NKCq3onAuwguIMidkZm9tKE6ePcbBTkoZzSPlngQoybVq1gYnRAJQQJ99BBACGhslBXJ3w3AAAFACOGksB1'
endpoint = 'https://twvision.cognitiveservices.azure.com/'

# Initialize the ComputerVisionClient
client =  ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))

# Set the upload folder
app.config['UPLOAD_FOLDER'] = 'uploads'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_image():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400
        file = request.files['file']
        
        # Check if the file has a valid name and extension
        # if file.filename == '' or not allowed_file(file.filename):
        #     return jsonify({"error": "Invalid file format"}), 400
        
        # Secure the filename
        # print('hehe ---> ', secure_filename(file.filename))
        filename = file.filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Save the file to the specified directory
        file.save(file_path)

        # Open the image using PIL
        try:
            image = Image.open(file_path)
            # You can process the image here (e.g., run OCR, etc.)
            # For example, if you are using Azure OCR or other processing:
            extracted_text = ocr_processing(image)  # Your custom OCR function to process the image
            print('extracted text ---> ',extracted_text)
            return jsonify({"extracted_text": extracted_text})
        except Exception as e:
            return jsonify({"error": f"Error processing the image: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

# Example OCR function (you need to implement OCR, this is a placeholder)
def ocr_processing(image):
    # Placeholder for image processing (e.g., Azure OCR)
    # You9 would implement the actual OCR code to extract text from the image
    try:
        print('Saving image as temp_image.jpg')  # Debugging line
        image_path = "temp_image.jpg"
        image.save(image_path)

        print('hehe 1', image_path)
         # Initialize extracted_text as an empty string
        extracted_text = ""
        with open(image_path, "rb") as image_file:
            # Call API with local image and raw response (allows you to get the operation location)
            print('hehe 2')
            read_response = client.read_in_stream(image_file, raw=True)

            # Get the operation location (URL with an ID at the end) from the response
            read_operation_location = read_response.headers["Operation-Location"]
            # Grab the ID from the URL
            print('read_operation_location ---> ', read_operation_location)
            operation_id = read_operation_location.split("/")[-1]

            # Call the "GET" API and wait for it to retrieve the results 
            while True:
                read_result = client.get_read_result(operation_id)
                if read_result.status not in ['notStarted', 'running']:
                    break
                time.sleep(1)

            # Print the detected text, line by line
            print('read_result ---> ', read_result)
            if read_result.status == OperationStatusCodes.succeeded:
                for text_result in read_result.analyze_result.read_results:
                    for line in text_result.lines:
                        print('line ---> ' ,line)
                        print(line.text)
                        extracted_text += line.text
                        print(line.bounding_box)
            else:
                print(f"Failed to process {image}. Status: {read_result.status}")

        return extracted_text

    except Exception as e:
        print(f"Error processing image: {str(e)}")
        return "Error processing image."

    # return "Extracted text from the image."

if __name__ == '__main__':
    app.run(debug=True)