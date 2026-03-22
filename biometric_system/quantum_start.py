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


app_name = input("\n[STEP 4] Enter App Name: ").lower().strip()


hash_obj = hashlib.sha3_256(app_name.encode())   # 🔥 upgraded
hash_hex = hash_obj.hexdigest()
hash_bytes = hash_obj.digest()

print("\n[STEP 5] SHA3-256 Hash:", hash_hex)


k = hash_bytes[0] % 64 or 16
ascii_sum = sum(ord(c) for c in hash_hex[:k])

row = ascii_sum % 16
col = (ascii_sum >> 4) % 16

print("\n[STEP 6] Start Position → Row:", row, "Col:", col)


steps = hash_bytes[1] % 40 + 20
print("[STEP 7] Number of Steps:", steps)

# ================= QUANTUM-INSPIRED WALK =================

def walk(matrix):
    r, c = row, col
    sig = []

    for i in range(steps):

        # 🔥 8-direction quantum-inspired movement
        direction = hash_bytes[i % len(hash_bytes)] % 8

        # 🔥 variable step size (1–3)
        step_size = (hash_bytes[(i+1) % len(hash_bytes)] % 3) + 1

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



length = (hash_bytes[8] % 8) + 8
print("[STEP 11] Password Length:", length)


def map_char(v):
    v = v % 62
    if v < 26: return chr(97 + v)
    elif v < 52: return chr(65 + v - 26)
    else: return chr(48 + v - 52)

base = "".join(map_char(v) for v in combined[:length])

print("\n[STEP 12] Base Password:", base)


positions = set()
i = 2
while len(positions) < 3:
    positions.add(hash_bytes[i] % length)
    i += 1

pos_special, pos_digit, pos_upper = list(positions)

print("\n[STEP 13] Positions Selected:")
print("Special Char Position:", pos_special)
print("Digit Position:", pos_digit)
print("Uppercase Position:", pos_upper)


password = list(base)

special_chars = "!@#$%^&*"

password[pos_special] = special_chars[hash_bytes[5] % len(special_chars)]
password[pos_digit] = str(hash_bytes[6] % 10)
password[pos_upper] = chr(65 + hash_bytes[7] % 26)

final_password = "".join(password)

print("\n[STEP 14] Final Password:", final_password)