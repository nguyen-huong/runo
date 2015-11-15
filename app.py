from flask import Flask, jsonify, request
from uno import get_state, play_card, save_state

app = Flask(__name__)


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
