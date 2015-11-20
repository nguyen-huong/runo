var json = (function() {
    var obj = {}

    obj.getState = function(callback) {
        $.getJSON($SCRIPT_ROOT + '/getstate', {
            game_id: GAME_ID,
            player_id: PLAYER_ID
        }, callback);
    };

    obj.start = function(callback) {
        $.getJSON($SCRIPT_ROOT + '/start', {
            game_id: GAME_ID,
            player_id: PLAYER_ID
        }, callback);
    };

    obj.playCard = function(cardId, selectedColor, callback) {
        $.getJSON($SCRIPT_ROOT + '/playcard', {
            game_id: GAME_ID,
            player_id: PLAYER_ID,
            card_id: cardId,
            selected_color: selectedColor
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
