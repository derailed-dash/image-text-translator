"""
Application: image-text-translator
Author: Darren Lester

Functions:
    extract_and_translate(request):
        Extract and translate the text from an image.
        The image can be POSTed in the request, or it can be a GCS object reference.
        Test with:
        > functions-framework --target extract_and_translate --debug
        > curl -X GET localhost:8080 -H "Content-Type: application/json" -d '{"bucket":"Bob", "filename":"Whatevs"}'
        > curl -X POST localhost:8080 -H "Content-Type: multipart/form-data" -F "uploaded=@/home/path/to/image.jpg"

    detect_text(image: vision.Image)
        Extract the text from the Image object.
        
    translate_text(message: dict):
        Translate the text from the specified source language to target (default 'en').
"""

import flask
from html import unescape

# https://github.com/GoogleCloudPlatform/functions-framework-python
import functions_framework

from google.cloud import storage
from google.cloud import translate_v2 as translate
from google.cloud import vision

vision_client = vision.ImageAnnotatorClient()
translate_client = translate.Client()
storage_client = storage.Client()

def extract_and_translate(request) -> None:
    """Extract and translate the text from an image.
    The image can be POSTed in the request, or it can be a GCS object reference.
    
    If a POSTed image, enctype should be multipart/form-data and the file should be named 'uploaded'.
    If we're passing a GCS object reference, content-type should be 'application/json', 
    with two attributes:
    - bucket: name of GCS bucket in which the file is stored.
    - filename: name of the file to be read.
    """

    # Check if the request method is POST
    if request.method == 'POST': 
        # Get the uploaded file from the request
        uploaded = request.files.get('uploaded')  # Assuming the input filename is 'uploaded'
        print(f"{uploaded=}")

        if uploaded: # Process the uploaded file
            file_contents = uploaded.read()  # Read the file contents
            image = vision.Image(content=file_contents)
        else:
            raise ValueError("Unable to read uploaded file")
    else:
        # If we haven't created this, then get it from the bucket instead
        content_type = request.headers.get('content-type', 'null')
        if content_type == 'application/json':
            bucket = request.json.get('bucket', None)
            filename = request.json.get('filename', None)
            print(f"Received {bucket=}, {filename=}")            
        else:
            raise ValueError("Unknown content type: {}".format(content_type))
        
        if bucket:
            image = vision.Image(source=vision.ImageSource(gcs_image_uri=f"gs://{bucket}/{filename}"))
        
    # Use the Vision API to extract text from the image
    detected = detect_text(image)
    if detected:
        translated = translate_text(detected)
        if translated["text"] != "":
            print(translated)
            return translated
    
    return "No text found in the image."

def detect_text(image: vision.Image) -> dict | None:
    """Extract the text from the Image object """
    text_detection_response = vision_client.text_detection(image=image)
    annotations = text_detection_response.text_annotations

    if annotations:
        text = annotations[0].description
    else:
        text = ""
    print(f"Extracted text from image:\n{text}")

    # Returns language identifer in ISO 639-1 format. E.g. en.
    # See https://en.wikipedia.org/wiki/List_of_ISO_639_language_codes
    detect_language_response = translate_client.detect_language(text)
    src_lang = detect_language_response["language"]
    print(f"Detected language: {src_lang}.")

    message = {
        "text": text,
        "src_lang": src_lang,
    }

    return message
        
@functions_framework.cloud_event
def translate_text(message: dict) -> None:
    """
    Translates the text in the message from the specified source language
    to the requested target language, then sends a message requesting another
    service save the result.
    """

    text = message["text"]
    src_lang = message["src_lang"]
    to_lang = "en"

    translated = { # before translating
        "text": text,
        "src_lang": src_lang,
        "to_lang": to_lang,
    }
    
    if src_lang != to_lang and src_lang != "und":
        print(f"Translating text into {to_lang}.")
        translated_text = translate_client.translate(
                text, target_language=to_lang, source_language=src_lang)

        translated = {
            "text": unescape(translated_text["translatedText"]),
            "src_lang": src_lang,
            "to_lang": to_lang,
        }
    else:
        print("No translation required.")
    
    return translated

@functions_framework.http
def hello(request: flask.Request):
    """ 
    Test with:
      > functions-framework --target hello --debug
      > curl localhost:8080
    """
    return "Hello world!"