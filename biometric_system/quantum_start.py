import hashlib
import numpy as np
from PIL import Image
import os

# ================= LOAD MATRIX =================

def get_matrix(path):
    img = Image.open(path).convert("L")
    mat = np.array(img)
    h, w = mat.shape
    center = mat[h//2-8:h//2+8, w//2-8:w//2+8]
    return center

def get_first_iris_image(base_path):
    for root, _, files in os.walk(base_path):
        for file in files:
            if file.lower().endswith(('.jpg', '.png', '.jpeg', '.bmp', '.tif')):
                return os.path.join(root, file)
    return None

# ================= LOAD DATA =================

fp_path = "Fingerprint_dataset/dataset/FVC2000/DB1_B/104_1.tif"
iris_path = get_first_iris_image("Iris_dataset/CASIA-Iris-Thousand")

fp = get_matrix(fp_path)
iris = get_matrix(iris_path)

print("\n[STEP 1] Fingerprint Matrix Shape:", fp.shape)
print("[STEP 2] Iris Matrix Shape:", iris.shape)

print("\nFingerprint Sample:\n", fp[6:10, 6:10])
print("\nIris Sample:\n", iris[6:10, 6:10])

# ================= XOR MERGE =================

merged = np.bitwise_xor(fp, iris)

print("\n[STEP 3] XOR Merged Matrix Sample:\n", merged[6:10, 6:10])


# ================= ROW HASH (INTEGRITY CHECK) =================

print("\n[STEP 4] Generating Row Hashes (Integrity Layer):")

row_hashes = []

for i in range(16):
    row_data = ",".join(map(str, merged[i]))
    row_hash = hashlib.sha256(row_data.encode()).hexdigest()
    row_hashes.append(row_hash)

    if i < 5:  # print first 5 for display
        print(f"Row {i} Hash:", row_hash[:16], "...")

# Combine all row hashes into one fingerprint
combined_hash = hashlib.sha256("".join(row_hashes).encode()).hexdigest()

print("\n[STEP 5] Combined Matrix Hash (Integrity Signature):")
print(combined_hash)

# ================= INPUT =================

app = input("\n[STEP 4] Enter App Name: ").lower().strip()

# ================= SHA-512 =================

hash_hex = hashlib.sha512(app.encode()).hexdigest()
hash_bin = bin(int(hash_hex, 16))[2:].zfill(512)

print("\n[STEP 5] SHA-512 (first 64 bits):")
print(hash_bin[:64])
print("SHA-512 (last 64 bits):")
print(hash_bin[-64:]) 

# ================= START POSITION =================

row = int(hash_bin[:4], 2)
col = int(hash_bin[-4:], 2)

print(f"\n[STEP 6] Start Position → Row: {row}, Col: {col}")

# ================= NUMBER OF STEPS =================

steps = int(hash_bin[4:10], 2) + 20

print("[STEP 7] Number of Steps:", steps)

# ================= PASSWORD LENGTH =================

length = int(hash_bin[10:16], 2) + 15

if length > 64:
    length = 64

print("[STEP 8] Password Length:", length)

# ================= RANDOM WALK =================

r, c = row, col
indices = []

print("\n[STEP 9] Random Walk (first 10 steps):")

for i in range(steps):

    start = 16 + (i * 3)   # 3 bits per step
    direction_bits = hash_bin[start:start+3]

    if len(direction_bits) < 3:
        break

    direction = int(direction_bits, 2)

    if direction == 0:          # UP
        r = (r - 1) & 15
    elif direction == 1:        # DOWN
        r = (r + 1) & 15
    elif direction == 2:        # LEFT
        c = (c - 1) & 15
    elif direction == 3:        # RIGHT
        c = (c + 1) & 15
    elif direction == 4:        # UP-LEFT
        r = (r - 1) & 15
        c = (c - 1) & 15
    elif direction == 5:        # UP-RIGHT
        r = (r - 1) & 15
        c = (c + 1) & 15
    elif direction == 6:        # DOWN-LEFT
        r = (r + 1) & 15
        c = (c - 1) & 15
    else:                       # DOWN-RIGHT
        r = (r + 1) & 15
        c = (c + 1) & 15

    index = r * 16 + c
    indices.append(index)

    if i < 10:
        print(f"Step {i}: ({r},{c}) → index={index}")

# ================= CHARACTER MAP =================

chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

def map_char(v):
    return chars[v % 62]

# ================= PASSWORD GENERATION =================

password = "".join(map_char(v) for v in indices[:length])

print("\n[STEP 11] Final Password:\n", password)