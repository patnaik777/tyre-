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
        print('file.filename ---> ',file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        print('file_path ---> ',file_path)

        
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

        with open(image_path, "rb") as image_stream:
            print("Sending image for OCR processing...")  # Debugging line
            poller = client.recognize_printed_text_in_stream(image_stream, language="en")
            print('poller ---> ', poller)
            result = poller.result()

        # Collect extracted text
        extracted_text = ""
        for page in result.analyze_result.read_results:
            for line in page.lines:
                extracted_text += line.text + "\n"

        print("Extracted Text: ", extracted_text)  # Debugging line

        # Clean up the temporary file
        os.remove(image_path)

        if not extracted_text.strip():
            print("No text found in the image.")  # Debugging line
            return "No text found in the image."

        return extracted_text

    except Exception as e:
        print(f"Error processing image: {str(e)}")
        return "Error processing image."

    # return "Extracted text from the image."

if __name__ == '__main__':
    app.run(debug=True)
