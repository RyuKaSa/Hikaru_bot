from flask import Flask, request, jsonify
from flask_cors import CORS
import chess

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

board = chess.Board()

def update_board(board_state):
    board.clear()
    piece_map = {
        'p': chess.PAWN,
        'r': chess.ROOK,
        'n': chess.KNIGHT,
        'b': chess.BISHOP,
        'q': chess.QUEEN,
        'k': chess.KING
    }

    for item in board_state:
        position = item['position']
        piece_type = item['piece'].lower()
        piece_color = chess.WHITE if item['piece'].isupper() else chess.BLACK
        piece = chess.Piece(piece_map[piece_type], piece_color)
        square = chess.parse_square(position_to_chess_square(position))
        board.set_piece_at(square, piece)

def position_to_chess_square(position):
    file = chr(ord('a') + (int(position) % 10) - 1)
    rank = position[0]
    return f"{file}{rank}"

def board_to_string(board):
    board_string = ""
    for file in range(7, -1, -1):  # Iterate from file 7 (h) to 0 (a) for horizontal flip
        for rank in range(1, 9):  # Iterate from rank 1 to 8 for correct orientation
            square = chess.square(file, rank - 1)
            piece = board.piece_at(square)
            if piece:
                board_string += piece.symbol()
            else:
                board_string += "."
            board_string += " "
        board_string = board_string.strip() + "\n"
    return board_string.strip()

@app.route('/update_board', methods=['POST'])
def update_board_route():
    board_state = request.get_json()
    update_board(board_state)
    print("Latest board state:\n" + board_to_string(board))  # Print the board in the desired format
    return jsonify({"status": "success"}), 200

@app.route('/get_board', methods=['GET'])
def get_board():
    return jsonify({"board": board.fen()}), 200

if __name__ == '__main__':
    app.run(debug=True)
