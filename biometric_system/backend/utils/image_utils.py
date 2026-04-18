import numpy as np
from PIL import Image

def get_matrix(path):
    """
    Load image → convert to grayscale → extract center 16x16 → normalize
    """
    img = Image.open(path).convert("L")
    mat = np.array(img, dtype=np.float64)

    h, w = mat.shape

    center_h = h // 2
    center_w = w // 2

    patch = mat[
        center_h - 8 : center_h + 8,
        center_w - 8 : center_w + 8
    ]

    return patch / 255.0