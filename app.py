from flask import Flask, render_template, request, Response, send_from_directory, redirect, url_for, send_file,jsonify
import os
import time
from PIL import Image
import shutil
import os
import sys
import ctypes
import subprocess
import zipfile
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import DateRange, Dimension, Metric, RunReportRequest
import hashlib
from joblib import load
from werkzeug.utils import secure_filename
from network_model import predict_attack
from malware_model import predict_malware, get_file_hash, predict_from_hash
import joblib

app = Flask(__name__)

restoration_active = False  # Control flag for restoration
restored_folder = 'restored_files'

# Create restored folder if not existing
if not os.path.exists(restored_folder):
    os.makedirs(restored_folder)

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# Function to create a simple placeholder image using Pillow
def create_placeholder_image(file_path):
    img = Image.new('RGB', (100, 100), color='red')
    for i in range(100):
        for j in range(100):
            img.putpixel((i, j), (255, 0, 0) if (i+j) % 10 == 0 else (0, 255, 0))
    img.save(file_path, 'JPEG')

# Function to recover JPEG files from a drive
def recover_jpg_files(drive):
    size = 512  # Size of bytes to read
    offs = 0  # Offset location
    drec = False  # Recovery mode
    rcvd = 0  # Recovered file ID
    current_file = None

    # File signatures for different formats
    file_signatures = {
        b'\xff\xd8\xff\xe0': 'jpg',  # JPEG
    b'\x89\x50\x4e\x47\x0d\x0a\x1a\x0a': 'png',  # PNG
    b'\x25\x50\x44\x46': 'pdf',  # PDF
    b'\x7B\x5C\x72\x74\x66': 'rtf',  # RTF
    b'\x52\x61\x72\x21\x1A\x07\x00': 'rar',  # RAR Archive
    b'\x37\x7A\xBC\xAF\x27\x1C': '7z',  # 7-Zip Archive
    b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1': 'msi',  # Windows Installer
        
    }

    with open(drive, "rb") as fileD:
        byte = fileD.read(size)

        while byte:
            for signature, ext in file_signatures.items():
                found = byte.find(signature)
                if found >= 0:
                    drec = True
                    print(f'==== Found {ext.upper()} at location: ' + str(hex(found + (size * offs))) + ' ====')
                    
                    # Open a new file to save the recovered data
                    file_path = os.path.join(restored_folder, f"{rcvd}.{ext}")
                    current_file = open(file_path, "wb")
                    current_file.write(byte[found:])
                    
                    while drec:
                        byte = fileD.read(size)
                        if not byte:
                            break
                        
                        # Check if another signature starts within the block
                        next_signature_found = False
                        for next_signature, next_ext in file_signatures.items():
                            next_found = byte.find(next_signature)
                            if next_found >= 0:
                                current_file.write(byte[:next_found])
                                print(f'==== Wrote {ext.upper()} to {rcvd}.{ext} ====\n')
                                drec = False
                                rcvd += 1
                                current_file.close()
                                fileD.seek((offs + 1) * size)
                                next_signature_found = True
                                break
                        
                        if not next_signature_found:
                            current_file.write(byte)

            byte = fileD.read(size)
            offs += 1

# Function to get Google Analytics report
def get_analytics_report():
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'static\service_account.json'

    from google.analytics.data_v1beta import BetaAnalyticsDataClient
    from google.analytics.data_v1beta.types import (
        DateRange,
        Dimension,
        Metric,
        RunReportRequest,
    )
    property_id = "457343596"  # Replace with your Google Analytics 4 property ID

    client = BetaAnalyticsDataClient()

    request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[Dimension(name="city")],
        metrics=[Metric(name="activeUsers")],
        date_ranges=[DateRange(start_date="2020-03-31", end_date="today")],
    )
    response = client.run_report(request)
    
    report_data = []
    for row in response.rows:
        report_data.append({
            'city': row.dimension_values[0].value,
            'active_users': row.metric_values[0].value
        })
    return report_data

@app.route('/scan_files', methods=['POST'])
def scan_files():
    if 'files' not in request.files:
        return jsonify({'success': False, 'message': 'No file part in the request.'})

    uploaded_files = request.files.getlist('files')
    results = []

    for file in uploaded_files:
        # Save the file temporarily
        file_path = os.path.join('uploads', secure_filename(file.filename))
        file.save(file_path)

        # Predict whether it's malware based on file hash or file contents
        prediction = predict_from_hash(file_path, data, model, scaler)
        results.append({
            'file': file.filename,
            'prediction': prediction
        })

    return jsonify({'success': True, 'message': results})

@app.route('/malware_analysis', methods=['GET', 'POST'])
def malware_analysis():
    model = joblib.load('malware_model.joblib')
    scaler = joblib.load('scaler.joblib')
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'result': 'No file part'})
        file = request.files['file']
        if file.filename == '':
            return jsonify({'result': 'No selected file'})
        if file:
            # Save the file
            file_path = f'uploads/{file.filename}'
            file.save(file_path)

            # Predict malware based on file
            result = predict_from_hash(file_path, model, scaler)
            return jsonify({'result': result})

    return render_template('malware_analysis.html')

# Configure upload folder
UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/network_analysis')
def network_trafficking():
    return render_template('network_trafficking.html')

@app.route('/network_analysis', methods=['POST'])
def network_analysis():
    # Handle file upload
    if 'file' not in request.files:
        return jsonify({'result': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'result': 'No selected file'}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    # Run prediction model on the uploaded file
    result = predict_attack(filepath)

    return jsonify({'result': result})

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analysis')
def analysis():
    return render_template('analysis.html')

# @app.route('/malware_analysis')
# def malware_analysis():
#     return render_template('malware_analysis.html')

@app.route('/recover_files')
def recover_files():
    return render_template('recover_files.html')

@app.route('/network_forensics')
def network_forensics():
    return render_template('network_forensics.html')

@app.route('/website_trafficking')
def website_trafficking():
    return render_template('website_trafficking.html')

@app.route('/start_restore', methods=['GET'])
def start_restore():
    global restoration_active
    drive = request.args.get('drive', 'D')  # Get drive from request
    restoration_active = True  # Activate restoration process

    def restore_files():
        yield "Restoration started...<br>"
        for message in recover_jpg_files(f"\\\\.\\{drive}:"):  # Call the recovery function with the drive
            yield message
        yield "Restoration completed successfully.<br>"

    return Response(restore_files(), mimetype='text/event-stream')

@app.route('/stop_restore', methods=['POST'])
def stop_restore():
    global restoration_active
    restoration_active = False
    return "Restoration process stopped."

@app.route('/images/<filename>')
def get_image(filename):
    return send_from_directory(restored_folder, filename)

@app.route('/download_all', methods=['GET'])
def download_all():
    zip_filename = 'recovered_images.zip'
    zip_filepath = os.path.join(restored_folder, zip_filename)
    
    # Create the ZIP file containing all restored images
    with zipfile.ZipFile(zip_filepath, 'w') as zipf:
        for root, dirs, files in os.walk(restored_folder):
            for file in files:
                if file != zip_filename:  # Avoid zipping the ZIP file itself
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, arcname=file)  # Write each file into the ZIP archive

    # Return the ZIP file for download
    return send_file(zip_filepath, as_attachment=True)

if __name__ == '__main__':
    if is_admin():
        # Run the Flask app if the script has admin privileges
        app.run(debug=True)
    else:
        # Re-run the script with admin rights
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, ' '.join(sys.argv), None, 1)
