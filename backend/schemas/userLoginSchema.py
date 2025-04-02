from marshmallow import Schema, fields, validate, ValidationError

class UserLoginSchema(Schema):
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

    class Meta:
        strict = True