import go
import random
from go import GameState, SMALL_BOARD


def main():
    for k in range(100):
        game = GameState.get_new_game_state(SMALL_BOARD)
        for x in range(100):
            legal_moves = go.get_legal_moves(game)
            if not legal_moves:
                break
            move = random.choice(legal_moves)
            game = go.play_move(game, move)
        winner_color, points_difference = go.get_winner(game)


if __name__ == "__main__":
    main()
