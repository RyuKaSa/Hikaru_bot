import numpy as np
import chess
import tensorflow as tf

def board_to_features_from_string(board_str):
    rows = board_str.strip().split("\n")
    features = np.zeros((8, 8, 12), dtype=np.float32)
    
    piece_to_index = {
        'P': 0, 'N': 1, 'B': 2, 'R': 3, 'Q': 4, 'K': 5,
        'p': 6, 'n': 7, 'b': 8, 'r': 9, 'q': 10, 'k': 11,
        '.': None
    }
    
    for row_idx, row in enumerate(rows):
        pieces = row.split()
        for col_idx, piece in enumerate(pieces):
            if piece != '.':
                features[row_idx, col_idx, piece_to_index[piece]] = 1.0
                
    return features

# Example board state
board_str = """
r . b q k b n r
p p p . p p p p
. . n . . . . .
. . . p . . . .
. . . . . . P .
. . . . . N . .
P P P P P P . P
R N B Q K B . R
"""

# Convert the board string to features
features = board_to_features_from_string(board_str)
print(features.shape)  # Should print (8, 8, 12)

# Load the saved model
model = tf.keras.models.load_model('hikaru_chess_model.h5')

# Load the move encoder
move_encoder_keys = np.load('move_encoder_classes.npy', allow_pickle=True)
move_encoder = {uci: idx for idx, uci in enumerate(move_encoder_keys)}

def predict_move(board_str, model, move_encoder):
    features = board_to_features_from_string(board_str)
    features = np.expand_dims(features, axis=0)
    preds = model.predict(features)
    sorted_indices = np.argsort(preds[0])[::-1]  # Indices of moves sorted by probability
    
    for move_idx in sorted_indices:
        move_uci = [uci for uci, idx in move_encoder.items() if idx == move_idx][0]
        move = chess.Move.from_uci(move_uci)
        
        # Create a chess board to validate legal moves
        board = chess.Board()
        # Set up the board from the provided board_str
        rows = board_str.strip().split("\n")
        board.clear()
        for row_idx, row in enumerate(rows):
            pieces = row.split()
            for col_idx, piece in enumerate(pieces):
                if piece != '.':
                    piece_type = chess.PIECE_SYMBOLS.index(piece.lower())
                    color = chess.BLACK if piece.islower() else chess.WHITE
                    board.set_piece_at(chess.square(col_idx, 7 - row_idx), chess.Piece(piece_type, color))
        
        if move in board.legal_moves:
            return move
    
    return None  # If no legal move is found

# Predict the move
predicted_move = predict_move(board_str, model, move_encoder)
print(predicted_move)  # Should print the predicted move in UCI format
