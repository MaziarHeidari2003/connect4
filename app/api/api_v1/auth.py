from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app import schemas, crud
from fastapi.encoders import jsonable_encoder
from app.core import security
from app.api import deps

router = APIRouter()


@router.post("/register")
async def register(
    _input: schemas.PlayerRegister,
    db: AsyncSession = Depends(deps.get_db_async),
):
    player = await crud.player.get_by_email(db=db, email=_input.email)
    if player:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Player with this email already exists",
        )
    player = await crud.player.create(db=db, obj_in=_input)
    player_data = jsonable_encoder(player)
    token_data = security.generate_access_token(player_data)
    player_data["access_token"] = token_data["token"]
    player_data["expire_time"] = token_data["expire_time"]
    login_result = schemas.LoginOutput(**player_data)
    return login_result


@router.post("/login")
async def login_access_token(
    login_data: schemas.PlayerLogin,
    db: AsyncSession = Depends(deps.get_db_async),
) -> schemas.LoginOutput:
    player = await crud.player.get_by_email(db=db, email=login_data.email)
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found, Please register first",
        )
    player_data = jsonable_encoder(player)
    token_data = security.generate_access_token(player_data)
    player_data["access_token"] = token_data["token"]
    player_data["expire_time"] = token_data["expire_time"]
    # login_result = schemas.LoginOutput(**player_data)
    # return login_result

    response = JSONResponse(
        content={"user": player_data, "expire_time": token_data["expire_time"]}
    )

    response.set_cookie(
        key="access_token",
        value=token_data["token"],
        httponly=True,
        secure=True,
        samesite="none",
        path="/",
    )

    return response
