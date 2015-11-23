var Hand = function(onPlaySuccess, onPlayFailure) {
    // Create the hand element
    this.element = $('<div id="hand" class=""></div>');

    // Store the handlers for the PlayerCard objects
    this.onPlaySuccess = onPlaySuccess;
    this.onPlayFailure = onPlayFailure;

    // Create the array to hold PlayerCard objects
    this.cards = [];
    this.active = false;
};

Hand.prototype.indexOf = function(cardId) {
    for (var i = 0; i < this.cards.length; i++) {
        if (cardId == this.cards[i].id) {
            return i;
        }
    }
    return -1;
};

Hand.prototype.removeCard = function(card) {
    var index = this.indexOf(card.id);
    if (index !== -1) {
        card.remove();
        this.cards.splice(index, 1);
    }
};

Hand.prototype.removeCards = function(handJSON) {
    var remove = [];
    var cardExists;
    for (var i = 0; i < this.cards.length; i++) {
        cardExists = false;
        for (var j = 0; j < handJSON.length; j++) {
            if (this.cards[i].id == handJSON[j].id) {
                cardExists = true;
                break;
            }
        }
        if (!cardExists) {
            remove.push(this.cards[i]);
        }
    }
    for (var i = 0; i < remove.length; i++) {
        this.removeCard(remove[i]);
    }
};

Hand.prototype.addCards = function(handJSON) {
    var newCard;
    var cardExists;
    for (var i = 0; i < handJSON.length; i++) {
        cardExists = false;
        for (var j = 0; j < this.cards.length; j++) {
            if (handJSON[i].id == this.cards[j].id) {
                cardExists = true;
                break;
            }
        }
        if (!cardExists) {
            if (handJSON[i].value === 'WILD' || handJSON[i].value === 'WILD_DRAW_FOUR') {
                newCard = new WildCard(this.element, handJSON[i], this.onPlaySuccess, this.onPlayFailure);
            } else {
                newCard = new PlayerCard(handJSON[i], this.onPlaySuccess, this.onPlayFailure);
            }
            this.cards.push(newCard);
            if (this.active) {
                setTimeout(function() {
                    newCard.activate();
                }, 25);
            }
            this.element.append(newCard.element);
        }
    }
};

Hand.prototype.activate = function() {
    var cards = this.cards;
    setTimeout(function() {
        for (var i = 0; i < cards.length; i++) {
            cards[i].activate();
        }
    }, 750);
    this.active = true;
};

Hand.prototype.deactivate = function() {
    var cards = this.cards;
    setTimeout(function() {
        for (var i = 0; i < cards.length; i++) {
            cards[i].deactivate();
        }
    }, 500);
    this.active = false;
};

Hand.prototype.update = function(game_data) {
    // Get handJSON object for the current player
    var currentPlayer;
    for (var i = 0; i < game_data.players.length; i++) {
        if (game_data.players[i].id) {
            currentPlayer = game_data.players[i];
            break;
        }
    }
    this.removeCards(currentPlayer.hand);
    this.addCards(currentPlayer.hand);

    if (currentPlayer.active && !this.active) {
        this.activate();
    } else if (!currentPlayer.active && this.active) {
        this.deactivate();
    }
};
