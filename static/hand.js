var Hand = function() {
    // Create the hand element
    this.element = $('<div id="hand" class=""></div>');

    // Create the array to hold PlayerCard objects
    this.cards = [];
    this.active = false;
};

Hand.prototype.indexOf = function(cardId) {
    for (var i = 0; i < this.cards.length; i++) {
        if (uxId == this.cards[i].id) {
            return i;
        }
    }
    return -1;
};

Hand.prototype.removeCard = function(card) {
    var index = this.indexOf(card.id);
    if (index !== -1) {
        card.element.remove();
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
            newCard = new PlayerCard(handJSON[i], function() {
                console.log('PlayerCard success!');
            }, function() {
                console.log('PlayerCard failure!');
            });
            this.cards.push(newCard);
            this.element.append(newCard.element);
        }
    }
};

Hand.prototype.activate = function() {
    for (var i = 0; i < this.cards.length; i++) {
        this.cards[i].activate();
    }
    this.active = true;
};

Hand.prototype.deactivate = function() {
    for (var i = 0; i < this.cards.length; i++) {
        this.cards[i].deactivate();
    }
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

// Hand.prototype.update = function(game_data) {
//     var active = false;
//     var cards = [];
//     var value;
//     var color;
//     var id;
//     var card;

//     for (var i = 0; i < handJSON.length; i++) {
//         value = handJSON[i].value;
//         color = handJSON[i].color;
//         id = handJSON[i].id;
//         card = new PlayerCard(value, color, id, function() {
//             console.log('PlayerCard success!');
//         }, function() {
//             console.log('PlayerCard failure!');
//         });
//         cards.push(card);
//         this.element.append(card.element)
//     }

//     this.isActive = function() {
//         return active;
//     };

//     this.activate = function() {
//         for (var i = 0; i < cards.length; i++) {
//             cards[i].activate();
//         }
//         active = true;
//     };

//     this.deactivate = function() {
//         for (var i = 0; i < cards.length; i++) {
//             cards[i].deactivate();
//         }
//         active = false;
//     };

//     if (playerIsActive) {
//         this.activate();
//     }
// };
