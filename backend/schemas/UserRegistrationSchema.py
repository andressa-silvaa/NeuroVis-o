from marshmallow import Schema, fields, validate, ValidationError
from repositories.userRepository import get_user_by_email

class UserRegistrationSchema(Schema):
    email = fields.Email(required=True, error_messages={
        "required": "O email é obrigatório",
        "invalid": "Email inválido"
    })
    
    password = fields.Str(required=True, validate=[
        validate.Length(
            min=6, 
            max=20,  
            error="A senha deve ter entre 6 e 20 caracteres"
        )
    ], error_messages={
        "required": "A senha é obrigatória"
    })
    
    name = fields.Str(required=True, validate=[
        validate.Length(min=3, error="O nome deve ter pelo menos 3 caracteres")
    ], error_messages={
        "required": "O nome é obrigatório"
    })

    class Meta:
        strict = True

    def validate_email(self, email):
        """Validação customizada para email único"""
        if get_user_by_email(email):
            raise ValidationError("Este email já está cadastrado")