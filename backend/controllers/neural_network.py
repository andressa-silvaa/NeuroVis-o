from flask import Blueprint, request, jsonify
from services.object_analysis_service import ObjectAnalysisService
from services.composition_analysis_service import CompositionAnalysisService

# Definindo o blueprint para o controlador de análise de objetos
neural_network_controller = Blueprint('neurasl_network_controller', __name__)

object_composition_service = CompositionAnalysisService()
object_analysis_service = ObjectAnalysisService()


@neural_network_controller.route('/analyze-object', methods=['POST'])
def analyze_object():
    if 'image' not in request.files:
        return jsonify({"error": "Nenhuma imagem enviada"}), 400

    image = request.files['image']
    result = object_analysis_service.process_image(image)
    return jsonify(result), 200


@neural_network_controller.route('/analyze-composition', methods=['POST'])
def analyze_composition():
    if 'image' not in request.files:
        return jsonify({"error": "Nenhuma imagem enviada"}), 400

    image = request.files['image']
    result = object_composition_service.process_image(image)
    return jsonify(result), 200
