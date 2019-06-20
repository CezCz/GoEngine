import numpy as np
from copy import copy
from collections import deque
from enum import Enum
from functools import lru_cache

WHITE = 2
BLACK = 1
EMPTY = 0
PASS = None

X = 0
Y = 1

SMALL_BOARD = (9, 9)
MEDIUM_BOARD = (13, 13)
BIG_BOARD = (19, 19)


class GameStatus(Enum):
    ON_GOING = "ON_GOING"
    ENDED = "ENDED"


class GameState:

    def __init__(self, shape):
        self.shape = shape
        self.current_player = BLACK
        self.board = np.zeros(shape)
        self.history = []
        self.moves_history = []
        self.moves = 0
        self.komi = 5.5
        self.status = GameStatus.ON_GOING

    @staticmethod
    def get_new_game_state(shape):
        return GameState(shape)

    def __str__(self):
        return str(self.board)


def play_move(game_state, move, color=None):
    if color is None:
        color = game_state.current_player

    if is_valid(game_state, move, color):
        do_move(game_state, move, color)
        check_end_game(game_state)
    else:
        raise IllegalMoveException("Move is not valid")

    return game_state


__end_game_condition = [PASS, PASS]


def check_end_game(game_state):
    if game_state.moves_history[:-2] == __end_game_condition:
        game_state.status = GameStatus.ENDED


def is_valid(game_state, move, color):
    if not is_within_bounds(move, game_state.board.shape):
        return False
    if not is_place_free(game_state, move):
        return False
    if is_suicide(game_state, move, color):
        return False
    if is_repetition(game_state, move, color):
        return False

    return True


def is_suicide(game_state, move, color):
    board = game_state.board
    board[move] = color
    checked = set()
    affected_points = list((move,))
    affected_points.extend(get_neighbour_points(move, board.shape))
    for current_coord in affected_points:
        if current_coord in checked:
            continue
        if board[current_coord] != color:
            continue

        liberties, group = get_stone_liberty_count(board, current_coord, color)
        checked.update(group)
        if liberties == 1:
            board[move] = EMPTY
            return False
    board[move] = EMPTY
    return True


def is_repetition(game_state, move, color):
    start_point = 0 if color == BLACK else 1
    if move not in game_state.moves_history[start_point::2]:
        return False

    do_move(game_state, move, color)
    color_history = game_state.history[start_point::2]
    current_board = game_state.board

    if np.equal(color_history, current_board).all((1, 2)).any():
        undo_move(game_state)
        return True

    undo_move(game_state)
    return False


def get_winner(game_state):
    # Assumes no dead groups on board
    board = game_state.board
    board_width, board_length = board.shape
    black_count = np.sum(board == BLACK)
    white_count = np.sum(board == WHITE)
    white_count += game_state.komi

    for x in range(board_width):
        for y in range(board_length):
            point = board[x, y]
            current_point = (x, y)
            if point == EMPTY:
                if is_solely_surrounded_by(board, BLACK, current_point):
                    black_count += 1
                #     Optimization!
                #     If one empty point is solely surrounded then if it has any empty neighbours they are also solely surrounded!
                elif is_solely_surrounded_by(board, WHITE, current_point):
                    white_count += 1

    points_difference = abs(black_count - white_count)
    if black_count > white_count:
        winner = BLACK
    else:
        winner = WHITE
    return winner, points_difference


def is_solely_surrounded_by(board, color, point):
    checked = {point}
    affected_points = get_neighbour_points(point, board.shape)
    points_to_check = deque(affected_points)
    opposite_color = get_opponent_color(color)
    while points_to_check:
        point_to_check = points_to_check.pop()
        current_point = board[point_to_check]
        if point_to_check in checked:
            continue
        if current_point == opposite_color:
            return False
        if current_point == EMPTY:
            points_to_check.extend(get_neighbour_points(point_to_check, board.shape))
        checked.add(point_to_check)
    return True


def get_legal_moves(game_state):
    board = game_state.board
    board_width, board_length = board.shape
    legal_moves = []
    # cdef int x, y
    for x in range(board_width):
        for y in range(board_length):
            move_candidate = (x, y)
            if is_valid(game_state, move_candidate, game_state.current_player):
                legal_moves.append(move_candidate)

    return legal_moves


def alternate_current_player(game_state):
    game_state.current_player = get_opponent_color(game_state.current_player)


def remove_captured_stones(game_state, move, color):
    board = game_state.board
    checked = set()
    affected_points = list((move,))
    affected_points.extend(get_neighbour_points(move, board.shape))
    for current_coord in affected_points:
        if current_coord in checked:
            continue
        x, y = current_coord
        if board[x, y] != color:
            continue

        liberties, group = get_stone_liberty_count(board, current_coord, color)
        checked.update(group)
        if liberties == 0:
            for coord in group:
                board[coord] = EMPTY


def get_stone_liberty_count(board, starting_coord, color):
    checked = set()
    queue = deque((starting_coord,))
    while queue:
        coord = queue.pop()
        points = get_neighbour_points(coord, board.shape)
        checked.add(coord)
        for point in points:
            board_point = board[point]
            if EMPTY == board_point:
                # Short circuit
                # Only concerned if more than one liberty
                return 1, checked
            if color != board_point:
                continue
            if point in checked:
                continue
            queue.append(point)
    return 0, checked


@lru_cache(400)
def get_neighbour_points(coord, board_shape):
    x, y = coord[X], coord[Y]
    left = (x - 1, y)
    right = (x + 1, y)
    up = (x, y - 1)
    down = (x, y + 1)
    point_candidates = [left, right, up, down]

    points = set()
    for candidate in point_candidates:
        if is_within_bounds(candidate, board_shape):
            points.add(candidate)

    return tuple(points)


def is_within_bounds(coord, board_shape):
    size_x, size_y = board_shape
    return 0 <= coord[X] < size_x and 0 <= coord[Y] < size_y


def is_place_free(game_state, move):
    return game_state.board[move] == EMPTY or move is PASS


def get_opponent_color(color):
    return BLACK if color == WHITE else WHITE


def do_move(game_state, move, color):
    opponent = get_opponent_color(color)
    game_state.moves_history.append(move)
    game_state.history.append(copy(game_state.board))
    place_stone(game_state, move, color)
    remove_captured_stones(game_state, move, opponent)
    game_state.moves += 1
    alternate_current_player(game_state)


def place_stone(game_state, move, color):
    if move is not PASS:
        game_state.board[move] = color


def undo_move(game_state):
    game_state.moves_history.pop()
    game_state.board = game_state.history.pop()
    game_state.moves -= 1
    alternate_current_player(game_state)


class IllegalMoveException(Exception):
    pass
