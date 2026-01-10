def display_board(board):
    """Display the current game board."""
    print()
    print(f" {board[0]} | {board[1]} | {board[2]} ")
    print("-----------")
    print(f" {board[3]} | {board[4]} | {board[5]} ")
    print("-----------")
    print(f" {board[6]} | {board[7]} | {board[8]} ")
    print()


def check_winner(board):
    """Check if there's a winner. Returns 'X', 'O', or None."""
    # All possible winning combinations
    winning_combos = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
        [0, 4, 8], [2, 4, 6]              # Diagonals
    ]

    for combo in winning_combos:
        if board[combo[0]] == board[combo[1]] == board[combo[2]] and board[combo[0]] in ['X', 'O']:
            return board[combo[0]]

    return None


def is_board_full(board):
    """Check if the board is full (draw condition)."""
    return all(cell in ['X', 'O'] for cell in board)


def get_player_move(board, player):
    """Get a valid move from the current player."""
    while True:
        try:
            move = input(f"Player {player}, enter your move (1-9): ")
            move = int(move) - 1

            if move < 0 or move > 8:
                print("Invalid input. Please enter a number between 1 and 9.")
                continue

            if board[move] in ['X', 'O']:
                print("That position is already taken. Try again.")
                continue

            return move
        except ValueError:
            print("Invalid input. Please enter a number between 1 and 9.")
        except (KeyboardInterrupt, EOFError):
            print("\nGame interrupted. Goodbye!")
            exit(0)


def main():
    """Main game loop."""
    print("Welcome to Tic-Tac-Toe!")
    print("Positions are numbered 1-9:")
    print(" 1 | 2 | 3 ")
    print("-----------")
    print(" 4 | 5 | 6 ")
    print("-----------")
    print(" 7 | 8 | 9 ")

    # Initialize the board with position numbers
    board = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
    current_player = 'X'

    while True:
        display_board(board)

        # Get player move
        move = get_player_move(board, current_player)
        board[move] = current_player

        # Check for winner
        winner = check_winner(board)
        if winner:
            display_board(board)
            print(f"Player {winner} wins!")
            break

        # Check for draw
        if is_board_full(board):
            display_board(board)
            print("It's a draw!")
            break

        # Switch players
        current_player = 'O' if current_player == 'X' else 'X'


if __name__ == "__main__":
    main()
