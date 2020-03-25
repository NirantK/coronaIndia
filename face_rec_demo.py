# from https://www.codepile.net/pile/ZJO0Gwaj

# Python packages required: face_recognition, flask 
# Requires cmake. On mac `brew install cmake` 
# Package works on dlib
# curl -XPOST -F "file=@/Users/maneesh/Downloads/obama.jpg" http://127.0.0.1:5001
# {
#   "face_found_in_image": true
# }
# TODO: Batch run
# TODO: Resize image


import face_recognition
from flask import Flask, jsonify, request, redirect
import json
import glob

# files = glob.glob("/Users/maneesh/Projects/covid/face_recognition/lfw/*.jpg")


app = Flask(__name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_image():
    # Check if a valid image file was uploaded
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            return redirect(request.url)

        if file and allowed_file(file.filename):
            # The image file seems valid! Detect faces and return the result.
            return detect_face(file)

    # If no valid image file was uploaded, show the file upload form:
    return '''
    <!doctype html>
    <title>Covid Face Detection Demo</title>
    <h1>Upload a picture and check if it's a face.</h1>
    <form method="POST" enctype="multipart/form-data">
      <input type="file" name="file">
      <input type="submit" value="Upload">
    </form>
    '''


def detect_face(file):
    if request.method == 'POST':
        img = face_recognition.load_image_file(file)
        unknown_face_encodings = face_recognition.face_encodings(img)
        face_found = True if len(unknown_face_encodings)>0 else False
        result = {
        "face_found_in_image": face_found
    }        
    return jsonify(result)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)
