import os
import torch
import re
from ultralytics import YOLO
import logging

# Configuração de logs
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Ativar expansão de segmentos de memória
os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'expandable_segments:True'


class YOLOv8Trainer:
    # Alterado para yolov8x.pt
    def __init__(self, data_yaml, base_dir, model_weights='yolov8x.pt', train_per_run=20):
        self.data_yaml = data_yaml
        self.base_dir = base_dir
        self.model_weights = model_weights  # Usando YOLOv8x
        self.train_per_run = train_per_run  # Quantidade de épocas por execução
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model = None
        self.last_epoch = 0
        self.last_train_dir = None
        self.last_weights = None

        self._check_device()
        self._find_last_training()

    def _check_device(self):
        if self.device == 'cuda':
            logger.info(f"GPU disponível: {torch.cuda.get_device_name(0)}")
        else:
            logger.warning("GPU não disponível. Usando CPU.")

    def _find_last_training(self):
        """Verifica a última pasta de treino e encontra o último checkpoint"""
        if not os.path.exists(self.base_dir):
            logger.warning(
                f"Diretório {self.base_dir} não existe. Treinamento começará do zero.")
            return

        train_dirs = [d for d in os.listdir(
            self.base_dir) if re.match(r'train\d+', d)]
        train_dirs.sort(key=lambda x: int(re.findall(r'\d+', x)[0]))

        if not train_dirs:
            logger.warning(
                "Nenhuma pasta de treino encontrada. Começando do zero.")
            return

        self.last_train_dir = os.path.join(
            self.base_dir, train_dirs[-1], 'weights')
        logger.info(
            f"Último diretório de treino encontrado: {self.last_train_dir}")

        last_pt_path = os.path.join(self.last_train_dir, 'last.pt')
        best_pt_path = os.path.join(self.last_train_dir, 'best.pt')

        if os.path.exists(last_pt_path):
            self.last_weights = last_pt_path
        elif os.path.exists(best_pt_path):
            self.last_weights = best_pt_path
        else:
            logger.warning(
                "Nenhum checkpoint encontrado. Treinamento começará do zero.")
            return

        logger.info(f"Pesos carregados de: {self.last_weights}")
        self._extract_last_epoch()

    def _extract_last_epoch(self):
        """Lê o arquivo de log para encontrar a última época treinada"""
        log_path = os.path.join(self.last_train_dir, '..', 'results.csv')

        if os.path.exists(log_path):
            try:
                with open(log_path, 'r') as f:
                    lines = f.readlines()
                last_line = lines[-1].strip()
                epoch_match = re.search(r'^(\d+),', last_line)
                if epoch_match:
                    self.last_epoch = int(epoch_match.group(1))
                    logger.info(f"Última época treinada: {self.last_epoch}")
            except Exception as e:
                logger.error(f"Erro ao ler log de treino: {e}")

    def load_model(self):
        """Carrega o modelo a partir do último checkpoint ou do modelo pré-treinado"""
        if self.last_weights:
            logger.info(f"Carregando modelo de {self.last_weights}")
            self.model = YOLO(self.last_weights)
        else:
            logger.info(
                f"Carregando modelo pré-treinado: {self.model_weights}")
            self.model = YOLO(self.model_weights)

    def train(self):
        """Treina o modelo por 20 épocas por execução"""
        logger.info(
            f"Iniciando treinamento por {self.train_per_run} épocas a partir da época {self.last_epoch}...")

        try:
            self.model.train(
                data=self.data_yaml,
                epochs=self.last_epoch + self.train_per_run,  # Total de épocas
                imgsz=640,  # Aumentado para 640
                batch=16,  # Aumentado para 16
                device=self.device,
                save=True,
                save_period=self.train_per_run,  # Salva a cada 20 épocas
                plots=True,
                rect=True,
                workers=4,  # Aumentado para 4 workers
                augment=True,  # Ativar aumento de dados
                resume=True,  # Tenta retomar o treinamento
                lr0=0.01,  # Taxa de aprendizagem inicial
                lrf=0.01,  # Taxa de aprendizagem final reduzida
                momentum=0.937,  # Momentum
                weight_decay=0.0005,  # Weight decay
                amp=True,  # Ativar precisão mista
                patience=10,  # Early stopping após 10 épocas sem melhoria
                warmup_epochs=3,  # Warmup para as primeiras 3 épocas
                warmup_momentum=0.8,  # Momentum durante o warmup
                warmup_bias_lr=0.1  # Taxa de aprendizagem do bias durante o warmup
            )
            self.last_epoch += self.train_per_run  # Atualiza a última época
            logger.info(
                f"Treinamento concluído até a época {self.last_epoch}.")
        except Exception as e:
            logger.error(f"Erro durante o treinamento: {e}")

            # Se o erro for relacionado a não poder retomar, inicie um novo treinamento
            if "nothing to resume" in str(e):
                logger.warning(
                    "Iniciando um novo treinamento a partir do modelo pré-treinado.")
                self.model.train(
                    data=self.data_yaml,
                    epochs=self.train_per_run,
                    imgsz=640,
                    batch=16,
                    device=self.device,
                    save=True,
                    save_period=self.train_per_run,
                    plots=True,
                    rect=True,
                    workers=4,  # Aumentado para 4 workers
                    augment=True,
                    resume=False,  # Não retomar, iniciar novo treinamento
                    lr0=0.01,
                    lrf=0.01,
                    momentum=0.937,
                    weight_decay=0.0005,
                    amp=True,
                    patience=10,
                    warmup_epochs=3,
                    warmup_momentum=0.8,
                    warmup_bias_lr=0.1
                )
                self.last_epoch = 0  # Reinicia a contagem de épocas
                logger.info(
                    f"Novo treinamento concluído até a época {self.last_epoch}.")


if __name__ == "__main__":
    data_yaml = 'E:/APS6/NeuroVis-o/backend/dataset/dataset_config.yaml'
    base_dir = 'E:/APS6/NeuroVis-o/runs/detect'
    model_weights = 'yolov8x.pt'  # Alterado para yolov8x.pt
    train_per_run = 20  # Rodar apenas 20 épocas por execução

    trainer = YOLOv8Trainer(
        data_yaml=data_yaml,
        base_dir=base_dir,
        model_weights=model_weights,
        train_per_run=train_per_run
    )

    trainer.load_model()
    trainer.train()
