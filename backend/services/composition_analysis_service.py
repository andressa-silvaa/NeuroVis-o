import os
from werkzeug.utils import secure_filename


class CompositionAnalysisService:
    def __init__(self):
        self.upload_folder = './uploads/compositions'
        os.makedirs(self.upload_folder, exist_ok=True)

    def process_image(self, image):
        filename = secure_filename(image.filename)
        image_path = os.path.join(self.upload_folder, filename)
        image.save(image_path)

        result = {
            "composition": {
                "Material A": 45.0,
                "Material B": 35.0,
                "Material C": 20.0
            },
            "accuracy": 0.90
        }

        # TODO: Substituir pela lógica real da análise de composição

        return result
