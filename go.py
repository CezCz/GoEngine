import numpy as np
from copy import copy
from collections import namedtuple, deque
from enum import Enum

WHITE = 2
BLACK = 1
EMPTY = 0
PASS = None

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
        self.captures = {
            BLACK: 0,
            WHITE: 0
        }
        self.moves = 0
        self.komi = 5.5
        self.status = GameStatus.ON_GOING

    @staticmethod
    def get_new_game_state(shape):
        return GameState(shape)

    def __str__(self):
        return str(self.board)


Coord = namedtuple('Coord', ['x', 'y'])


def play_move(game_state, move, color=None):
    if color is None:
        is_normal_move = True
        color = game_state.current_player
    else:
        is_normal_move = False

    if is_valid(game_state, move, color):
        opponent = get_opponent_color(color)
        do_move(game_state, move, color)
        remove_captured_stones(game_state, move, opponent)
        remove_captured_stones(game_state, move, color)
    else:
        raise Exception("Move is not valid")

    if is_normal_move:
        alternate_current_player(game_state)

    return game_state


def is_valid(game_state, move, color):
    if not is_within_bounds(move, game_state.board.shape):
        return False
    if not is_place_free(game_state, move):
        return False

    do_move(game_state, move, color)

    start_point = 0 if color == BLACK else 1
    color_history = game_state.history[start_point::2]
    current_board = game_state.board
    if np.equal(color_history, current_board).all((1, 2)).any():
        undo_move(game_state)
        return False
    undo_move(game_state)

    return True


def get_winner(game_state):
    # Assume no dead groups on board
    board = game_state.board
    board_width, board_length = board.shape
    black_count = np.sum(board == BLACK)
    white_count = np.sum(board == WHITE)
    black_count += game_state.captures[BLACK]
    white_count += game_state.captures[WHITE]
    white_count += game_state.komi

    for x in range(board_width):
        for y in range(board_length):
            point = board[x][y]
            current_point = Coord._make((x, y))
            if point == EMPTY:
                if is_solely_surrounded_by(BLACK, current_point, board):
                    black_count += 1
                elif is_solely_surrounded_by(WHITE, current_point, board):
                    white_count += 1

    points_difference = abs(black_count - white_count)
    if black_count > white_count:
        winner = BLACK
    else:
        winner = WHITE
    return winner, points_difference


def is_solely_surrounded_by(color, point, board):
    # Tries to find a path, to both opposite color
    checked = {point}
    affected_points = get_neighbour_points(point, board.shape)
    points_to_check = deque(affected_points)
    opposite_color = get_opponent_color(color)
    while points_to_check:
        point_to_check = points_to_check.pop()
        current_point = board[point_to_check.x][point_to_check.y]
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
    for x in range(board_width):
        for y in range(board_length):
            move_candidate = Coord._make((x, y))
            if is_valid(game_state, move_candidate, game_state.current_player):
                legal_moves.append(move_candidate)

    return legal_moves


def alternate_current_player(game_state):
    game_state.current_player = get_opponent_color(game_state.current_player)


def remove_captured_stones(game_state, move, color):
    board = game_state.board
    affected_points = get_neighbour_points(move, board.shape)
    affected_points.add(move)
    for current_coord in affected_points:
        x, y = current_coord
        if board[x][y] != color:
            continue

        liberties, group = get_stone_libery_count(current_coord, board, color)
        group_size = len(group)
        if liberties == 0:
            for coord in group:
                board[coord.x][coord.y] = EMPTY
            opponent = get_opponent_color(color)
            game_state.captures[opponent] += group_size


def get_opponent_color(color):
    return BLACK if color == WHITE else WHITE


def get_stone_libery_count(starting_coord, board, color):
    checked = set()
    queue = deque((starting_coord,))
    liberties = 0
    while queue:
        coord = queue.pop()
        points = get_neighbour_points(coord, board.shape)
        checked.add(coord)
        for point in points:
            board_point = board[point.x][point.y]
            if board_point == EMPTY:
                liberties += 1
                # Short circuit
                # Only concerned if more than one liberty
                return liberties, checked
            if board_point == color and point not in checked:
                queue.append(point)

    return liberties, checked


def get_neighbour_points(coord, board_shape):
    x, y = coord.x, coord.y
    left = Coord._make((x - 1, y))
    right = Coord._make((x + 1, y))
    up = Coord._make((x, y - 1))
    down = Coord._make((x, y + 1))
    point_candidates = [left, right, up, down]

    points = set()
    for candidate in point_candidates:
        if is_within_bounds(candidate, board_shape):
            points.add(candidate)

    return points


def is_within_bounds(coord, board_shape):
    size_x, size_y = board_shape
    return 0 <= coord.x < size_x and 0 <= coord.y < size_y


def is_place_free(game_state, move):
    return game_state.board[move.x][move.y] == EMPTY or move is PASS


def do_move(game_state, move, color):
    game_state.moves_history.append(move)
    game_state.history.append(copy(game_state.board))
    place_stone(game_state, move, color)
    game_state.moves += 1


def place_stone(game_state, move, color):
    if move is not PASS:
        game_state.board[move.x][move.y] = color


def remove_stone(game_state, move):
    if move is not PASS:
        game_state.board[move.x][move.y] = EMPTY


def undo_move(game_state):
    last_move = game_state.moves_history.pop()
    game_state.history.pop()
    remove_stone(game_state, last_move)
    game_state.moves -= 1
