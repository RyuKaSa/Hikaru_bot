from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import logging

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Mapping of pieces to their indices in the 12-channel tensor
piece_map = {
    'p': 0, 'r': 1, 'n': 2, 'b': 3, 'q': 4, 'k': 5,  # Black pieces
    'P': 6, 'R': 7, 'N': 8, 'B': 9, 'Q': 10, 'K': 11  # White pieces
}

# Function to convert position to indices
def position_to_indices(position):
    rank = 8 - int(position[1])
    file = int(position[0]) - 1
    return rank, file

# Function to convert board state to 8x8x12 tensor
def board_state_to_features(board_state):
    features = np.zeros((8, 8, 12), dtype=np.float32)
    for item in board_state:
        position = item['position']
        piece = item['piece']
        rank, file = position_to_indices(position)
        if piece in piece_map:
            features[rank, file, piece_map[piece]] = 1
    return features

# Function to convert tensor to human-readable board state
def tensor_to_human_readable(features):
    piece_symbols = ['p', 'r', 'n', 'b', 'q', 'k', 'P', 'R', 'N', 'B', 'Q', 'K']
    board_state = [['.' for _ in range(8)] for _ in range(8)]
    
    for rank in range(8):
        for file in range(8):
            for piece_index in range(12):
                if features[rank, file, piece_index] == 1:
                    board_state[rank][file] = piece_symbols[piece_index]
    
    for rank in board_state:
        print(' '.join(rank))

@app.route('/update_board', methods=['POST'])
def update_board_route():
    try:
        board_state = request.get_json()
        logging.debug(f"Received board state: {board_state}")
        
        # Convert the board state to features
        features = board_state_to_features(board_state)
        logging.debug(f"Board features: {features}")
        
        # Print the human-readable board state
        tensor_to_human_readable(features)
        
        return jsonify({"status": "success", "features_shape": features.shape}), 200
    except Exception as e:
        logging.error(f"Error in /update_board route: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
