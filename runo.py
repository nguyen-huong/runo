import json
import os
import random
import string
from collections import deque
from datetime import datetime
from itertools import cycle

GAME_ID_LENGTH = 48
PLAYER_ID_LENGTH = 48
PLAYER_UX_ID_LENGTH = 8
CARD_ID_LENGTH = 6
GAME_FILE_PATH = 'games'
SPECIAL_CARDS = ['WILD', 'WILD_DRAW_FOUR']
SPECIAL_COLOR_CARDS = ['DRAW_TWO', 'SKIP', 'REVERSE']
CARD_COLORS = ['RED', 'GREEN', 'YELLOW', 'BLUE']
CARD_VALUES = [str(i) for i in range(0, 10)]
MIN_PLAYERS = 2
MAX_PLAYERS = 8
POINTS_TO_WIN = 250
MAX_GAMES_PER_DAY = 1000
DEFAULT_GAME_NAME = 'Game'
DEFAULT_PLAYER_NAME = 'Player'


def set_GAME_FILE_PATH(path):
    global GAME_FILE_PATH
    GAME_FILE_PATH = path


def set_MAX_GAMES_PER_DAY(num):
    global MAX_GAMES_PER_DAY
    MAX_GAMES_PER_DAY = num


def get_game_path(game_id):
    return '{}/{}'.format(GAME_FILE_PATH, game_id)


def serialize_datetime(dt):
    return str(dt)


def deserialize_datetime(serialized_dt):
    return datetime.strptime(serialized_dt, '%Y-%m-%d %H:%M:%S.%f')


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


def get_open_games():
    games = []
    for game_id in os.listdir(GAME_FILE_PATH):
        game_data = load_state(game_id)
        if not game_data['active'] and not game_data['ended_at']:
            games.append(game_data)
    return games


def get_old_games():
    games = []
    for game_id in os.listdir(GAME_FILE_PATH):
        game_data = load_state(game_id)
        age = datetime.utcnow() - deserialize_datetime(game_data['created_at'])
        # If game is at least a day old, add it to the list.
        if age.days > 0:
            games.append(game_data)
    return games


def do_house_keeping():
    for game in get_old_games():
        os.remove(get_game_path(game['id']))


def get_number_of_games():
    return len(os.listdir(GAME_FILE_PATH))


def can_create_new_game():
    return get_number_of_games() < MAX_GAMES_PER_DAY


def generate_id(length):
    return ''.join(
        random.choice(
            string.ascii_lowercase + string.ascii_uppercase + string.digits
        ) for x in xrange(length)
    )


def generate_digits(length):
    return ''.join(random.choice(string.digits) for x in xrange(length))


def generate_game_name():
    return DEFAULT_GAME_NAME + generate_digits(5)


