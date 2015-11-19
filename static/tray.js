var Tray = function(lastDiscardJSON, playerIsActive) {
    var drawCard = new DrawCard(function() {
        console.log('DrawCard success!');
    }, function() {
        console.log('DrawCard failure!');
    });
    var lastDiscard = null;

    this.element = $('<div id="tray" class=""></div>');

    if (lastDiscardJSON) {
        lastDiscard = new Card(lastDiscardJSON.value, lastDiscardJSON.color);
        this.element.append(lastDiscard.element)
    }

    if (playerIsActive) {
        drawCard.activate();
    }

    this.element.append(drawCard.element);
};

Tray.prototype.update = function(lastDiscardJSON, playerIsActive) {

};
