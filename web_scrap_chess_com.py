import csv
import requests
import time

# Add headers
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
    'Referer': 'https://www.chess.com/'
}

# Function to fetch JSON data from a URL
def fetch_json(url):
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

# Function to clean the PGN
def clean_pgn(pgn):
    moves = pgn.split('\n\n')[1]
    moves = moves.replace('{[%clk ', '')
    moves = ' '.join(moves.split()).replace('} ', '')
    moves = moves.split(' ')[:-1]  # remove the game result (e.g., "1-0", "0-1", "1/2-1/2")
    
    # Remove timestamps
    cleaned_moves = []
    for move in moves:
        if ']' in move:
            move = move.split(']')[1]
        cleaned_moves.append(move)
        
    return ' '.join(cleaned_moves)

# Function to process a single game
def process_game(game):
    if 'pgn' not in game:
        return None, None, None

    pgn = game['pgn']
    white_player = game['white']['username']
    black_player = game['black']['username']
    white_result = game['white']['result']
    black_result = game['black']['result']

    # Determine the result for Hikaru
    if white_player.lower() == 'hikaru':
        hikaru_color = 'white'
        if white_result == 'win':
            hikaru_result = 'win'
        elif white_result in ['resigned', 'timeout', 'checkmated']:
            hikaru_result = 'lose'
        elif white_result == 'agreed':
            hikaru_result = 'draw'
        else:
            hikaru_result = 'lose'
    else:
        hikaru_color = 'black'
        if black_result == 'win':
            hikaru_result = 'win'
        elif black_result in ['resigned', 'timeout', 'checkmated']:
            hikaru_result = 'lose'
        elif black_result == 'agreed':
            hikaru_result = 'draw'
        else:
            hikaru_result = 'lose'

    trimmed_pgn = clean_pgn(pgn)
    return hikaru_result, hikaru_color, trimmed_pgn

# Function to fetch all games from a list of archive URLs
def fetch_all_games(archive_urls):
    all_games = []
    for url in archive_urls:
        try:
            games = fetch_json(url)['games']
            all_games.extend(games)
            print(f"Fetched {len(games)} games from {url}")
        except Exception as e:
            print(f"Failed to fetch games from {url}: {e}")
        # Sleep to avoid hitting rate limits
        time.sleep(1)
    return all_games

# Function to write games to a CSV file
def write_games_to_csv(games, filename):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Result', 'Color', 'Moves'])
        for game in games:
            hikaru_result, hikaru_color, moves = process_game(game)
            if hikaru_result and hikaru_color and moves:
                writer.writerow([hikaru_result, hikaru_color, moves])

# URL to fetch all game archives for Hikaru
archives_url = "https://api.chess.com/pub/player/hikaru/games/archives"

# Fetch archive URLs
archives_data = fetch_json(archives_url)
archive_urls = archives_data['archives']

# Fetch all games
all_games = fetch_all_games(archive_urls)

# Write games to CSV
write_games_to_csv(all_games, 'hikaru_all_games.csv')

print(f"Total number of games: {len(all_games)}")