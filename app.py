from flask import Flask, jsonify, request
from runo import admin_start_game, create_new_game, get_state, join_game, \
    leave_game, play_card, player_draw_card

app = Flask(__name__)


@app.route('/newgame')
def new_game_route():
    game_name = request.args.get('game_name')
    player_name = request.args.get('player_name')
    # points_to_win = request.args.get('points_to_win')
    # min_players = request.args.get('min_players', 0, int)
    # max_players = request.args.get('max_players', 0, int)
    game_data = create_new_game(game_name, player_name)
    game_id = game_data['id']
    player_id = game_data['players'][0]['id']
    return jsonify(game_id=game_id, player_id=player_id)


@app.route('/join')
def join_route():
    game_id = request.args.get('game_id')
    name = request.args.get('name')
    player = join_game(game_id, name)
    if player:
        return jsonify(player_id=player['id'])
    return jsonify(player_id=None)


@app.route('/start')
def start_route():
    game_id = request.args.get('game_id')
    player_id = request.args.get('player_id')
    result = admin_start_game(game_id, player_id)
    return jsonify(result=result)


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
    result = play_card(game_id, player_id, card_id, selected_color)
    return jsonify(result=result)


@app.route('/draw')
def draw_route():
    game_id = request.args.get('game_id')
    player_id = request.args.get('player_id')
    result = player_draw_card(game_id, player_id)
    return jsonify(result=result)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
