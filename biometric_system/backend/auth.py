from quantum_engine import (
    generate_password_with_signature
)

from database import save_user, get_users

import secrets


# ---------------------------------------------------
# REGISTER
# ---------------------------------------------------

def register(
    username,
    app,
    user_secret,
    fp_path,
    iris_path
):

    has_secret = 1 if user_secret else 0

    seed = secrets.token_bytes(16)

    signature, password = generate_password_with_signature(
        username,
        app,
        user_secret,
        fp_path,
        iris_path,
        seed
    )

    save_user(
        username,
        app,
        signature,
        seed,
        has_secret
    )

    return password


# ---------------------------------------------------
# LOGIN
# ---------------------------------------------------

def login(
    username,
    app,
    user_secret,
    fp_path,
    iris_path
):

    users = get_users(username, app)

    if not users:
        return False, "User not found"

    for stored_signature, seed, has_secret in users:

        if has_secret and not user_secret:
            continue

        new_signature, password = generate_password_with_signature(
            username,
            app,
            user_secret,
            fp_path,
            iris_path,
            seed
        )

        if new_signature == stored_signature:

            return True, password

    return False, "Biometric mismatch"