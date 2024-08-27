# i want to separate the conversion logic into another function
import os
from flask import request, jsonify, send_file, after_this_request
from werkzeug.utils import secure_filename
from utils.utils import validate_file

def pdf_to_psd_route(app):
    @app.route('/api/pdf-to-psd', methods=['POST'])
    def pdf_to_psd_file():
        if 'files' not in request.files:
            return jsonify({"error": "No file provided"}), 400

        files = request.files.getlist('files')
        error = validate_file(files)
        if error:
            return jsonify({"error": error}), 400

        if len(files) != 1:
            return jsonify({"error": "Only one file is supported in this route"}), 400

        pdf_file = files[0]
        filename = secure_filename(pdf_file.filename)
        if not filename.lower().endswith('.pdf'):
            return jsonify({"error": "Only PDF files are supported"}), 400

        temp_input_path = os.path.join('/tmp', filename)
        temp_output_path = os.path.join('/tmp', filename.replace('.pdf', '.psd'))

        try:
            # Save the uploaded PDF file temporarily
            pdf_file.save(temp_input_path)

            # Convert PDF to PSD using ImageMagick
            command = f"convert {temp_input_path} {temp_output_path}"
            os.system(command)

            @after_this_request
            def remove_files(response):
                os.remove(temp_input_path)
                if os.path.exists(temp_output_path):
                    os.remove(temp_output_path)
                return response

            # Send the resulting PSD file
            response = send_file(
                temp_output_path,
                mimetype='image/vnd.adobe.photoshop',
                as_attachment=True,
                download_name='converted_psd.psd'
            )

            response.headers['X-Accel-Buffering'] = 'no'
            response.headers['Cache-Control'] = 'no-cache'
            response.headers['Connection'] = 'close'

            return response

        except Exception as e:
            return jsonify({"error": f"Error during conversion: {str(e)}"}), 500
