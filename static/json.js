var start = function(e) {
    $.getJSON($SCRIPT_ROOT + '/start', {
        game_id: GAME_ID,
        player_id: PLAYER_ID
    }, function(data) {
        getstateJSON();
    });
    return false;
};

var getStateJSON = function(callback) {
    $.getJSON($SCRIPT_ROOT + '/getstate', {
        game_id: GAME_ID,
        player_id: PLAYER_ID
    }, callback);
};

var playcardJSON = function() {
    $.getJSON($SCRIPT_ROOT + '/playcard', {
        game_id: GAME_ID,
        player_id: PLAYER_ID,
        card_id: CARD_ID,
        selected_color: SELECTED_COLOR
    }, function(data) {
        if (!data.result) {
            alert('Failed to play that card.');
        }
        getstateJSON();
    });
};

var playcard = function(e) {
    playcardJSON();
    return false;
};

var draw = function(e) {
    $.getJSON($SCRIPT_ROOT + '/draw', {
        game_id: GAME_ID,
        player_id: PLAYER_ID
    }, function(data) {
        if (!data.result) {
            alert('Failed to draw a card.');
        }
        getstateJSON();
    });
    return false;
};

var quit = function(e) {
    $.getJSON($SCRIPT_ROOT + '/quit', {
        game_id: GAME_ID,
        player_id: PLAYER_ID
    }, function(data) {
        getstateJSON();
    });
    return false;
};
