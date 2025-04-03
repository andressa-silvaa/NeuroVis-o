import cv2
import numpy as np
from tkinter import *
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from skimage.restoration import denoise_bilateral
import os


class ImageProcessor:
    def __init__(self):
        self.root = Tk()
        self.root.title("Image Preprocessing")
        self.root.geometry("300x200")

        # Frame para o label de processamento
        self.processing_frame = Frame(self.root)
        self.processing_frame.pack(pady=10)

        # Ajusta o comprimento da linha
        self.processing_label = Label(
            self.processing_frame, text="", wraplength=280)
        self.processing_label.pack(pady=10)

        btn_select = Button(self.root, text="Select Image",
                            command=self.select_image)
        btn_select.pack(pady=20)

    @staticmethod
    def is_grayscale(img):
        return len(img.shape) < 3 or img.shape[2] == 1

    @staticmethod
    def is_too_dark(img, threshold=50):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return np.mean(gray) < threshold

    @staticmethod
    def is_noisy(img, threshold=30):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return cv2.Laplacian(gray, cv2.CV_64F).var() < threshold

    @staticmethod
    def calculate_contrast(img):
        if img.dtype != np.uint8:
            img = img.astype(np.uint8)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        contrast = gray.max() - gray.min()
        return contrast

    @staticmethod
    def apply_histogram_equalization(img):
        img_yuv = cv2.cvtColor(img, cv2.COLOR_BGR2YUV)
        img_yuv[:, :, 0] = cv2.equalizeHist(img_yuv[:, :, 0])
        return cv2.cvtColor(img_yuv, cv2.COLOR_YUV2BGR)

    def improve_image_quality(self, img):
        # Ajusta brilho e contraste de maneira leve
        alpha = 1.1  # Fator de ganho de contraste ajustado
        beta = 5     # Fator de brilho suavizado
        img = cv2.convertScaleAbs(img, alpha=alpha, beta=beta)
        return img

    def preprocess_image(self, img):
        # Tamanho desejado para a imagem
        target_size = (640, 640)
        original_height, original_width = img.shape[:2]

        # Se a imagem for menor que 640x640, coloca ela centralizada em um fundo preto
        if original_height < 640 or original_width < 640:
            new_img = np.zeros((640, 640, 3), dtype=np.uint8)  # Fundo preto
            x_offset = (target_size[0] - original_width) // 2
            y_offset = (target_size[1] - original_height) // 2
            new_img[y_offset:y_offset + original_height,
                    x_offset:x_offset + original_width] = img
            img = new_img
        else:
            img = cv2.resize(img, target_size)  # Redimensiona para 640x640

        # Aplicar pré-processamento para qualquer imagem
        if self.is_too_dark(img):
            img = self.apply_histogram_equalization(img)

        if self.is_noisy(img):
            img = denoise_bilateral(
                img, sigma_color=0.05, sigma_spatial=10, channel_axis=-1)  # Reduzir o efeito de ruído
            img = (img * 255).astype(np.uint8)

        img = self.improve_image_quality(img)

        # Diminuir a luminosidade de maneira suave
        alpha = 0.95
        beta = -5
        img = cv2.convertScaleAbs(img, alpha=alpha, beta=beta)

        # Aumentar a nitidez com um kernel suave
        kernel = np.array(
            [[0, -0.05, 0], [-0.05, 1.1, -0.05], [0, -0.05, 0]])  # Kernel mais suave
        img = cv2.filter2D(src=img, ddepth=-1, kernel=kernel)

        # Segmentação com limiarização adaptativa (para manter a imagem colorida)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)
        segmented_img = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)

        # Combine a imagem segmentada com a original
        img = cv2.bitwise_and(img, segmented_img)

        return img

    @staticmethod
    def save_image(img, path):
        if not cv2.imwrite(path, img):
            print(f"Erro ao salvar a imagem processada: {path}")

    def select_image(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("Image files", ".jpg;.jpeg;.png;.bmp")])
        if not filepath:
            return

        img = cv2.imread(filepath)

        if img is None:
            messagebox.showerror("Error", "Failed to load image!")
            return

        self.processing_label.config(text="Processing image, please wait...")
        self.root.update()

        try:
            processed_img = self.preprocess_image(img)

            # Verifica se a imagem processada não está vazia
            if processed_img is None or np.sum(processed_img) == 0:
                messagebox.showerror("Error", "Processed image is empty!")
                self.processing_label.config(text="")
                return

            self.display_image(img, "Original Image")
            self.display_image(processed_img, "Processed Image")

            save_path = os.path.join(os.path.expanduser(
                "~"), "Downloads", "processed_image.jpg")
            self.save_image(processed_img, save_path)
            print(f"Processed image saved at: {save_path}")

            self.processing_label.config(text="Image processed successfully!")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to process image: {str(e)}")
            self.processing_label.config(text="")

    def display_image(self, img, title="Image"):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        img_tk = ImageTk.PhotoImage(image=img_pil)

        top = Toplevel()
        top.title(title)

        label = Label(top, image=img_tk)
        label.image = img_tk
        label.pack()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    processor = ImageProcessor()
    processor.run()
