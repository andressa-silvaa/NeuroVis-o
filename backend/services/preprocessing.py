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
        self.processing_label = Label(self.root, text="")
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
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        contrast = gray.max() - gray.min()
        return contrast

    @staticmethod
    def apply_histogram_equalization(img):
        img_yuv = cv2.cvtColor(img, cv2.COLOR_BGR2YUV)
        img_yuv[:, :, 0] = cv2.equalizeHist(img_yuv[:, :, 0])
        return cv2.cvtColor(img_yuv, cv2.COLOR_YUV2BGR)

    @staticmethod
    def apply_edge_detection(img):
        return cv2.Canny(img, 100, 200)

    def preprocess_image(self, img, annotations=None):
        original_h, original_w = img.shape[:2]
        target_size = (800, 800)

        # Redimensiona a imagem para 800x800
        img_resized = cv2.resize(img, target_size)

        # Ajustar as anotações (se fornecidas)
        if annotations:
            for annotation in annotations:
                annotation['XMin'] = (
                    annotation['XMin'] * original_w) / target_size[1]
                annotation['XMax'] = (
                    annotation['XMax'] * original_w) / target_size[1]
                annotation['YMin'] = (
                    annotation['YMin'] * original_h) / target_size[0]
                annotation['YMax'] = (
                    annotation['YMax'] * original_h) / target_size[0]

        # Aplicar outras etapas de pré-processamento, como equalização de histograma, remoção de ruído, etc.
        if self.is_grayscale(img_resized):
            img_resized = cv2.cvtColor(img_resized, cv2.COLOR_GRAY2BGR)

        if self.is_too_dark(img_resized):
            img_resized = self.apply_histogram_equalization(img_resized)

        if self.is_noisy(img_resized):
            img_resized = denoise_bilateral(
                img_resized, sigma_color=0.01, sigma_spatial=5, channel_axis=-1)

        contrast = self.calculate_contrast(img_resized)
        if contrast < 50:
            img_resized = cv2.convertScaleAbs(img_resized, alpha=1.5, beta=0)

        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        img_resized = cv2.filter2D(src=img_resized, ddepth=-1, kernel=kernel)

        return img_resized, annotations if annotations else None

    @staticmethod
    def save_image(img, path):
        cv2.imwrite(path, img)

    def select_image(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.bmp")])
        if not filepath:
            return

        img = cv2.imread(filepath)

        if img is None:
            messagebox.showerror("Error", "Failed to load image!")
            return

        self.processing_label.config(text="Processing image, please wait...")
        self.root.update()

        try:
            # Exemplo de anotação. No seu caso, você leria do arquivo correspondente à imagem.
            annotations = [
                {'XMin': 0.1, 'XMax': 0.5, 'YMin': 0.2, 'YMax': 0.6},
                {'XMin': 0.3, 'XMax': 0.7, 'YMin': 0.4, 'YMax': 0.8}
            ]

            processed_img, updated_annotations = self.preprocess_image(
                img, annotations)

            self.display_image(img, "Original Image")
            self.display_image(processed_img, "Processed Image")

            save_path = os.path.join(os.path.expanduser(
                "~"), "Downloads", "processed_image.jpg")
            self.save_image(processed_img, save_path)
            print(f"Imagem processada salva em: {save_path}")
            print("Novas anotações:", updated_annotations)

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
