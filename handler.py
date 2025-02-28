from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# Define the upload folder and allowed extensions
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'mp4', 'txt'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if the file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def handle_photo(file):
    """Function to handle photo uploads."""
    # Save the file or process it as needed
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)
    return f"Photo saved at {file_path}"

def handle_video(file):
    """Function to handle video uploads."""
    # Save the file or process it as needed
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)
    return f"Video saved at {file_path}"

def handle_text_file(file):
    """Function to handle text file uploads."""
    # Read the text content
    text_content = file.read().decode('utf-8')
    return f"Text file content received: {text_content}"

def handle_text_input(text):
    """Function to handle raw text input."""
    return f"Text input received: {text}"

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' in request.files:
        # Handle file upload
        file = request.files['file']

        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        if file and allowed_file(file.filename):
            file_extension = file.filename.rsplit('.', 1)[1].lower()

            if file_extension in {'png', 'jpg', 'jpeg'}:
                result = handle_photo(file)
            elif file_extension == 'mp4':
                result = handle_video(file)
            elif file_extension == 'txt':
                result = handle_text_file(file)
            else:
                return jsonify({"error": "Unsupported file type"}), 400

            return jsonify({"message": result}), 200

        return jsonify({"error": "File type not allowed"}), 400

    elif 'text' in request.form:
        # Handle text input
        text = request.form['text']
        if text.strip():
            result = handle_text_input(text)
            return jsonify({"message": result}), 200
        else:
            return jsonify({"error": "Text input is empty"}), 400

    else:
        return jsonify({"error": "No file or text input provided"}), 400

if __name__ == '__main__':
    app.run(debug=True)