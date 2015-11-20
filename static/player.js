var Player = function(playerJSON) {
    // Initialize player data
    this.id = playerJSON.id;
    this.uxId = playerJSON.ux_id;
    this.name = playerJSON.name;
    this.points = playerJSON.points;
    this.roundsWon = playerJSON.rounds_won;
    this.numCards = playerJSON.hand_size;
    this.isActive = playerJSON.active;
    this.isAdmin = playerJSON.admin;
    this.isGameWinner = playerJSON.game_winner;
    this.isDrawRequired = playerJSON.draw_required;

    // Create the player element
    this.element = $('<tr class="player"></tr>');
    this.element.append('<td>' + this.name + '</td>');
    this.element.append('<td>' + this.points + '</td>');
    this.element.append('<td>' + this.roundsWon + '</td>');
    this.element.append('<td>' + this.numCards + '</td>');

    // Highlight the active player
    if (this.isActive) {
        this.activate();
    }
};

Player.prototype.activate = function() {
    this.element.addClass('player-active');
};

Player.prototype.deactivate = function() {
    this.element.removeClass('player-active');
};

Player.prototype.update = function(playerJSON, game_data) {
    this.points = playerJSON.points;
    this.roundsWon = playerJSON.rounds_won;
    this.numCards = playerJSON.hand_size;
    this.isGameWinner = playerJSON.game_winner;
    this.isDrawRequired = playerJSON.draw_required;

    if (playerJSON.active && !this.isActive) {
        this.activate();
    } else if (!playerJSON.active && this.isActive) {
        this.deactivate();
    }
    this.isActive = playerJSON.active;

    // Perform actions specific to the current player
    if (this.id) {
        if (!this.isAdmin && playerJSON.admin && !game_data.started_at) {
            // TODO: Add a flash message here
            alert('The admin left... You are now the game admin!');
        }
    }
    this.isAdmin = playerJSON.admin;
};
