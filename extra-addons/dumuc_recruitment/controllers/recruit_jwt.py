# dumuc_recruitment/utils/recruit_jwt.py

import jwt
import datetime
import uuid
import hashlib

SECRET = "CHANGE_ME_SECRET"
ALGO = "HS256"

ACCESS_EXPIRE_MIN = 120
REFRESH_EXPIRE_DAYS = 30


# ===========================
# ROLE MAP (KHAI BÁO TẠI ĐÂY)
# ===========================
ROLE_MAP = {
    "admin": "admin",
    "employer": "employer",
    "seeker": "seeker",
    "guest": "guest"
}


def create_access_token(user_id, role):
    payload = {
        "sub": user_id,
        "role": role,
        "scope": "recruitment",
        "type": "access",
        "jti": uuid.uuid4().hex,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_EXPIRE_MIN)
    }
    return jwt.encode(payload, SECRET, algorithm=ALGO)


def create_refresh_token(user_id):
    payload = {
        "sub": user_id,
        "type": "refresh",
        "scope": "recruitment",
        "jti": uuid.uuid4().hex,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=REFRESH_EXPIRE_DAYS)
    }
    return jwt.encode(payload, SECRET, algorithm=ALGO)


def decode_token(token):
    return jwt.decode(token, SECRET, algorithms=[ALGO])


def hash_refresh(token: str):
    return hashlib.sha256(token.encode()).hexdigest()
