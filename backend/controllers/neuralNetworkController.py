from flask import Blueprint, request, jsonify
from schemas.fileSchema import validate_image_upload
from services.neuralNetworkService import analyze_image
from flask_jwt_extended import jwt_required, get_jwt_identity
import os
import uuid
from werkzeug.utils import secure_filename
from datetime import datetime

neural_bp = Blueprint('neural', __name__, url_prefix='/api/neural')

UPLOAD_FOLDER = 'uploads/images'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@neural_bp.route('/analyze', methods=['POST'])
@jwt_required()
@validate_image_upload 
def analyze():
    try:
        current_user_id = get_jwt_identity()
        file = request.files['image'] 
        image_uuid = request.form['uuid']  
        
        filename = secure_filename(f"{image_uuid}_{file.filename}")
        temp_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(temp_path)

        try:
            result = analyze_image(temp_path, current_user_id)
            
            return jsonify({
                "message": "Análise concluída",
                "data": {
                    "image_id": result['image_id'],
                    "image_url": result['image_url'],
                    "objects": result['objects'],
                    "accuracy": result['accuracy'],
                    "metrics": result['metrics'],
                    "objects_count": result['objects_count']
                }
            }), 200
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    except Exception as e:
        return jsonify({
            "error": "Erro ao processar imagem",
            "message": str(e)
        }), 500
