import hashlib
import numpy as np
from PIL import Image
import os

def get_matrix(path):
    img = Image.open(path).convert("L")
    mat = np.array(img)
    h, w = mat.shape
    return mat[h//2-8:h//2+8, w//2-8:w//2+8]

def get_first_iris_image(base_path):
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.lower().endswith(('.jpg', '.png', '.jpeg', '.bmp', '.tif')):
                return os.path.join(root, file)
    return None


fp_path = "Fingerprint_dataset/dataset/FVC2000/DB1_B/104_1.tif"
fingerprint = get_matrix(fp_path)

print("\n[STEP 1] Fingerprint 16x16 Matrix Extracted")


iris_path = get_first_iris_image("Iris_dataset/CASIA-Iris-Thousand")

if iris_path is None:
    raise Exception("No iris image found!")

print("[STEP 2] Iris Image Used:", iris_path)

iris = get_matrix(iris_path)

print("[STEP 3] Iris 16x16 Matrix Extracted")


print("\n[STEP 4] Enter User Details")

username = input("Enter Username: ").lower().strip()
app_name = input("Enter App Name: ").lower().strip()

combined_input = username + "|" + app_name

hash_obj = hashlib.sha3_256(combined_input.encode())
hash_hex = hash_obj.hexdigest()
hash_bytes = hash_obj.digest()

print("\n[STEP 5] SHA3-256 Hash:")
print("Input Used:", combined_input)
print("Hash:", hash_hex)


hash_bin = bin(int(hash_hex, 16))[2:].zfill(512)

row = int(hash_bin[:4], 2)
col = int(hash_bin[-4:], 2)

print("\n[STEP 6] Start Position → Row:", row, "Col:", col)


steps = int((hash_bytes[1] / 255) * 40) + 20
print("[STEP 7] Number of Steps:", steps)


def walk(matrix):
    r, c = row, col
    sig = []

    for i in range(steps):

        direction = int((hash_bytes[i % len(hash_bytes)] / 255) * 7.9999)

        step_size = int((hash_bytes[(i+1) % len(hash_bytes)] / 255) * 2.9999) + 1

        if direction == 0:        # up
            r = (r - step_size) % 16
        elif direction == 1:      # down
            r = (r + step_size) % 16
        elif direction == 2:      # left
            c = (c - step_size) % 16
        elif direction == 3:      # right
            c = (c + step_size) % 16
        elif direction == 4:      # up-right
            r = (r - step_size) % 16
            c = (c + step_size) % 16
        elif direction == 5:      # up-left
            r = (r - step_size) % 16
            c = (c - step_size) % 16
        elif direction == 6:      # down-right
            r = (r + step_size) % 16
            c = (c + step_size) % 16
        else:                     # down-left
            r = (r + step_size) % 16
            c = (c - step_size) % 16

        sig.append(int(matrix[r][c]))

    return sig


fp_sig = walk(fingerprint)
ir_sig = walk(iris)

print("\n[STEP 8] Fingerprint Signature (first 10):", fp_sig[:10])
print("[STEP 9] Iris Signature (first 10):", ir_sig[:10])

combined = []
for a, b in zip(fp_sig, ir_sig):
    combined.append(a)
    combined.append(b)

print("\n[STEP 10] Combined Signature Length:", len(combined))


# Maps 0–255 → 16–64 without mod
raw_len_byte = hash_bytes[8]
length = 16 + int((raw_len_byte / 255) * (64 - 16))
print("[STEP 11] Password Length:", length)


def map_char(v):
    # Maps 0–255 → alphanumeric only (a-z, A-Z, 0-9) = 62 chars, no mod
    index = int((v / 255) * 61.9999)
    if index < 26:
        return chr(97 + index)       # a–z
    elif index < 52:
        return chr(65 + index - 26)  # A–Z
    else:
        return chr(48 + index - 52)  # 0–9

base = "".join(map_char(v) for v in combined[:length])

print("\n[STEP 12] Base Password:", base)


# Select 3 unique positions using division instead of mod
positions = set()
i = 2
while len(positions) < 3:
    pos = int((hash_bytes[i] / 255) * (length - 0.0001))
    positions.add(pos)
    i += 1

pos_special, pos_digit, pos_upper = list(positions)

print("\n[STEP 13] Positions Selected:")
print("Special Char Position:", pos_special)
print("Digit Position:", pos_digit)
print("Uppercase Position:", pos_upper)


password = list(base)

special_chars = "!@#$%^&*"

# Map to special char, digit, uppercase using division
special_index = int((hash_bytes[5] / 255) * (len(special_chars) - 0.0001))
password[pos_special] = special_chars[special_index]

digit_val = int((hash_bytes[6] / 255) * 9.9999)
password[pos_digit] = str(digit_val)

upper_val = int((hash_bytes[7] / 255) * 25.9999)
password[pos_upper] = chr(65 + upper_val)

final_password = "".join(password)

print("\n[STEP 14] Final Password:", final_password)