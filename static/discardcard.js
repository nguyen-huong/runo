var DiscardCard = function(value, color, id) {
    Card.call(this, value, color);
    this.id = id;
};
DiscardCard.prototype = Object.create(Card.prototype);
DiscardCard.prototype.constructor = DiscardCard;
