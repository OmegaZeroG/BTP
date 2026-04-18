from quantum_engine import generate_password_with_signature, generate_from_signature
from database import save_user, get_user
import secrets

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ✅ FIXED PATH (NO "..")
FP_PATH = os.path.abspath(
    os.path.join(BASE_DIR, "Fingerprint_dataset", "dataset", "FVC2000", "DB1_B", "104_1.tif")
)

# ✅ Already correct
IRIS_PATH = os.path.abspath(
    os.path.join(BASE_DIR, "CASIA-Iris-Thousand")
)

print("FP_PATH:", FP_PATH)
print("FP exists:", os.path.exists(FP_PATH))

print("IRIS_PATH:", IRIS_PATH)
print("IRIS exists:", os.path.exists(IRIS_PATH))

def register(username, app, user_secret):

    has_secret = 1 if user_secret else 0

    signature, password = generate_password_with_signature(
        username, app, user_secret,
        FP_PATH, IRIS_PATH,
        secrets.token_bytes(16)   # RANDOM → new password every time
    )

    save_user(username, app, signature, has_secret)

    return password


def login(username, app, user_secret):

    user = get_user(username, app)

    if not user:
        return False, "User not found"

    signature, has_secret = user

    if has_secret and not user_secret:
        return False, "PIN required"

    password = generate_from_signature(signature)

    return True, password