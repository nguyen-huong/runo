var DrawCard = function(onSuccess, onFailure) {
    InteractiveCard.call(this, 'DUMMY', null, function() {
        // Make JSON call to draw a card
        console.log(this);
        // Return result
        return true;
    }, onSuccess, onFailure);
};
DrawCard.prototype = Object.create(InteractiveCard.prototype);
DrawCard.prototype.constructor = DrawCard;
