from imgurpython import ImgurClient
from config.config import Config
import logging
import os

logger = logging.getLogger(__name__)

class ImgurUploader:
    def __init__(self):
        # Autenticação básica (não requer access token)
        self.client = ImgurClient(Config.IMGUR_CLIENT_ID, Config.IMGUR_CLIENT_SECRET)
    
    def upload_image(self, image_path):
        try:
            # Upload anônimo (não requer autenticação de usuário)
            response = self.client.upload_from_path(
                image_path,
                config=None,
                anon=True  # Upload não autenticado
            )
            
            logger.info(f"Upload para Imgur realizado. Link: {response['link']}")
            return response['link']
            
        except Exception as e:
            logger.error(f"Erro no upload para Imgur: {str(e)}")
            raise

imgur_uploader = ImgurUploader()