def generate_player_name():
    return DEFAULT_PLAYER_NAME + generate_digits(5)


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
    player_ux_id = generate_id(PLAYER_UX_ID_LENGTH)
    player = {
        'id': player_id,
        'ux_id': player_ux_id,
        'name': player_name,
        'admin': admin,
        'active': False,
        'hand': [],
        'points': 0,
        'rounds_won': 0,
        'game_winner': False,
        'messages': []
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
            msg_data = '{} just skipped you via REVERSE!'.format(
                    active_player['name'])
            msg = make_warning_message(msg_data)
            flash_player(game_data, next_player, msg)
            next_player = player_iter.next()
        elif last_card['value'] == 'SKIP':
            msg_data = '{} just skipped you!'.format(
                    active_player['name'])
            msg = make_warning_message(msg_data)
            flash_player(game_data, next_player, msg)
            if num_players != 2:
                msg_data = '{} just skipped {}!'.format(
                        active_player['name'], next_player['name'])
                msg = make_info_message(msg_data)
                flash_exclude(game_data, [active_player, next_player], msg)
            next_player = player_iter.next()
        # If top of stack is draw_four or draw_two, draw cards on behalf
        # of the next player, then activate the player after them.
        elif last_card['value'] == 'DRAW_TWO':
            draw_two(game_data, next_player)
            msg_data = '{} made you draw two cards!'.format(
                    active_player['name'])
            msg = make_warning_message(msg_data)
            flash_player(game_data, next_player, msg)
            msg_data = '{} made {} draw two cards!'.format(
                    active_player['name'], next_player['name'])
            msg = make_info_message(msg_data)
            flash_exclude(game_data, [active_player, next_player], msg)
            next_player = player_iter.next()
        elif last_card['value'] == 'WILD_DRAW_FOUR':
            draw_four(game_data, next_player)
            msg_data = '{} made you draw four cards!'.format(
                    active_player['name'])
            msg = make_warning_message(msg_data)
            flash_player(game_data, next_player, msg)
            msg_data = '{} made {} draw four cards!'.format(
                    active_player['name'], next_player['name'])
            msg = make_info_message(msg_data)
            flash_exclude(game_data, [active_player, next_player], msg)
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
        activate_next_player(game_data)
        msg = make_success_message('You won the round!')
        alt_msg = make_info_message('{} won the round!'.format(player['name']))
        flash_player(game_data, player, msg, alt_msg)


def set_game_winner(game_data, player):
    game_data['active'] = False
    player['active'] = False
    game_data['ended_at'] = serialize_datetime(datetime.utcnow())
    player['game_winner'] = True
    msg = make_success_message('You won the game!')
    alt_msg = make_info_message('{} won the game!'.format(player['name']))
    flash_player(game_data, player, msg, alt_msg)


def make_success_message(message):
    return {'data': message, 'type': 'success'}


def make_info_message(message):
    return {'data': message, 'type': 'info'}


def make_warning_message(message):
    return {'data': message, 'type': 'warning'}


def make_danger_message(message):
    return {'data': message, 'type': 'danger'}


def flash_broadcast(game_data, message):
    for player in game_data['players']:
        player['messages'].append(message)
    save_state(game_data)


def flash_player(game_data, player, message=None, alt_message=None):
    if message:
        player['messages'].append(message)
    if alt_message:
        for p in [p for p in game_data['players'] if p != player]:
            p['messages'].append(alt_message)
    save_state(game_data)


def flash_exclude(game_data, players, message):
    for p in [p for p in game_data['players'] if p not in players]:
        p['messages'].append(message)


def create_new_game(game_name, player_name, points_to_win=POINTS_TO_WIN,
                    min_players=MIN_PLAYERS, max_players=MAX_PLAYERS):
    """ Creates a new game.
        Returns the game data dictionary.
    """
    do_house_keeping()
    if not can_create_new_game():
        return {}
    game_name = game_name or generate_game_name()
    player_name = player_name or generate_player_name()
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
    msg = make_info_message(
        'Click "Start" after all player(s) have joined')
    flash_broadcast(game_data, msg)
    result = save_state(game_data)
    if result:
        return game_data
    return {}


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
    if len(player['hand']) == 1:
        msg = make_info_message('Only one card to go!')
        alt_msg = make_warning_message(
            '{} only has one card left!'.format(player['name']))
        flash_player(game_data, player, msg, alt_msg)
    game_data['stack'].append(card)
    if card['value'] == 'REVERSE':
        game_data['reverse'] = not game_data['reverse']
        if len(game_data['players']) != 2:
            if game_data['reverse']:
                msg = make_info_message('Game order has been reversed')
            else:
                msg = make_info_message('Game order is back to normal')
            flash_broadcast(game_data, msg)
    if not player['hand']:
        set_round_winner(game_data, player)
    else:
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
    msg = None
    if not player_has_playable_card(game_data, player):
        activate_next_player(game_data, card_drawn=True)
        msg = make_info_message(
            '{} drew a card but couldn\'t play'.format(player['name']))
    else:
        msg = make_info_message('{} drew a card'.format(player['name']))
    flash_player(game_data, player, alt_message=msg)
    save_state(game_data)
    return True


def join_game(game_id, name):
    """ Attempts to join a new player to the game.
        Returns player if successful, otherwise None.
    """
    name = name or generate_player_name()
    game_data = load_state(game_id)
    if not game_data:
        return None
    if game_data['active']:
        return None
    if game_data['ended_at']:
        return None
    player = add_player_to_game(game_data, name)
    if player:
        msg = make_info_message('You have joined the game')
        alt_msg = make_info_message(
            '{} has joined the game'.format(player['name']))
        flash_player(game_data, player, msg, alt_msg)
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
    msg = make_info_message('You have left the game')
    alt_msg = make_info_message('{} has left the game'.format(quitter['name']))
    flash_player(game_data, quitter, msg, alt_msg)
    if quitter['active']:
        activate_next_player(game_data, player_quit=True)
    game_data['players'].remove(quitter)
    # If the quitter was the admin and there is at least one player
    # remaining, reassign the admin role to the first position.
    new_admin = None
    if quitter['admin'] and game_data['players']:
        new_admin = game_data['players'][0]
        new_admin['admin'] = True
    # If one player remaining in an active game, end the game now.
    if game_data['active'] and len(game_data['players']) == 1:
        game_data['active'] = False
        game_data['players'][0]['active'] = False
        game_data['ended_at'] = serialize_datetime(datetime.utcnow())
        msg = make_info_message('The game has ended')
        flash_broadcast(game_data, msg)
    if new_admin and not (game_data['started_at'] or game_data['ended_at']):
            msg = make_info_message('You are now the game administrator')
            flash_player(game_data, new_admin, msg)
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
    msg = make_info_message('The game has started')
    alt_msg = make_info_message('{} started the game'.format(player['name']))
    flash_player(game_data, player, msg, alt_msg)
    msg = make_info_message(
        'The first player to reach {} points wins!'.format(POINTS_TO_WIN))
    flash_broadcast(game_data, msg)
    save_state(game_data)
    return True


def get_state(game_id, player_id):
    game_data = load_state(game_id)
    players = game_data.get('players')
    if not players or player_id not in [p['id'] for p in players]:
        return {}
    for p in players:
        if p['id'] == player_id:
            messages = p['messages']
            p['messages'] = []
            save_state(game_data)
            game_data['messages'] = messages
            break;
    game_data['draw_pile_size'] = len(game_data['deck'])
    game_data.pop('deck')
    last_discard = game_data['stack'][-1] if game_data['stack'] else None
    game_data['last_discard'] = last_discard
    game_data['discard_pile_size'] = len(game_data['stack'])
    for p in players:
        del p['messages']
        p['hand_size'] = len(p['hand'])
        if p['id'] == player_id and p['active']:
            p['draw_required'] = True
            for card in p['hand']:
                if can_play_card(game_data, card):
                    p['draw_required'] = False
                    break
        elif p['id'] != player_id:
            p['id'] = None
            p.pop('hand')
    game_data.pop('stack')
    return game_data
