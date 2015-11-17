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
DEFAULT_GAME_NAME = 'Game'
DEFAULT_PLAYER_NAME = 'Player'


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


def reclaim_stack(game_data, is_deal=False):
    # Take the stack and make it the deck. If this is not happening during
    # a deal, remove the top card and put it back in the empty stack so the
    # game can continue. Otherwise, leave the stack empty. In either case,
    # shuffle the deck.
    game_data['deck'] = game_data['stack']
    if not is_deal:
        game_data['stack'] = [game_data['deck'].pop()]
    else:
        game_data['stack'] = []
    random.shuffle(game_data['deck'])
    # Scrub the color from all WILD and WILD_DRAW_FOUR cards.
    cards = [wc for wc in game_data['deck'] if wc['value'] in SPECIAL_CARDS]
    for card in cards:
        card['color'] = None


def reclaim_player_cards(game_data, player):
    # Collect player's cards and inserts them into the bottom of the stack.
    game_data['stack'] = player['hand'] + game_data['stack']
    player['hand'] = []


def reclaim_cards(game_data):
    # Collects cards from all players.
    for player in game_data['players']:
        reclaim_player_cards(game_data, player)


def draw_card(game_data, player, is_deal=False):
    deck = game_data['deck']
    player['hand'].append(deck.pop())
    if not deck:
        reclaim_stack(game_data, is_deal)


def draw_two(game_data, player):
    for __ in range(2):
        draw_card(game_data, player)


def draw_four(game_data, player):
    for __ in range(4):
        draw_card(game_data, player)


def deal_cards(game_data):
    for player in game_data['players']:
        for __ in range(7):
            draw_card(game_data, player, is_deal=True)
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


def player_has_playable_card(game_data, player):
    for card in player['hand']:
        if can_play_card(game_data, card):
            return True
    return False


def player_has_matching_color_card(game_data, player):
    # Get the color of the previously played card
    color_to_match = game_data['stack'][-1]['color']
    return color_to_match in [c['color'] for c in player['hand']]


def get_active_player(game_data):
    """ Returns the currently active player """
    try:
        return [p for p in game_data['players'] if p['active']][0]
    except IndexError:
        return None


def activate_next_player(game_data, card_drawn=False, player_quit=False):
    active_player = get_active_player(game_data)
    active_player['active'] = False
    active_index = game_data['players'].index(active_player)
    player_dq = deque(game_data['players'])
    player_dq.rotate(-active_index)
    # Initialize the player iterator.
    if game_data['reverse']:
        player_iter = cycle(reversed(player_dq))
    else:
        player_iter = cycle(player_dq)
        player_iter.next()
    # If the last player was able to play a card, execute additional logic
    # to determine any consequences of the card played.
    if not card_drawn or player_quit:
        num_players = len(game_data['players'])
        last_card = game_data['stack'][-1]
        next_player = player_iter.next()
        if num_players == 2 and last_card['value'] == 'REVERSE':
            next_player = player_iter.next()
        elif last_card['value'] == 'SKIP':
            next_player = player_iter.next()
        # If top of stack is draw_four or draw_two, draw cards on behalf
        # of the next player, then activate the player after them.
        elif last_card['value'] == 'DRAW_TWO':
            draw_two(game_data, next_player)
            next_player = player_iter.next()
        elif last_card['value'] == 'WILD_DRAW_FOUR':
            draw_four(game_data, next_player)
            next_player = player_iter.next()
    # If the last play was just drawing a card, the only logic necessary to
    # run here is advancing to the next player.
    else:
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
        reclaim_cards(game_data)
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
    game_name = game_name or DEFAULT_GAME_NAME
    player_name = player_name or DEFAULT_PLAYER_NAME
    points_to_win = points_to_win or POINTS_TO_WIN
    min_players = min_players or MIN_PLAYERS
    max_players = max_players or MAX_PLAYERS
    if min_players < 2:
        min_players = 2
    if max_players > 10:
        max_players = 10
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
        'points_to_win': points_to_win
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
    if card['value'] == 'WILD_DRAW_FOUR':
        if player_has_matching_color_card(game_data, player):
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
    if player_has_playable_card(game_data, player):
        return False
    draw_card(game_data, player)
    if not player_has_playable_card(game_data, player):
        activate_next_player(game_data, card_drawn=True)
    save_state(game_data)
    return True


def join_game(game_id, name):
    """ Attempts to join a new player to the game.
        Returns player if successful, otherwise None.
    """
    name = name or DEFAULT_PLAYER_NAME
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
    if game_data['ended_at']:
        return False
    quitter = [p for p in players if p['id'] == player_id][0]
    if quitter['active']:
        activate_next_player(game_data, player_quit=True)
    game_data['players'].remove(quitter)
    # If the quitter was the admin and there is at least one player
    # remaining, reassign the admin role to the first position.
    if quitter['admin'] and game_data['players']:
        game_data['players'][0]['admin'] = True
    # If one player remaining in an active game, end the game now.
    if game_data['active'] and len(game_data['players']) == 1:
        game_data['active'] = False
        game_data['ended_at'] = serialize_datetime(datetime.utcnow())
    # If no players remaining, end the game now.
    if not game_data['players']:
        game_data['ended_at'] = serialize_datetime(datetime.utcnow())
    # If game is still active at this point, reclaim the quitter's cards.
    if game_data['active']:
        reclaim_player_cards(game_data, quitter)
    save_state(game_data)
    return True


def admin_start_game(game_id, player_id):
    """ Attempts to start the game, as long as the player is admin.
        Returns True if successful.
    """
    game_data = load_state(game_id)
    if not game_data:
        return False
    players = game_data.get('players')
    if player_id not in [p['id'] for p in players]:
        return False
    player = [p for p in players if p['id'] == player_id][0]
    if game_data['active']:
        return False
    if game_data['ended_at']:
        return False
    if len(game_data['players']) < game_data['min_players']:
        return False
    if not player['admin']:
        return False
    start_game(game_data)
    save_state(game_data)
    return True
