from flask import Flask
from controllers.neural_network import neural_network_controller


def create_app():
    app = Flask(__name__)

    # Registrar o blueprint do neural_network_controller
    app.register_blueprint(neural_network_controller)

    return app
