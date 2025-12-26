from sqlalchemy.ext.asyncio import AsyncSession
from app import schemas, crud


def winner_move(column_count: int, row_count: int, player_move: int, board: list):
    # vertically
    for c in range(column_count + 1):
        for r in range(row_count - 2):
            if (
                board[c][r] == player_move
                and board[c][r + 1] == player_move
                and board[c][r + 2] == player_move
                and board[c][r + 3] == player_move
            ):
                return True

    # horizantally
    for r in range(row_count+1):
        for c in range(column_count - 2):
            if (
                board[c][r] == player_move
                and board[c + 1][r] == player_move
                and board[c + 2][r] == player_move
                and board[c + 3][r] == player_move
            ):
                return True

    # diagonal
    for c in range(column_count - 2):
        for r in range(row_count - 2):
            if (
                board[c][r] == player_move
                and board[c + 1][r + 1] == player_move
                and board[c + 2][r + 2] == player_move
                and board[c + 3][r + 3] == player_move
            ):
                return True

    for c in range(column_count - 2):
        for r in range(row_count, 2, -1):
            if (
                board[c][r] == player_move
                and board[c + 1][r - 1] == player_move
                and board[c + 2][r - 2] == player_move
                and board[c + 3][r - 3] == player_move
            ):
                return True

    return False


async def terminate_active_game_if_exists(db: AsyncSession, player_id: int):
    active_game = await crud.game.get_active_game_for_player(db, player_id)
    if active_game:
        active_game.status = schemas.GameStatus.TERMINATED.value
        await crud.game.update(db=db, db_obj=active_game)
        return active_game
    return None
