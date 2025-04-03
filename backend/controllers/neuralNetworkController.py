from flask import Blueprint, request, jsonify
from services.neuralNetworkService import analyze_image
from flask_jwt_extended import jwt_required, get_jwt_identity
import os
import uuid
from werkzeug.utils import secure_filename
from datetime import datetime

neural_bp = Blueprint('neural', __name__, url_prefix='/api/neural')

# Configurações (ajuste conforme seu ambiente)
UPLOAD_FOLDER = 'uploads/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@neural_bp.route('/analyze', methods=['POST'])
@jwt_required()
def analyze():
    try:
        current_user_id = get_jwt_identity()
        
        # Verifica se a imagem foi enviada
        if 'image' not in request.files:
            return jsonify({"error": "Nenhuma imagem enviada"}), 400
            
        file = request.files['image']
        
        if file.filename == '':
            return jsonify({"error": "Nome de arquivo vazio"}), 400
            
        if not allowed_file(file.filename):
            return jsonify({"error": "Tipo de arquivo não permitido"}), 400

        # Salva a imagem temporariamente
        filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
        temp_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(temp_path)

        # Processa a imagem
        result = analyze_image(temp_path, current_user_id)

        # Remove o arquivo temporário (opcional)
        os.remove(temp_path)

        return jsonify({
            "message": "Análise concluída",
            "processed_image_url": result['processed_image_url'],
            "recognized_objects": result['recognized_objects'],
            "accuracy": result['accuracy'],
            "image_id": result['image_id']
        }), 200

    except Exception as e:
        return jsonify({
            "error": "Erro ao processar imagem",
            "message": str(e)
        }), 500