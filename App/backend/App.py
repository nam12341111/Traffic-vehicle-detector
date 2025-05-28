import os
import uuid
import datetime
import cv2

from flask import Flask, request, jsonify, send_from_directory
from flask_bcrypt import Bcrypt
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity
)
from flask_cors import CORS
from flask_pymongo import PyMongo

from ultralytics import YOLO

# === Flask App Setup ===
app = Flask(__name__)
app.config['SECRET_KEY'] = '123'  # Change to a secure key in production
app.config["MONGO_URI"] = "mongodb://localhost:27017/mydatabase"  # Update as needed
app.config['JWT_SECRET_KEY'] = '123' 
CORS(app)

# Initialize PyMongo, Bcrypt, JWT
mongo = PyMongo(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
# sudo systemctl start mongod
# Create folders for storing images
UPLOAD_FOLDER = 'static/uploads'
RESULT_FOLDER = 'static/results'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)


model = YOLO('best.pt')

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'msg': 'Missing username or password'}), 400

    # Check if the username already exists in the "users" collection
    if mongo.db.users.find_one({'username': username}):
        return jsonify({'msg': 'Username already exists'}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    user = {
        'username': username,
        'password': hashed_password
    }
    # Insert the new user into MongoDB
    mongo.db.users.insert_one(user)
    return jsonify({'msg': 'User registered successfully'}), 200

# Login endpoint
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    user = mongo.db.users.find_one({'username': username})
    if user and bcrypt.check_password_hash(user['password'], password):
        # Use the string version of the MongoDB ObjectId as the identity
        access_token = create_access_token(identity=str(user['_id']))
        return jsonify({'access_token': access_token, 'user_id': str(user['_id'])}), 200
    else:
        return jsonify({'msg': 'Bad username or password'}), 401

# Upload and detection endpoint (protected)
@app.route('/api/upload', methods=['POST'])
@jwt_required()
def upload():
    current_user_id = get_jwt_identity()
    if 'image' not in request.files:
        return jsonify({'msg': 'No file part'}), 400
    file = request.files['image']
    if file.filename == '':
        return jsonify({'msg': 'No selected file'}), 400

    # Save the uploaded image
    ext = os.path.splitext(file.filename)[1]
    orig_filename = f"{uuid.uuid4()}{ext}"
    upload_path = os.path.join(UPLOAD_FOLDER, orig_filename)
    file.save(upload_path)

    # Run detection on the saved image using YOLO
    results = model(upload_path)
    img = cv2.imread(upload_path)
    for pred in results[0].boxes:
        x1, y1, x2, y2 = map(int, pred.xyxy[0].cpu().numpy())
        conf = float(pred.conf.cpu().numpy())
        class_id = int(pred.cls.cpu().numpy())
        label = model.names[class_id]
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
        cv2.putText(img, f'{label}: {conf:.2f}', (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    result_filename = "result_" + orig_filename
    result_path = os.path.join(RESULT_FOLDER, result_filename)
    cv2.imwrite(result_path, img)

    # Insert history record in the "history" collection
    history_entry = {
        'original_filename': orig_filename,
        'result_filename': result_filename,
        'timestamp': datetime.datetime.utcnow(),
        'user_id': current_user_id
    }
    mongo.db.history.insert_one(history_entry)

    return jsonify({'msg': 'Image processed successfully', 'result_filename': result_filename}), 200

# History endpoint (protected)
@app.route('/api/history', methods=['GET'])
@jwt_required()
def history():
    current_user_id = get_jwt_identity()
    histories = mongo.db.history.find({'user_id': current_user_id}).sort('timestamp', -1)
    result = []
    for h in histories:
        # Format the timestamp for output
        timestamp = h.get('timestamp')
        if isinstance(timestamp, datetime.datetime):
            timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        else:
            timestamp_str = str(timestamp)
        result.append({
            'id': str(h['_id']),
            'original_filename': h['original_filename'],
            'result_filename': h['result_filename'],
            'timestamp': timestamp_str
        })
    return jsonify(result), 200

# Serving static image files
@app.route('/uploads/<folder>/<filename>')
def serve_file(folder, filename):
    if folder not in ['uploads', 'results']:
        return jsonify({'msg': 'Invalid folder'}), 400
    directory = os.path.join('static', folder)
    return send_from_directory(directory, filename)
# In app.py, after your imports:
from werkzeug.utils import secure_filename

ALLOWED_VIDEO_EXTS = {'.mp4', '.avi', '.mov', '.mkv'}

def allowed_video(filename):
    return os.path.splitext(filename)[1].lower() in ALLOWED_VIDEO_EXTS

@app.route('/api/upload_video', methods=['POST'])
@jwt_required()
def upload_video():
    current_user_id = get_jwt_identity()
    if 'video' not in request.files:
        return jsonify({'msg': 'No file part'}), 400
    file = request.files['video']
    if file.filename == '':
        return jsonify({'msg': 'No selected file'}), 400
    if not allowed_video(file.filename):
        return jsonify({'msg': 'Unsupported video format'}), 400

    # Secure and save the upload
    ext = os.path.splitext(file.filename)[1]
    orig_filename = f"{uuid.uuid4()}{ext}"
    upload_path = os.path.join(UPLOAD_FOLDER, orig_filename)
    file.save(upload_path)

    # Open the video
    cap = cv2.VideoCapture(upload_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Prepare writer for annotated video
    result_filename = f"result_{orig_filename}"
    result_path = os.path.join(RESULT_FOLDER, result_filename)
    
    # Use H.264 codec which is more browser-compatible
    # For .mp4 output, use 'avc1' or 'H264' codec
    if os.path.splitext(result_filename)[1].lower() == '.mp4':
        fourcc = cv2.VideoWriter_fourcc(*'avc1')  # H.264 codec
    else:
        fourcc = cv2.VideoWriter_fourcc(*'XVID')  # Default to XVID for other formats
        
    out = cv2.VideoWriter(result_path, fourcc, fps, (width, height))

    # Process each frame
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        # Run YOLO on the frame
        results = model(frame)  # assuming ultralytics accepts ndarray
        for pred in results[0].boxes:
            x1, y1, x2, y2 = map(int, pred.xyxy[0].cpu().numpy())
            conf = float(pred.conf.cpu().numpy())
            class_id = int(pred.cls.cpu().numpy())
            label = model.names[class_id]
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
            cv2.putText(frame, f'{label}: {conf:.2f}', (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        out.write(frame)

    cap.release()
    out.release()

    # Record history
    history_entry = {
        'original_filename': orig_filename,
        'result_filename': result_filename,
        'timestamp': datetime.datetime.utcnow(),
        'user_id': current_user_id,
        'type': 'video'
    }
    mongo.db.history.insert_one(history_entry)

    return jsonify({
        'msg': 'Video processed successfully',
        'result_filename': result_filename
    }), 200

# Add a new route to serve video files with the correct MIME type
# Add this after your existing routes:

@app.route('/api/video/<filename>')
def serve_video(filename):
    """Serve video files with the correct MIME type"""
    video_path = os.path.join(RESULT_FOLDER, filename)
    if not os.path.exists(video_path):
        return jsonify({'msg': 'Video not found'}), 404
        
    # Determine MIME type based on extension
    ext = os.path.splitext(filename)[1].lower()
    mime_type = 'video/mp4'  # Default to MP4
    if ext == '.avi':
        mime_type = 'video/x-msvideo'
    elif ext == '.mov':
        mime_type = 'video/quicktime'
    elif ext == '.mkv':
        mime_type = 'video/x-matroska'
        
    return send_from_directory(RESULT_FOLDER, filename, mimetype=mime_type)

if __name__ == '__main__':
    app.run(debug=True)
