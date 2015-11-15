import json
import random
import string
from collections import deque
from datetime import datetime
from itertools import cycle
from flask import Flask, jsonify, request

app = Flask(__name__)

GAME_ID_LENGTH = 48
PLAYER_ID_LENGTH = 48
CARD_ID_LENGTH = 6
GAME_FILE_PATH = 'games'
SPECIAL_CARDS = ['WILD', 'WILD_DRAW_FOUR']
SPECIAL_COLOR_CARDS = ['DRAW_TWO', 'SKIP', 'REVERSE']
CARD_COLORS = ['RED', 'GREEN', 'YELLOW', 'BLUE']


def set_GAME_FILE_PATH(path):
    global GAME_FILE_PATH
    GAME_FILE_PATH = path


def get_game_path(game_id):
    return '{}/{}'.format(GAME_FILE_PATH, game_id)


def load_state(game_id):
    filepath = get_game_path(game_id)
    try:
        with open(filepath) as game_file:
            game_data = json.load(game_file)
    except IOError:
        game_data = {}
    return game_data


def save_state(game_data):
    filepath = get_game_path(game_data['id'])
    try:
        with open(filepath, 'w') as game_file:
            json.dump(game_data, game_file)
    except IOError:
        return False
    return True


def generate_id(length):
    return ''.join(
        random.choice(
            string.ascii_lowercase + string.ascii_uppercase + string.digits
        ) for x in xrange(length)
    )


def serialize_datetime(dt):
    return str(dt)


def deserialize_datetime(serialized_dt):
    return datetime.strptime(serialized_dt, '%Y-%m-%d %H:%M:%S.%f')


def create_card(value, color=None):
    return {'id': generate_id(CARD_ID_LENGTH), 'value': value, 'color': color}


def create_deck():
    cards = []
    for color in CARD_COLORS:
        cards.append(create_card(0, color))
        for i in range(1, 10):
            cards.append(create_card(i, color))
            cards.append(create_card(i, color))
        for special in SPECIAL_COLOR_CARDS:
            cards.append(create_card(special, color))
            cards.append(create_card(special, color))
    for special in SPECIAL_CARDS:
        for i in range(0, 4):
            cards.append(create_card(special))
    random.shuffle(cards)
    return cards


def add_player_to_game(game_data, player_name, admin=False):
    player_id = generate_id(PLAYER_ID_LENGTH)
    player = {
        'id': player_id,
        'name': player_name,
        'admin': admin,
        'active': False,
        'hand': []
    }
    game_data['players'].append(player)
    return player


def create_new_game(game_name, player_name):
    game_id = generate_id(GAME_ID_LENGTH)
    game_data = {
        'id': game_id,
        'name': game_name,
        'deck': create_deck(),
        'stack': [],
        'created_at': serialize_datetime(datetime.utcnow()),
        'started_at': None,
        'active': False,
        'reverse': False,
        'players': []
    }
    add_player_to_game(game_data, player_name, True)
    return game_data


def deal_cards(game_data):
    for player in game_data['players']:
        for i in range(0, 7):
            draw = game_data['deck'].pop()
            player['hand'].append(draw)
    draw = game_data['deck'].pop()
    game_data['stack'].append(draw)


def start_game(game_data):
    deal_cards(game_data)
    admin_player = [p for p in game_data['players'] if p['admin']][0]
    admin_player['active'] = True
    game_data['active'] = True
    game_data['started_at'] = serialize_datetime(datetime.utcnow())


def get_state(game_id, player_id):
    game_data = load_state(game_id)
    players = game_data.get('players', None)
    if not players or player_id not in [p['id'] for p in players]:
        return {}
    for p in players:
        if p['id'] != player_id:
            p['id'] = None
            for card in p['hand']:
                card['color'] = None
                card['id'] = None
                card['value'] = None
    return game_data


def can_play_card(game_data, card):
    if card['value'] in SPECIAL_CARDS:
        return True
    card_to_match = game_data['stack'][-1]
    if card['color'] == card_to_match['color']:
        return True
    if card['value'] == card_to_match['value']:
        return True
    return False


def get_active_player(game_data):
    """ Returns the currently active player """
    return [p for p in game_data['players'] if p['active']][0]


def activate_next_player(game_data):
    active_player = get_active_player(game_data)
    active_index = game_data['players'].index(active_player)
    player_dq = deque(game_data['players'])
    player_dq.rotate(-active_index)
    if game_data['reverse']:
        player_iter = cycle(reversed(player_dq))
    else:
        player_iter = cycle(player_dq)
        print(player_iter.next())
    num_players = len(game_data['players'])
    last_card = game_data['stack'][-1]
    if num_players == 2 and last_card['value'] == 'REVERSE':
        player_iter.next()
    if last_card['value'] == 'SKIP':
        player_iter.next()
    next_player = player_iter.next()
    active_player['active'] = False
    next_player['active'] = True
    # if top of stack is draw_four or draw_two, activate next player and do it


def play_card(game_id, player_id, card_id, selected_color=None):
    """ Attempts to play card, returns game_data dictionary if succeeds """
    game_data = load_state(game_id)
    players = game_data.get('players', None)
    if not players or player_id not in [p['id'] for p in players]:
        return None
    player = [p for p in players if p['id'] == player_id][0]
    if not player['active']:
        return None
    if card_id not in [c['id'] for c in player['hand']]:
        return None
    card = [c for c in player['hand'] if c['id'] == card_id][0]
    if not can_play_card(game_data, card):
        return None
    if card['value'] in SPECIAL_CARDS:
        if selected_color not in CARD_COLORS:
            return None
        card['color'] = selected_color
    player['hand'].remove(card)
    game_data['stack'].append(card)
    if card['value'] == 'REVERSE':
        game_data['reverse'] = not game_data['reverse']
    activate_next_player(game_data)
    return game_data


@app.route('/getstate')
def get_state_route():
    game_id = request.args.get('game_id')
    player_id = request.args.get('player_id')
    game_data = get_state(game_id, player_id)
    return jsonify(**game_data)


@app.route('/playcard')
def play_card_route():
    game_id = request.args.get('game_id')
    player_id = request.args.get('player_id')
    card_id = request.args.get('card_id')
    selected_color = request.args.get('selected_color')
    game_data = play_card(game_id, player_id, card_id, selected_color)
    result = game_data is not None
    if result:
        save_state(game_data)
    return jsonify(result=result)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
