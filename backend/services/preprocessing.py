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

    @staticmethod
    def apply_edge_detection(img):
        return cv2.Canny(img, 100, 200)

    def preprocess_image(self, img):
        target_size = (800, 800)

        # Resize the image to 800x800
        img_resized = cv2.resize(img, target_size)

        # Ensure the image is of type uint8
        img_resized = img_resized.astype(np.uint8)

        # Apply preprocessing steps
        if self.is_grayscale(img_resized):
            img_resized = cv2.cvtColor(img_resized, cv2.COLOR_GRAY2BGR)

        # Se a imagem for muito escura, aplique a equalização de histograma
        if self.is_too_dark(img_resized):
            img_resized = self.apply_histogram_equalization(img_resized)

        # Se a imagem for ruidosa, aplique a denoising
        if self.is_noisy(img_resized):
            img_resized = denoise_bilateral(
                img_resized, sigma_color=0.1, sigma_spatial=15, channel_axis=-1)
            # Converta para uint8
            img_resized = (img_resized * 255).astype(np.uint8)

        contrast = self.calculate_contrast(img_resized)
        # Aumente o contraste apenas se for necessário
        if contrast < 50:
            img_resized = cv2.convertScaleAbs(img_resized, alpha=1.2, beta=10)

        # Apply sharpening filter
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        img_resized = cv2.filter2D(src=img_resized, ddepth=-1, kernel=kernel)

        return img_resized

    @staticmethod
    def save_image(img, path):
        if not cv2.imwrite(path, img):
            print(f"Erro ao salvar a imagem processada: {path}")

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
