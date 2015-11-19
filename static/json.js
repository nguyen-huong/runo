var json = (function() {
    var obj = {}

    obj.start = function(callback) {
        $.getJSON($SCRIPT_ROOT + '/start', {
            game_id: GAME_ID,
            player_id: PLAYER_ID
        }, callback);
    };

    obj.getState = function(callback) {
        $.getJSON($SCRIPT_ROOT + '/getstate', {
            game_id: GAME_ID,
            player_id: PLAYER_ID
        }, callback);
    };

    obj.playCard = function(callback) {
        $.getJSON($SCRIPT_ROOT + '/playcard', {
            game_id: GAME_ID,
            player_id: PLAYER_ID,
            card_id: CARD_ID,
            selected_color: SELECTED_COLOR
        }, callback);
    };

    obj.draw = function(callback) {
        $.getJSON($SCRIPT_ROOT + '/draw', {
            game_id: GAME_ID,
            player_id: PLAYER_ID
        }, callback);
    };

    return obj;
})();
