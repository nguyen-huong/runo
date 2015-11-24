var FlashMessage = function(message) {
    this.element = $('<div id="flash-message">' + message + '</div>');
    var element = this.element;
    setTimeout(function() {
        element.remove();
    }, 5000);
};
