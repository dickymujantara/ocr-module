from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
import pytesseract
import cv2
import re

# --- this command just for running in windows ---
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"
# --- this command just for running in windows ---

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def ocr_scan(filename):
    path_file = os.path.join("./uploads/", filename)
    img_cv = cv2.imread(path_file)
    img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
    ocr_processing = pytesseract.image_to_string(img_rgb)
    return ocr_processing


def clearing_text(data):
    filter_data = list(filter(None, data))
    temp_data = []
    for text in filter_data:
        text = re.sub("[$&+,:;=?@#|'<>.^*()%_!-]", "", text.strip())
        if text != "" and text is not None and len(text) > 0:
            temp_data.append(text)
    return temp_data


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route('/file-upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        resp = jsonify({'message': 'No file part in the request'})
        resp.status_code = 400
        return resp
    file = request.files['file']

    if file.filename == '':
        resp = jsonify({'message': 'No file selected for uploading'})
        resp.status_code = 400
        return resp

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        path_file = os.path.join("./uploads/", filename)
        file.save(path_file)
        result_scan = ocr_scan(filename)
        arr_result = result_scan.rsplit("\n")
        arr_result = clearing_text(arr_result)
        resp = jsonify({
            'raw_text': result_scan,
            'arr_text': arr_result
        })
        resp.status_code = 200
        os.remove(path_file)
        return resp
    else:
        resp = jsonify({'message': 'Allowed file types are png, jpg, jpeg'})
        resp.status_code = 500
        return resp


if __name__ == "__main__":
    app.run(debug=True, port=5000)
