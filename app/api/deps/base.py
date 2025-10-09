from typing import Generator, AsyncGenerator
from app.db.session import async_session
from fastapi.security import HTTPBearer
from fastapi import Depends, HTTPException, status
import jwt
from app.core import security
from app.core.config import settings
from app import schemas, crud


async def get_db_async() -> AsyncGenerator:
    async with async_session() as db:
        yield db
        await db.commit()
        # This is a clean way to ensure all pending changes are committed before the session is closed.


async def get_current_user(authorization: str = Depends(HTTPBearer())):
    try:
        token = authorization.credentials
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = schemas.TokenPayload(**payload)

    except jwt.ExpiredSignatureError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
    except IndexError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token prefix missing",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication Failed",
        )
    user = await crud.player.get_with_cache(db=None, id=token_data.user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user
