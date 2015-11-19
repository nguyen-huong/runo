var Hand = function(handJSON, playerIsActive) {
    var active = false;
    var cards = [];

    this.element = $('<div id="hand" class=""></div>');

    var value;
    var color;
    var id;
    var card;
    for (var i = 0; i < handJSON.length; i++) {
        value = handJSON[i].value;
        color = handJSON[i].color;
        id = handJSON[i].id;
        card = new PlayerCard(value, color, id, function() {
            console.log('PlayerCard success!');
        }, function() {
            console.log('PlayerCard failure!');
        });
        cards.push(card);
        this.element.append(card.element)
    }

    this.isActive = function() {
        return active;
    };

    this.activate = function() {
        for (var i = 0; i < cards.length; i++) {
            cards[i].activate();
        }
        active = true;
    };

    this.deactivate = function() {
        for (var i = 0; i < cards.length; i++) {
            cards[i].deactivate();
        }
        active = false;
    };

    if (playerIsActive) {
        this.activate();
    }
};

Hand.prototype.update = function(handJSON, playerIsActive) {

};
