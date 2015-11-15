import json
import random
import string
from collections import deque
from datetime import datetime
from itertools import cycle


GAME_ID_LENGTH = 48
PLAYER_ID_LENGTH = 48
CARD_ID_LENGTH = 6
GAME_FILE_PATH = 'games'
SPECIAL_CARDS = ['WILD', 'WILD_DRAW_FOUR']
SPECIAL_COLOR_CARDS = ['DRAW_TWO', 'SKIP', 'REVERSE']
CARD_COLORS = ['RED', 'GREEN', 'YELLOW', 'BLUE']
CARD_VALUES = [str(i) for i in range(0, 10)]
MIN_PLAYERS = 2
MAX_PLAYERS = 10
POINTS_TO_WIN = 250


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
        cards.append(create_card(CARD_VALUES[0], color))
        for value in CARD_VALUES[1:]:
            for __ in range(2):
                cards.append(create_card(value, color))
        for special in SPECIAL_COLOR_CARDS:
            for __ in range(2):
                cards.append(create_card(special, color))
    for special in SPECIAL_CARDS:
        for i in range(0, 4):
            cards.append(create_card(special))
    random.shuffle(cards)
    return cards


def add_player_to_game(game_data, player_name, admin=False):
    if game_data['max_players'] == len(game_data['players']):
        return None
    player_id = generate_id(PLAYER_ID_LENGTH)
    player = {
        'id': player_id,
        'name': player_name,
        'admin': admin,
        'active': False,
        'hand': [],
        'points': 0,
        'rounds_won': 0,
        'game_winner': False
    }
    game_data['players'].append(player)
    return player


def reclaim_stack(game_data):
    # Take the stack and make it the deck, remove the top card and put
    # it back in the empty stack, then shuffle the deck.
    game_data['deck'] = game_data['stack']
    game_data['stack'] = [game_data['deck'].pop()]
    random.shuffle(game_data['deck'])


def reclaim_player_cards(game_data):
    # Collect cards from all players and insert them into the bottom
    # of the stack.
    player_cards = []
    for player in game_data['players']:
        player_cards += player['hand']
        player['hand'] = []
    game_data['stack'] = player_cards + game_data['stack']


def draw_card(game_data, player):
    deck = game_data['deck']
    player['hand'].append(deck.pop())
    if not deck:
        reclaim_stack(game_data)


def draw_two(game_data, player):
    for __ in range(2):
        draw_card(game_data, player)


def draw_four(game_data, player):
    for __ in range(4):
        draw_card(game_data, player)


def deal_cards(game_data):
    for player in game_data['players']:
        for __ in range(7):
            draw_card(game_data, player)
    # Look for a non-special card in the deck. Once found, move it
    # from the deck to the discard pile (stack).
    for card in reversed(game_data['deck']):
        if card['value'] not in SPECIAL_CARDS + SPECIAL_COLOR_CARDS:
            game_data['stack'].append(card)
            break
    game_data['deck'].remove(card)


def start_game(game_data):
    deal_cards(game_data)
    admin_player = [p for p in game_data['players'] if p['admin']][0]
    admin_player['active'] = True
    game_data['active'] = True
    game_data['started_at'] = serialize_datetime(datetime.utcnow())


def get_state(game_id, player_id):
    game_data = load_state(game_id)
    players = game_data.get('players')
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
    try:
        return [p for p in game_data['players'] if p['active']][0]
    except IndexError:
        return None


def activate_next_player(game_data):
    active_player = get_active_player(game_data)
    active_index = game_data['players'].index(active_player)
    player_dq = deque(game_data['players'])
    player_dq.rotate(-active_index)
    if game_data['reverse']:
        player_iter = cycle(reversed(player_dq))
    else:
        player_iter = cycle(player_dq)
        player_iter.next()
    num_players = len(game_data['players'])
    last_card = game_data['stack'][-1]
    if num_players == 2 and last_card['value'] == 'REVERSE':
        player_iter.next()
    if last_card['value'] == 'SKIP':
        player_iter.next()
    next_player = player_iter.next()
    active_player['active'] = False
    next_player['active'] = True
    # If top of stack is draw_four or draw_two, activate next player
    # and make them draw, then activate the player after them.
    if last_card['value'] == 'DRAW_TWO':
        draw_two(game_data, next_player)
        next_player['active'] = False
        next_player = player_iter.next()
        next_player['active'] = True
    if last_card['value'] == 'WILD_DRAW_FOUR':
        draw_four(game_data, next_player)
        next_player['active'] = False
        next_player = player_iter.next()
        next_player['active'] = True


