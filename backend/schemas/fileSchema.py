from marshmallow import Schema, ValidationError, fields, validates_schema
from flask import request, jsonify
from werkzeug.datastructures import FileStorage
import os

class FileValidationSchema(Schema):
    image = fields.Field(
        required=True,
        error_messages={
            "required": "O campo 'imagem' é obrigatório",
            "null": "Nenhuma imagem foi enviada"
        }
    )
    
    @validates_schema
    def validate_file(self, data, **kwargs):
        if 'image' not in request.files:
            raise ValidationError("Nenhum arquivo de imagem foi enviado", field_name="image")
        
        file = request.files['image']
        
        if file.filename.strip() == '':
            raise ValidationError("O nome do arquivo não pode estar vazio", field_name="image")
        
        if not isinstance(file, FileStorage):
            raise ValidationError("O arquivo enviado não é válido", field_name="image")
        
        allowed_extensions = {'png', 'jpg', 'jpeg'}
        filename = file.filename.lower()
        
        if '.' not in filename:
            raise ValidationError("O arquivo não possui extensão", field_name="image")
            
        extension = filename.rsplit('.', 1)[1]
        
        if extension not in allowed_extensions:
            raise ValidationError(
                "Formato de arquivo não suportado. Use apenas: PNG, JPG ou JPEG", 
                field_name="image"
            )

def validate_image_upload(func):
    def wrapper(*args, **kwargs):
        schema = FileValidationSchema()
        try:
            data = {'image': request.files.get('image')}
            errors = schema.validate(data)
            
            if errors:
                formatted_errors = {
                    "erro": {
                        "mensagem": "Validação falhou",
                        "erros": {
                            field: messages[0] if isinstance(messages, list) and len(messages) > 0 else str(messages)
                            for field, messages in errors.items()
                        }
                    }
                }
                return jsonify(formatted_errors), 400
                
            return func(*args, **kwargs)
            
        except ValidationError as err:
            error_response = {
                "erro": {
                    "mensagem": "Erro na validação do arquivo",
                    "detalhes": {
                        field: messages[0] if isinstance(messages, list) else str(messages)
                        for field, messages in err.messages.items()
                    }
                }
            }
            return jsonify(error_response), 400
            
        except Exception as e:
            return jsonify({
                "erro": {
                    "mensagem": "Erro interno ao processar a imagem",
                    "detalhes": str(e)
                }
            }), 500
    
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper