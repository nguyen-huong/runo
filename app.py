from flask import abort, Flask, jsonify, redirect, render_template, request, \
    url_for
from runo import admin_start_game, create_new_game, get_state, get_open_games, \
    join_game, leave_game, play_card, player_draw_card

app = Flask(__name__)


@app.route('/')
def index():
    open_games = get_open_games()
    return render_template('index.html', open_games=open_games)


@app.route('/play/<game_id>/<player_id>')
def play(game_id, player_id):
    game_data = get_state(game_id, player_id)
    if not game_data:
        abort(404);
    return render_template('play.html', game_id=game_id, player_id=player_id)


@app.route('/newgame')
def newgame():
    game_name = request.args.get('game_name')
    player_name = request.args.get('player_name')
    game_data = create_new_game(game_name, player_name)
    game_id = game_data['id']
    player_id = game_data['players'][0]['id']
    return redirect(url_for('play', game_id=game_id, player_id=player_id))


@app.route('/join')
def join():
    game_id = request.args.get('game_id')
    name = request.args.get('name')
    player = join_game(game_id, name)
    if player:
        player_id = player['id']
        return redirect(url_for('play', game_id=game_id, player_id=player_id))
    return 'We apologize, but this game is no longer available.'


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