def count_points_for_player(player):
    points = 0
    for card in player['hand']:
        if card['value'] in SPECIAL_CARDS:
            points = points + 50
        elif card['value'] in SPECIAL_COLOR_CARDS:
            points = points + 20
        else:
            points = points + int(card['value'])
    return points


def count_points(game_data, winning_player):
    points = 0
    for player in [p for p in game_data['players'] if p != winning_player]:
        points = points + count_points_for_player(player)
    return points


def set_round_winner(game_data, player):
    player['points'] += count_points(game_data, player)
    player['rounds_won'] += 1
    if player['points'] >= game_data['points_to_win']:
        set_game_winner(game_data, player)
    else:
        reclaim_player_cards(game_data)
        deal_cards(game_data)


def set_game_winner(game_data, player):
    game_data['active'] = False
    game_data['ended_at'] = serialize_datetime(datetime.utcnow())
    player['game_winner'] = True


def create_new_game(game_name, player_name, points_to_win=POINTS_TO_WIN,
                    min_players=MIN_PLAYERS, max_players=MAX_PLAYERS):
    """ Creates a new game.
        Returns the game data dictionary.
    """
    game_id = generate_id(GAME_ID_LENGTH)
    game_data = {
        'id': game_id,
        'name': game_name,
        'deck': create_deck(),
        'stack': [],
        'created_at': serialize_datetime(datetime.utcnow()),
        'started_at': None,
        'ended_at': None,
        'active': False,
        'reverse': False,
        'min_players': min_players,
        'max_players': max_players,
        'players': [],
        'points_to_win': points_to_win,
        'is_winner': False
    }
    add_player_to_game(game_data, player_name, True)
    save_state(game_data)
    return game_data


def play_card(game_id, player_id, card_id, selected_color=None):
    """ Attempts to play a card.
        Returns True if succeeds.
    """
    game_data = load_state(game_id)
    if not game_data:
        return False
    players = game_data.get('players')
    if player_id not in [p['id'] for p in players]:
        return False
    player = [p for p in players if p['id'] == player_id][0]
    if not player['active']:
        return False
    if card_id not in [c['id'] for c in player['hand']]:
        return False
    if not game_data['active']:
        return False
    card = [c for c in player['hand'] if c['id'] == card_id][0]
    if not can_play_card(game_data, card):
        return False
    if card['value'] in SPECIAL_CARDS:
        if selected_color not in CARD_COLORS:
            return False
        card['color'] = selected_color
    player['hand'].remove(card)
    game_data['stack'].append(card)
    if card['value'] == 'REVERSE':
        game_data['reverse'] = not game_data['reverse']
    if not player['hand']:
        set_round_winner(game_data, player)
    activate_next_player(game_data)
    save_state(game_data)
    return True


def player_draw_card(game_id, player_id):
    """ Attempts to draw a card for the player.
        Returns True if successful.
    """
    game_data = load_state(game_id)
    if not game_data:
        return False
    players = game_data.get('players')
    if player_id not in [p['id'] for p in players]:
        return False
    player = [p for p in players if p['id'] == player_id][0]
    if not player['active']:
        return False
    if not game_data['active']:
        return False
    draw_card(game_data, player)
    save_state(game_data)
    return True


def join_game(game_id, name):
    """ Attempts to join a new player to the game.
        Returns player if successful, otherwise None.
    """
    game_data = load_state(game_id)
    if not game_data:
        return None
    if game_data['active']:
        return None
    if game_data['ended_at']:
        return None
    player = add_player_to_game(game_data, name)
    if player:
        save_state(game_data)
    return player


def leave_game(game_id, player_id):
    """ Attempts to remove a player from a game.
        Returns True if successful.
    """
    game_data = load_state(game_id)
    if not game_data:
        return False
    players = game_data.get('players')
    if player_id not in [p['id'] for p in players]:
        return False
    if game_data['active']:
        return False
    if game_data['ended_at']:
        return None
    player = [p for p in players if p['id'] == player_id][0]
    game_data['players'].remove(player)
    if player['admin']:
        game_data['ended_at'] = serialize_datetime(datetime.utcnow())
    save_state(game_data)
    return True
