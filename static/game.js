var game = function() {
    var update = function(game_data) {
        var playerIsActive = true;
        var playerIsAdmin = true;
        var gameStarted = false;
        var gameEnded = false;

        // Controls
        var controlsElement = $('#controls');
        var startButtonElement = $('<a class="game-control" href="#">Start</a>');
        startButtonElement.attr('id', 'start-button');
        var quitButtonElement = $('<a class="game-control">Quit</a>');
        quitButtonElement.attr('href', QUIT_URL);
        quitButtonElement.attr('id', 'quit-button');
        if (playerIsAdmin && !gameStarted && !gameEnded) {
            controlsElement.append(startButtonElement);
        }
        controlsElement.append(quitButtonElement);

        // Scoreboard

        // Tray
        var lastDiscardJSON = {value: '8', color: 'BLUE'};
        var tray = new Tray(lastDiscardJSON, playerIsActive);
        $('#game').append(tray.element);

        // Hand
        var handJSON = [
            {value: 'WILD', color: null, id: 'jd6j3w'},
            {value: 'WILD_DRAW_FOUR', color: null, id: 'jd6j3w'},
            {value: 'DRAW_TWO', color: 'RED', id: 'jd6j3w'},
            {value: 'SKIP', color: 'RED', id: 'jd6j3w'},
            {value: 'REVERSE', color: 'RED', id: 'jd6j3w'},
            {value: '0', color: 'RED', id: 'jd6j3w'},
            {value: '1', color: 'RED', id: 'jd6j3w'},
            {value: '2', color: 'RED', id: 'jd6j3w'},
            {value: '3', color: 'RED', id: 'jd6j3w'},
            {value: '4', color: 'RED', id: 'jd6j3w'},
            {value: '5', color: 'RED', id: 'jd6j3w'},
            {value: '6', color: 'RED', id: 'jd6j3w'},
            {value: '7', color: 'RED', id: 'jd6j3w'},
            {value: '8', color: 'RED', id: 'jd6j3w'},
            {value: '9', color: 'RED', id: 'jd6j3w'},
        ];
        var hand = new Hand(handJSON, playerIsActive);
        $('#game').append(hand.element);
    };

    getStateJSON(update);
    // setInterval(function() {
    //     getStateJSON(update);
    // }, 5000);
};
