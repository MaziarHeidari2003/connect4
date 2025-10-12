def winner_move(column_count: int, row_count: int, player_move: int, board: list):
    for c in range(column_count - 3):  
        for r in range(row_count):
            if (
                board[c][r] == player_move
                and board[c+1][r] == player_move
                and board[c+2][r] == player_move
                and board[c+3][r] == player_move
            ):
                return True

   
    for c in range(column_count):
        for r in range(row_count - 3):
            if (
                board[c][r] == player_move
                and board[c][r+1] == player_move
                and board[c][r+2] == player_move
                and board[c][r+3] == player_move
            ):
                return True

 
    for c in range(column_count - 3):
        for r in range(row_count - 3):
            if (
                board[c][r] == player_move         
                and board[c+1][r+1] == player_move 
                and board[c+2][r+2] == player_move 
                and board[c+3][r+3] == player_move
            ):
                return True


    for c in range(column_count - 3):
        for r in range(3, row_count):
            if (
                board[c][r] == player_move         
                and board[c+1][r-1] == player_move 
                and board[c+2][r-2] == player_move
                and board[c+3][r-3] == player_move 
            ):
                return True

    return False

