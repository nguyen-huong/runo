from flask import abort, Flask, jsonify, redirect, render_template, request, \
    url_for
from runo import admin_start_game, create_new_game, get_state, get_open_games, \
    join_game, leave_game, load_state, play_card, player_draw_card


MAX_GAME_NAME_LENGTH = 20
MAX_PLAYER_NAME_LENGTH = 16

app = Flask(__name__)


@app.route('/')
def index():
    open_games = get_open_games()
    return render_template('index.html', open_games=open_games,
        max_game_name_length=MAX_GAME_NAME_LENGTH,
        max_player_name_length=MAX_PLAYER_NAME_LENGTH)


@app.route('/play/<game_id>/<player_id>')
def play(game_id, player_id):
    game_data = load_state(game_id)
    if not game_data:
        abort(404)
    if player_id not in [p['id'] for p in game_data['players']]:
        abort(404)
    return render_template('play.html', game_id=game_id, player_id=player_id)


@app.route('/newgame')
def newgame():
    game_name = request.args.get('game_name', '')[:MAX_GAME_NAME_LENGTH]
    player_name = request.args.get('player_name', '')[:MAX_PLAYER_NAME_LENGTH]
    game_data = create_new_game(game_name, player_name)
    if game_data:
        game_id = game_data['id']
        player_id = game_data['players'][0]['id']
        return redirect(url_for('play', game_id=game_id, player_id=player_id))
    return 'Unable to create a new game at this time. Please try again later.'


@app.route('/join')
def join():
    game_id = request.args.get('game_id')
    name = request.args.get('name', '')[:MAX_PLAYER_NAME_LENGTH]
    player = join_game(game_id, name)
    if player:
        player_id = player['id']
        return redirect(url_for('play', game_id=game_id, player_id=player_id))
    return 'This game is no longer accepting new players.'


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


@app.route('/quit/<game_id>/<player_id>')
def quit(game_id, player_id):
    result = leave_game(game_id, player_id)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
