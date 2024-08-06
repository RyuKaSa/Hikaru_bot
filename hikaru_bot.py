import numpy as np
import tensorflow as tf
import chess

# Function to convert board to features
def board_to_features(board):
    features = np.zeros((8, 8, 12), dtype=np.float32)
    for i in range(64):
        piece = board.piece_at(i)
        if piece:
            features[i // 8, i % 8, piece.piece_type - 1 + (6 if piece.color == chess.BLACK else 0)] = 1
    return features

# Function to convert model prediction back to move
def predict_move(board, model, move_encoder):
    features = board_to_features(board)
    features = np.expand_dims(features, axis=0)
    preds = model.predict(features, verbose=0)
    sorted_indices = np.argsort(preds[0])[::-1]  # Indices of moves sorted by probability
    
    for move_idx in sorted_indices:
        move_uci = [uci for uci, idx in move_encoder.items() if idx == move_idx][0]
        move = chess.Move.from_uci(move_uci)
        if move in board.legal_moves:
            return move
    
    return None  # If no legal move is found

# Load the model
model = tf.keras.models.load_model('hikaru_chess_model.h5')

# Load the move encoder
move_encoder_classes = np.load('move_encoder_classes.npy', allow_pickle=True)
move_encoder = {uci: idx for idx, uci in enumerate(move_encoder_classes)}

# Set up the board
board = chess.Board()

# Function to print the board
def print_board(board):
    print(board)

# Main loop to play against the model
bot_last_move = None

while not board.is_game_over():
    print_board(board)
    if bot_last_move:
        print(f"Bot's last move: {bot_last_move}")
    human_move = input("Enter your move in UCI format (e.g., e2e4): ")
    
    try:
        move = chess.Move.from_uci(human_move)
        if move in board.legal_moves:
            board.push(move)
        else:
            print("Illegal move, try again.")
            continue
    except:
        print("Invalid input, try again.")
        continue
    
    if board.is_game_over():
        break
    
    # Model's turn
    model_move = predict_move(board, model, move_encoder)
    if model_move is None:
        print("Model could not find a legal move. Game over.")
        break
    board.push(model_move)
    bot_last_move = model_move.uci()

print_board(board)
result = board.result()
print(f"Game over. Result: {result}")