from typing import Any, Dict, Tuple
from datetime import datetime, timedelta
import jwt
from app.core.config import settings


ALGORITHM = "HS256"


def generate_access_token(user_data: Dict, expire_days: int = 5):
    expire_time = (datetime.now() + timedelta(seconds=expire_days)).timestamp()
    access_token_payload = {
        "user_id": user_data["id"],
        "mobile": user_data["email"],
        "exp": expire_time,
    }
    access_token = jwt.encode(
        access_token_payload, settings.SECRET_KEY, algorithm=ALGORITHM
    )

    return {
        "token": access_token,
        "expire_time": expire_time,
    }
