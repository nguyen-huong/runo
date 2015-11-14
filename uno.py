import json
import random
import string
from datetime import datetime
from flask import Flask, jsonify, request

app = Flask(__name__)

GAME_ID_LENGTH = 48
PLAYER_ID_LENGTH = 48
CARD_ID_LENGTH = 6
GAME_FILE_PATH = 'games'
SPECIAL_CARDS = ['WILD', 'WILD_DRAW_FOUR']
SPECIAL_COLOR_CARDS = ['DRAW_TWO', 'SKIP', 'REVERSE']
CARD_COLORS = ['RED', 'GREEN', 'YELLOW', 'BLUE']


def generate_id(length):
    return ''.join(
        random.choice(
            string.ascii_lowercase + string.ascii_uppercase + string.digits
        ) for x in xrange(length)
    )


def serialize_datetime(dt):
    return str(dt)


def deserialize_date(serialized_dt):
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
    if game_data['players']:
        ordinal = max([p['ordinal'] for p in game_data['players']]) + 1
    else:
        ordinal = 0
    player = {
        'id': player_id,
        'name': player_name,
        'admin': admin,
        'active': False,
        'ordinal': ordinal,
        'hand': []
    }
    game_data['players'].append(player)


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
    with open(filepath, 'w') as game_file:
        json.dump(game_data, game_file)


@app.route('/getstate')
def get_state():
    game_id = request.args.get('game_id')
    player_id = request.args.get('player_id')
    game_data = load_state(game_id)
    players = game_data.get('players', None)
    if not players or player_id not in [p['id'] for p in players]:
        return jsonify({})
    for p in players:
        if p['id'] != player_id:
            p['id'] = None
            for card in p['hand']:
                card['color'] = None
                card['id'] = None
                card['value'] = None
    return jsonify(**game_data)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
