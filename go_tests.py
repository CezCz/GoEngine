import numpy as np
import unittest
import go
from go import GameState, SMALL_BOARD, EMPTY, Coord, BLACK, WHITE

EMPTY_BOARD = np.zeros(SMALL_BOARD)


class GoEngineTest(unittest.TestCase):

    def test_new_game_starts_empty(self):
        game = GameState.get_new_game_state(SMALL_BOARD)
        np.testing.assert_array_equal(game.board, np.zeros(SMALL_BOARD))

    def test_player_can_play_a_move(self):
        game = GameState.get_new_game_state(SMALL_BOARD)
        board = np.copy(EMPTY_BOARD)
        board[0][0] = BLACK

        game = go.play_move(game, Coord._make((0, 0)), BLACK)

        np.testing.assert_array_equal(game.board, board)

    def test_history_records_after_playing_a_move(self):
        game = GameState.get_new_game_state(SMALL_BOARD)

        game = go.play_move(game, Coord._make((0, 0)), BLACK)

        self.assertEqual(len(game.history), 1)
        np.testing.assert_array_equal(game.history[0], EMPTY_BOARD)

    def test_history_records_after_playing_two_moves(self):
        game = GameState.get_new_game_state(SMALL_BOARD)
        board_first_move = np.zeros(SMALL_BOARD)
        board_first_move[0][0] = BLACK

        game = go.play_move(game, Coord._make((0, 0)))
        game = go.play_move(game, Coord._make((0, 1)))

        self.assertEqual(len(game.history), 2)
        np.testing.assert_array_equal(game.history[0], EMPTY_BOARD)
        np.testing.assert_array_equal(game.history[1], board_first_move)

    def test_move_is_incremented(self):
        game = GameState.get_new_game_state(SMALL_BOARD)
        self.assertEqual(game.moves, 0)

        game = go.play_move(game, Coord._make((0, 0)), BLACK)

        self.assertEqual(game.moves, 1)

    def test_new_game_current_player_black(self):
        game = GameState.get_new_game_state(SMALL_BOARD)
        self.assertEqual(game.current_player, BLACK)

    def test_proper_stone_is_played_if_not_indicated(self):
        game = GameState.get_new_game_state(SMALL_BOARD)
        game = go.play_move(game, Coord._make((0, 0)))
        self.assertEqual(game.board[0][0], BLACK)
        game = go.play_move(game, Coord._make((0, 1)))
        self.assertEqual(game.board[0][1], WHITE)

    def test_current_player_alternates(self):
        game = GameState.get_new_game_state(SMALL_BOARD)
        self.assertEqual(game.current_player, BLACK)
        game = go.play_move(game, Coord._make((0, 0)))
        self.assertEqual(game.current_player, WHITE)

    def test_stone_can_be_captured_middle(self):
        game = GameState.get_new_game_state(SMALL_BOARD)
        game = go.play_move(game, Coord._make((4, 4)), BLACK)
        game = go.play_move(game, Coord._make((4, 5)), WHITE)
        game = go.play_move(game, Coord._make((4, 3)), WHITE)
        game = go.play_move(game, Coord._make((5, 4)), WHITE)
        game = go.play_move(game, Coord._make((3, 4)), WHITE)
        self.assertEqual(game.captures[WHITE], 1)
        self.assertEqual(game.board[4][4], EMPTY)

    def test_stone_can_be_captured_side(self):
        game = GameState.get_new_game_state(SMALL_BOARD)
        game = go.play_move(game, Coord._make((0, 4)), BLACK)
        game = go.play_move(game, Coord._make((0, 5)), WHITE)
        game = go.play_move(game, Coord._make((0, 3)), WHITE)
        game = go.play_move(game, Coord._make((1, 4)), WHITE)
        self.assertEqual(game.captures[WHITE], 1)
        self.assertEqual(game.board[0][4], EMPTY)

    def test_stone_can_be_captured_corner(self):
        game = GameState.get_new_game_state(SMALL_BOARD)
        game = go.play_move(game, Coord._make((0, 0)), BLACK)
        game = go.play_move(game, Coord._make((0, 1)), WHITE)
        game = go.play_move(game, Coord._make((1, 0)), WHITE)
        self.assertEqual(game.captures[WHITE], 1)
        self.assertEqual(game.board[0][4], EMPTY)

    def test_move_cannot_be_placed_on_taken_place(self):
        with self.assertRaises(Exception):
            game = GameState.get_new_game_state(SMALL_BOARD)
            game = go.play_move(game, Coord._make((0, 0)))
            go.play_move(game, Coord._make((0, 0)))

    def test_group_can_be_captured_middle(self):
        game = GameState.get_new_game_state(SMALL_BOARD)
        game = go.play_move(game, Coord._make((4, 4)), BLACK)
        game = go.play_move(game, Coord._make((4, 5)), BLACK)
        game = go.play_move(game, Coord._make((5, 4)), BLACK)
        game = go.play_move(game, Coord._make((3, 4)), WHITE)
        game = go.play_move(game, Coord._make((3, 5)), WHITE)
        game = go.play_move(game, Coord._make((4, 3)), WHITE)
        game = go.play_move(game, Coord._make((4, 6)), WHITE)
        game = go.play_move(game, Coord._make((5, 3)), WHITE)
        game = go.play_move(game, Coord._make((5, 5)), WHITE)
        game = go.play_move(game, Coord._make((6, 4)), WHITE)
        self.assertEqual(game.captures[WHITE], 3)
        self.assertEqual(game.board[4][4], EMPTY)
        self.assertEqual(game.board[4][5], EMPTY)
        self.assertEqual(game.board[5][4], EMPTY)

    def test_group_can_be_captured_side(self):
        game = GameState.get_new_game_state(SMALL_BOARD)
        game = go.play_move(game, Coord._make((0, 4)), BLACK)
        game = go.play_move(game, Coord._make((0, 5)), BLACK)
        game = go.play_move(game, Coord._make((0, 6)), WHITE)
        game = go.play_move(game, Coord._make((0, 3)), WHITE)
        game = go.play_move(game, Coord._make((1, 4)), WHITE)
        game = go.play_move(game, Coord._make((1, 5)), WHITE)
        self.assertEqual(game.captures[WHITE], 2)
        self.assertEqual(game.board[0][4], EMPTY)
        self.assertEqual(game.board[0][5], EMPTY)

    def test_group_can_be_captured_corner(self):
        game = GameState.get_new_game_state(SMALL_BOARD)
        game = go.play_move(game, Coord._make((0, 0)), BLACK)
        game = go.play_move(game, Coord._make((0, 1)), BLACK)
        game = go.play_move(game, Coord._make((1, 0)), BLACK)
        game = go.play_move(game, Coord._make((0, 2)), WHITE)
        game = go.play_move(game, Coord._make((2, 0)), WHITE)
        game = go.play_move(game, Coord._make((1, 1)), WHITE)
        self.assertEqual(game.captures[WHITE], 3)
        self.assertEqual(game.board[0][0], EMPTY)
        self.assertEqual(game.board[0][1], EMPTY)
        self.assertEqual(game.board[1][0], EMPTY)

    def test_count_score(self):
        game = GameState.get_new_game_state(SMALL_BOARD)
        game = go.play_move(game, Coord._make((1, 0)), BLACK)
        game = go.play_move(game, Coord._make((1, 1)), BLACK)
        game = go.play_move(game, Coord._make((1, 2)), BLACK)
        game = go.play_move(game, Coord._make((1, 3)), BLACK)
        game = go.play_move(game, Coord._make((1, 4)), BLACK)
        game = go.play_move(game, Coord._make((1, 5)), BLACK)
        game = go.play_move(game, Coord._make((1, 6)), BLACK)
        game = go.play_move(game, Coord._make((1, 7)), BLACK)
        game = go.play_move(game, Coord._make((1, 8)), BLACK)
        game = go.play_move(game, Coord._make((2, 0)), WHITE)
        game = go.play_move(game, Coord._make((2, 1)), WHITE)
        game = go.play_move(game, Coord._make((2, 2)), WHITE)
        game = go.play_move(game, Coord._make((2, 3)), WHITE)
        game = go.play_move(game, Coord._make((2, 4)), WHITE)
        game = go.play_move(game, Coord._make((2, 5)), WHITE)
        game = go.play_move(game, Coord._make((2, 6)), WHITE)
        game = go.play_move(game, Coord._make((2, 7)), WHITE)
        game = go.play_move(game, Coord._make((2, 8)), WHITE)
        self.assertEqual(go.get_winner(game), (WHITE, 50.5))

    def test_count_score_with_dames(self):
        game = GameState.get_new_game_state(SMALL_BOARD)
        game = go.play_move(game, Coord._make((3, 0)), BLACK)
        game = go.play_move(game, Coord._make((3, 1)), BLACK)
        game = go.play_move(game, Coord._make((3, 2)), BLACK)
        game = go.play_move(game, Coord._make((3, 3)), BLACK)
        game = go.play_move(game, Coord._make((3, 4)), BLACK)
        game = go.play_move(game, Coord._make((3, 5)), BLACK)
        game = go.play_move(game, Coord._make((3, 6)), BLACK)
        game = go.play_move(game, Coord._make((3, 7)), BLACK)
        game = go.play_move(game, Coord._make((3, 8)), BLACK)
        game = go.play_move(game, Coord._make((4, 0)), WHITE)
        game = go.play_move(game, Coord._make((4, 1)), WHITE)
        game = go.play_move(game, Coord._make((4, 2)), WHITE)
        game = go.play_move(game, Coord._make((4, 3)), WHITE)
        game = go.play_move(game, Coord._make((5, 3)), WHITE)
        game = go.play_move(game, Coord._make((5, 4)), WHITE)
        game = go.play_move(game, Coord._make((5, 5)), WHITE)
        game = go.play_move(game, Coord._make((5, 6)), WHITE)
        game = go.play_move(game, Coord._make((5, 7)), WHITE)
        game = go.play_move(game, Coord._make((5, 8)), WHITE)
        self.assertEqual(go.get_winner(game), (WHITE, 9.5))

    def test_cannot_capture_own_stone_in_corner(self):
        game = GameState.get_new_game_state(SMALL_BOARD)
        game = go.play_move(game, Coord._make((0, 0)), BLACK)
        game = go.play_move(game, Coord._make((0, 1)), BLACK)
        game = go.play_move(game, Coord._make((0, 2)), BLACK)
        self.assertEqual(game.board[0][0], BLACK)
        self.assertEqual(game.board[0][1], BLACK)
        self.assertEqual(game.board[0][2], BLACK)

    def test_cannot_capture_own_stone_on_side(self):
        game = GameState.get_new_game_state(SMALL_BOARD)
        game = go.play_move(game, Coord._make((0, 4)), BLACK)
        game = go.play_move(game, Coord._make((1, 4)), BLACK)
        game = go.play_move(game, Coord._make((0, 5)), BLACK)
        game = go.play_move(game, Coord._make((0, 3)), BLACK)
        self.assertEqual(game.board[0][4], BLACK)
        self.assertEqual(game.board[1][4], BLACK)
        self.assertEqual(game.board[0][5], BLACK)
        self.assertEqual(game.board[0][3], BLACK)

    def test_cannot_capture_own_stone_center(self):
        game = GameState.get_new_game_state(SMALL_BOARD)
        game = go.play_move(game, Coord._make((4, 4)), BLACK)
        game = go.play_move(game, Coord._make((4, 5)), BLACK)
        game = go.play_move(game, Coord._make((4, 3)), BLACK)
        game = go.play_move(game, Coord._make((3, 4)), BLACK)
        game = go.play_move(game, Coord._make((5, 4)), BLACK)
        self.assertEqual(game.board[4][4], BLACK)
        self.assertEqual(game.board[4][5], BLACK)
        self.assertEqual(game.board[4][3], BLACK)
        self.assertEqual(game.board[3][4], BLACK)
        self.assertEqual(game.board[5][4], BLACK)
