def winner_move(column_count: int, row_count: int, player_move: int, board: list):
    # vertical check
    for c in range(column_count):
        for r in range(row_count - 3):
            if all(board[c][r + i] == player_move for i in range(4)):
                return True

    # horizontal check
    for r in range(row_count):
        for c in range(column_count - 3):
            if all(board[c + i][r] == player_move for i in range(4)):
                return True

    # diagonal bottom-left -> top-right
    for c in range(column_count - 3):
        for r in range(row_count - 3):
            if all(board[c + i][r + i] == player_move for i in range(4)):
                return True

    # diagonal top-left -> bottom-right (correct indexing for rectangular boards)
    for c in range(column_count - 3):
        for r in range(3, row_count):
            if all(board[c + i][r - i] == player_move for i in range(4)):
                return True

    return False
