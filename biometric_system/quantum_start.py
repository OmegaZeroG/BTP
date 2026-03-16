import hashlib
import numpy as np
from PIL import Image


fingerprint_path = "Fingerprint_dataset/dataset/FVC2000/DB1_B/104_1.tif"

fingerprint_img = Image.open(fingerprint_path).convert("L")
fp_matrix = np.array(fingerprint_img)

h, w = fp_matrix.shape
center_h = h // 2
center_w = w // 2

fingerprint_16x16 = fp_matrix[
    center_h - 8:center_h + 8,
    center_w - 8:center_w + 8
]


app_name = input("Enter App Name: ")
app_name = app_name.lower().strip()


hash_object = hashlib.sha256(app_name.encode())
hash_hex = hash_object.hexdigest()
hash_bytes = hash_object.digest()

print("\nSHA-256 Hash:")
print(hash_hex)


k = hash_bytes[0] % 64
if k == 0:
    k = 16

print("\nWindow Size (k):", k)


ascii_values = [ord(char) for char in hash_hex[:k]]
ascii_sum = sum(ascii_values)

print("Partial ASCII Sum:", ascii_sum)


row = ascii_sum % 16
col = (ascii_sum >> 4) % 16

print("\nStarting Position:")
print("Row:", row)
print("Col:", col)


steps = hash_bytes[1] % 64 + 16
print("\nNumber of Steps:", steps)


current_row = row
current_col = col

signature = []

for i in range(steps):

    direction = hash_bytes[i % len(hash_bytes)] % 4

    if direction == 0:      
        current_row = (current_row - 1) % 16
    elif direction == 1:    
        current_row = (current_row + 1) % 16
    elif direction == 2:    
        current_col = (current_col - 1) % 16
    else:                   
        current_col = (current_col + 1) % 16

    signature.append(int(fingerprint_16x16[current_row][current_col]))

print("\nTraversal Signature:")
print(signature)
#Flatten it 
