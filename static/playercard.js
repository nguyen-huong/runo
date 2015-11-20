var PlayerCard = function(cardJSON, onSuccess, onFailure) {
    var value = cardJSON.value;
    var color = cardJSON.color;

    InteractiveCard.call(this, value, color, function() {
        // Make JSON call to play the card
        // json.playCard(this.id, null, )
        console.log(this);
        // Return result
        return true;
    }, onSuccess, onFailure);
    this.id = cardJSON.id;
};
PlayerCard.prototype = Object.create(InteractiveCard.prototype);
PlayerCard.prototype.constructor = PlayerCard;
