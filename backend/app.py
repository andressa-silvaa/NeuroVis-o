from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config.config import Config
from sqlalchemy import text  # Importar o 'text' do SQLAlchemy

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

@app.route('/')
def test_connection():
    try:
        # Use o 'text()' para indicar que é uma expressão SQL textual
        result = db.session.execute(text("SELECT 1"))
        return "Conexão com o banco de dados bem-sucedida!"
    except Exception as e:
        return f"Erro de conexão: {e}"

if __name__ == "__main__":
    app.run(debug=True)
