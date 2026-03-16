from PIL import Image
import numpy as np


fingerprint_path = "Fingerprint_dataset/dataset/FVC2002/DB1_B/104_1.tif"
iris_path = r"Iris_dataset\CASIA-Iris-Thousand\CASIA-Iris-Thousand\000\L\S5000L00.jpg"


fingerprint_img = Image.open(fingerprint_path).convert("L")
iris_img = Image.open(iris_path).convert("L")


fingerprint_matrix = np.array(fingerprint_img)
iris_matrix = np.array(iris_img)


print("Original Fingerprint Shape:", fingerprint_matrix.shape)
print("Original Iris Shape:", iris_matrix.shape)


fp_matrix = np.array(fingerprint_img)
iris_matrix = np.array(iris_img)


fp_h, fp_w = fp_matrix.shape
iris_h, iris_w = iris_matrix.shape


fp_center_h = fp_h // 2
fp_center_w = fp_w // 2


iris_center_h = iris_h // 2
iris_center_w = iris_w // 2


fingerprint_16x16 = fp_matrix[
    fp_center_h - 8 : fp_center_h + 8,
    fp_center_w - 8 : fp_center_w + 8
]


iris_16x16 = iris_matrix[
    iris_center_h - 8 : iris_center_h + 8,
    iris_center_w - 8 : iris_center_w + 8
]


print("\nFingerprint Center 16x16 Matrix:")
print(fingerprint_16x16)


print("\nIris Center 16x16 Matrix:")
print(iris_16x16)


print("\nFingerprint Shape:", fingerprint_16x16.shape)
print("Iris Shape:", iris_16x16.shape)


print("\nFingerprint 16x16 Matrix:")
print(fingerprint_16x16)


print("\nIris 16x16 Matrix:")
print(iris_16x16)


print("\nFingerprint 16x16 Shape:", fingerprint_16x16.shape)
print("Iris 16x16 Shape:", iris_16x16.shape)

