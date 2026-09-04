from passlib.context import CryptContext


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


MAX_PASSWORD_BYTES = 72


def hash_password(password):
    if len(password.encode("utf-8")) > MAX_PASSWORD_BYTES:
        raise ValueError(
            "Password must be 72 bytes or fewer."
        )

    return pwd_context.hash(password)


def verify_password(
    plain_password,
    hashed_password
):
    if len(plain_password.encode("utf-8")) > MAX_PASSWORD_BYTES:
        return False

    return pwd_context.verify(
        plain_password,
        hashed_password
    )