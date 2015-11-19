var PlayerCard = function(value, color, id, onSuccess, onFailure) {
    InteractiveCard.call(this, value, color, function() {
        // Make JSON call to play the card
        console.log(this);
        // Return result
        return true;
    }, onSuccess, onFailure);
    this.id = id;
};
PlayerCard.prototype = Object.create(InteractiveCard.prototype);
PlayerCard.prototype.constructor = PlayerCard;
