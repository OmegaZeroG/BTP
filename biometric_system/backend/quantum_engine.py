import hashlib
import numpy as np
from PIL import Image
import os
from utils.image_utils import get_matrix
# ─────────────────────────────────────────────
# HELPERS (UNCHANGED)
# ─────────────────────────────────────────────

def get_matrix(path):
    img = Image.open(path).convert("L")
    mat = np.array(img, dtype=np.float64)
    h, w = mat.shape
    patch = mat[h//2-8:h//2+8, w//2-8:w//2+8]
    return patch / 255.0

def get_first_iris_image(base_path):
    for root, _, files in os.walk(base_path):
        for f in files:
            if f.lower().endswith(('.jpg','.png','.jpeg','.bmp','.tif')):
                return os.path.join(root, f)
    return None

# ─────────────────────────────────────────────
# QUANTUM WALK ENGINE (UNCHANGED)
# ─────────────────────────────────────────────

def hadamard_coin(psi_up, psi_down):
    s = 1.0 / np.sqrt(2)
    return s * (psi_up + psi_down), s * (psi_up - psi_down)

def shift_operator(psi, direction):
    if direction == 0:   return np.roll(psi, -1, axis=0)
    elif direction == 1: return np.roll(psi,  1, axis=0)
    elif direction == 2: return np.roll(psi, -1, axis=1)
    elif direction == 3: return np.roll(psi,  1, axis=1)
    elif direction == 4: return np.roll(np.roll(psi, -1, axis=0),  1, axis=1)
    elif direction == 5: return np.roll(np.roll(psi, -1, axis=0), -1, axis=1)
    elif direction == 6: return np.roll(np.roll(psi,  1, axis=0),  1, axis=1)
    else:                return np.roll(np.roll(psi,  1, axis=0), -1, axis=1)

def quantum_walk(matrix, hash_bytes, steps, start_row, start_col):
    SIZE = 16
    psi = np.zeros((SIZE, SIZE), dtype=complex)

    for r in range(SIZE):
        for c in range(SIZE):
            dist = ((r - start_row)**2 + (c - start_col)**2)
            psi[r, c] = np.exp(-dist / 8.0)

    phase_seed = hash_bytes[0] / 255.0 * 2 * np.pi
    psi = psi * np.exp(1j * phase_seed)
    norm = np.sqrt(np.sum(np.abs(psi)**2))
    psi  = psi / norm

    psi_up   = psi * 0.7071
    psi_down = psi * 0.7071

    for step in range(steps):
        psi_up, psi_down = hadamard_coin(psi_up, psi_down)
        direction = int((hash_bytes[step % len(hash_bytes)] / 255.0) * 7.9999)
        psi_up   = shift_operator(psi_up,   direction)
        psi_down = shift_operator(psi_down, (direction + 4) % 8)

        phase = matrix * (2 * np.pi * hash_bytes[(step+3) % len(hash_bytes)] / 255.0)
        modulation = np.exp(1j * phase)

        psi_up   = psi_up   * modulation
        psi_down = psi_down * modulation

        total_norm = np.sqrt(np.sum(np.abs(psi_up)**2 + np.abs(psi_down)**2))
        if total_norm > 1e-10:
            psi_up   = psi_up   / total_norm
            psi_down = psi_down / total_norm

    prob = np.abs(psi_up)**2 + np.abs(psi_down)**2
    prob = prob / prob.sum()

    final_psi   = psi_up + psi_down
    phase_values = np.angle(final_psi)
    phase_norm   = (phase_values + np.pi) / (2 * np.pi)

    flat_prob = prob.flatten()
    flat_prob = flat_prob / flat_prob.sum()

    rng = np.random.default_rng(seed=int.from_bytes(hash_bytes[:8], 'big'))
    indices = rng.choice(SIZE * SIZE, size=steps, replace=True, p=flat_prob)

    signature = []
    for idx in indices:
        r, c = divmod(idx, SIZE)
        pixel_val = matrix[r, c]
        phase_val = phase_norm[r, c]
        combined  = (pixel_val * 0.6 + phase_val * 0.4)
        signature.append(combined)

    return signature



def generate_password_with_signature(username, app_name, user_secret, fp_path, iris_base_path, seed):

    iris_path = get_first_iris_image(iris_base_path)
    if iris_path is None:
        raise Exception("No iris image found!")

    fingerprint = get_matrix(fp_path)
    iris = get_matrix(iris_path)

    combined_input = username + "|" + app_name
    if user_secret:
        combined_input += "|" + user_secret

    hash_bytes = hashlib.sha3_256(combined_input.encode() + seed).digest()

    hash_bin  = bin(int.from_bytes(hash_bytes, 'big'))[2:].zfill(256)
    start_row = int(hash_bin[:4], 2)
    start_col = int(hash_bin[-4:], 2)

    steps = int((hash_bytes[1] / 255.0) * 40) + 20

    fp_sig = quantum_walk(fingerprint, hash_bytes, steps, start_row, start_col)
    ir_sig = quantum_walk(iris, hash_bytes, steps, start_row, start_col)

    combined = []
    for a, b in zip(fp_sig, ir_sig):
        combined.append(a)
        combined.append(b)

    signature = combined[:32]

    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()"

    password = ""
    for v in signature:
        index = int(v * (len(chars) - 0.0001))
        password += chars[index]

    return signature, password




def generate_from_signature(signature):

    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()"

    password = ""
    for v in signature:
        index = int(v * (len(chars) - 0.0001))
        password += chars[index]

    return password



# ─────────────────────────────────────────────
# PASSWORD FUNCTION (WRAPPED ONLY)
# ─────────────────────────────────────────────

def generate_password(username, app_name, user_secret, fp_path, iris_base_path, seed):

    iris_path = get_first_iris_image(iris_base_path)
    if iris_path is None:
        raise Exception("No iris image found!")

    fingerprint = get_matrix(fp_path)
    iris = get_matrix(iris_path)

    combined_input = username + "|" + app_name
    if user_secret:
        combined_input += "|" + user_secret

    hash_bytes = hashlib.sha3_256(combined_input.encode() + seed).digest()

    hash_bin  = bin(int.from_bytes(hash_bytes, 'big'))[2:].zfill(256)
    start_row = int(hash_bin[:4], 2)
    start_col = int(hash_bin[-4:], 2)

    steps = int((hash_bytes[1] / 255.0) * 40) + 20

    fp_sig = quantum_walk(fingerprint, hash_bytes, steps, start_row, start_col)
    ir_sig = quantum_walk(iris, hash_bytes, steps, start_row, start_col)

    combined = []
    for a, b in zip(fp_sig, ir_sig):
        combined.append(a)
        combined.append(b)

    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()"

    password = ""
    for v in combined[:32]:
        index = int(v * (len(chars) - 0.0001))
        password += chars[index]

    return password