var PlayerCard = function(cardJSON, onSuccess, onFailure) {
    var value = cardJSON.value;
    var color = cardJSON.color;

    InteractiveCard.call(this, value, color, function() {
        // Make JSON call to play the card
        var selectedColor = null;
        if (this.value == 'WILD' || this.value == 'WILD_DRAW_FOUR') {
            selectedColor = prompt('Red, blue, green or yellow?').toUpperCase();
        }
        json.playCard(this.id, selectedColor, function(data) {
            if (data.result && onSuccess) {
                onSuccess();
            } else if (!data.result && onFailure) {
                onFailure();
            }
        });
        console.log(this);
    });
    this.id = cardJSON.id;
};
PlayerCard.prototype = Object.create(InteractiveCard.prototype);
PlayerCard.prototype.constructor = PlayerCard;
