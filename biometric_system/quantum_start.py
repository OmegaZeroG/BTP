import hashlib
import numpy as np
from PIL import Image
import os

# ─────────────────────────────────────────────
#  HELPERS
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
#  QUANTUM WALK ENGINE
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


# ─────────────────────────────────────────────
#  CHARACTER MAPPING  (no mod)
# ─────────────────────────────────────────────

def map_char(v):
    index = int(v * 61.9999)
    if index < 26:   return chr(97 + index)
    elif index < 52: return chr(65 + index - 26)
    else:            return chr(48 + index - 52)


# ─────────────────────────────────────────────
#  HASH-DRIVEN SPECIAL CHARACTER ENGINE
# ─────────────────────────────────────────────

def get_special_count(hash_bytes, length):
    """
    Derive number of special characters from hash.
    Maps hash_bytes[9] to range [2, length//4].
    Ensures at least 2 and at most 25% of password length.
    """
    max_specials = max(2, length // 4)     # e.g. length=32 → max 8 specials
    min_specials = 2
    raw = hash_bytes[9] / 255.0
    count = min_specials + int(raw * (max_specials - min_specials))
    return count


def get_special_positions(hash_bytes, length, count):
    """
    Derive `count` unique positions from hash using division mapping.
    Uses a chain of hash bytes starting at index 10.
    If we exhaust hash_bytes, re-hash the last used bytes for more entropy.
    """
    positions = set()
    byte_index = 10
    extra_hash  = hash_bytes    # fallback pool

    while len(positions) < count:
        if byte_index >= len(extra_hash):
            # Re-hash to get more bytes without mod
            extra_hash = hashlib.sha3_256(extra_hash).digest()
            byte_index = 0

        pos = int((extra_hash[byte_index] / 255.0) * (length - 0.0001))
        positions.add(pos)
        byte_index += 1

    return sorted(positions)    # sorted so injection is left-to-right


def get_special_chars(hash_bytes, count):
    """
    Pick `count` special characters from the pool using hash bytes.
    Uses bytes starting at index 5, re-hashing if needed.
    """
    special_pool = "!@#$%^&*()-_=+[]{}|;:,.<>?"
    chars = []
    byte_index  = 5
    extra_hash   = hash_bytes

    for i in range(count):
        if byte_index >= len(extra_hash):
            extra_hash = hashlib.sha3_256(extra_hash).digest()
            byte_index = 0

        idx  = int((extra_hash[byte_index] / 255.0) * (len(special_pool) - 0.0001))
        chars.append(special_pool[idx])
        byte_index += 1

    return chars


# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────

fp_path     = "Fingerprint_dataset/dataset/FVC2000/DB1_B/104_1.tif"
fingerprint = get_matrix(fp_path)
print("[STEP 1]  Fingerprint 16×16 matrix extracted")

iris_path = get_first_iris_image("Iris_dataset/CASIA-Iris-Thousand")
if iris_path is None:
    raise Exception("No iris image found!")
print("[STEP 2]  Iris image:", iris_path)

iris = get_matrix(iris_path)
print("[STEP 3]  Iris 16×16 matrix extracted")

print("\n[STEP 4]  Enter user details")
username = input("Enter Username: ").lower().strip()
app_name = input("Enter App Name: ").lower().strip()
combined_input = username + "|" + app_name

hash_obj   = hashlib.sha3_256(combined_input.encode())
hash_hex   = hash_obj.hexdigest()
hash_bytes = hash_obj.digest()

print("\n[STEP 5]  SHA3-256 hash")
print("Input :", combined_input)
print("Hash  :", hash_hex)

hash_bin  = bin(int(hash_hex, 16))[2:].zfill(256)
start_row = int(hash_bin[:4], 2)
start_col = int(hash_bin[-4:], 2)
print(f"\n[STEP 6]  Start position → row: {start_row}, col: {start_col}")

steps = int((hash_bytes[1] / 255.0) * 40) + 20
print(f"[STEP 7]  Quantum walk steps: {steps}")

print("\n[STEP 8]  Running quantum walk on fingerprint...")
fp_sig = quantum_walk(fingerprint, hash_bytes, steps, start_row, start_col)

print("[STEP 9]  Running quantum walk on iris...")
ir_sig = quantum_walk(iris, hash_bytes, steps, start_row, start_col)

combined = []
for a, b in zip(fp_sig, ir_sig):
    combined.append(a)
    combined.append(b)
print(f"\n[STEP 10] Combined signature length: {len(combined)}")

# Password length 16–64
length = 16 + int((hash_bytes[8] / 255.0) * (64 - 16))
print(f"[STEP 11] Password length: {length}")

# Alphanumeric base
base = "".join(map_char(v) for v in combined[:length])
print(f"\n[STEP 12] Base password (alphanumeric): {base}")

# ── Hash-driven special character count ──
num_specials = get_special_count(hash_bytes, length)
print(f"\n[STEP 13] Number of special characters (from hash): {num_specials}")

# ── Hash-driven unique positions ──
special_positions = get_special_positions(hash_bytes, length, num_specials)
print(f"[STEP 14] Injection positions (from hash): {special_positions}")

# ── Hash-driven special character selection ──
special_chars = get_special_chars(hash_bytes, num_specials)
print(f"[STEP 15] Special characters selected: {special_chars}")

# ── Inject into password ──
password = list(base)
for pos, char in zip(special_positions, special_chars):
    password[pos] = char

# ── Always guarantee 1 digit + 1 uppercase (from hash, no mod) ──
# Use positions and bytes not already used by specials
digit_pos = int((hash_bytes[6] / 255.0) * (length - 0.0001))
upper_pos = int((hash_bytes[7] / 255.0) * (length - 0.0001))

# Shift by 1 if they collide with a special position
while digit_pos in special_positions:
    digit_pos = (digit_pos + 1) % length
while upper_pos in special_positions or upper_pos == digit_pos:
    upper_pos = (upper_pos + 1) % length

digit_val = int((hash_bytes[6] / 255.0) * 9.9999)
upper_val = int((hash_bytes[7] / 255.0) * 25.9999)

password[digit_pos] = str(digit_val)
password[upper_pos] = chr(65 + upper_val)

final_password = "".join(password)

print(f"\n[STEP 16] Digit injected at position : {digit_pos}")
print(f"[STEP 17] Uppercase injected at position: {upper_pos}")
print(f"\n[STEP 18] Final password : {final_password}")
print(f"          Length         : {len(final_password)}")
print(f"          Specials used  : {num_specials}  at positions {special_positions}")