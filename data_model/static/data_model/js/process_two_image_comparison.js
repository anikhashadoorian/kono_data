function handleKeypress(element, keycode, myEvent){
    var inputNumber = keycode - 48;
    var element = "#label_select_" + inputNumber;
    var state = $(element).prop("checked");
    $(element).prop("checked", !state).change();
}

$(document).ready(function(){
    $("html").keypress(function(event) {
        var keycode = (event.keyCode ? event.keyCode : event.which);
        if ((keycode >= 48) & (keycode <= 57)) {
            handleKeypress(this, keycode, "click");
        }
        event.stopPropagation();
    });

    $("html").keydown(function(event) {
        var button = document.querySelector("button[value=submit]");
        if ((event.keyCode === 13)  && (!button.disabled)){
            this.querySelector(".form").submit();
            return false;
         }
    });
});

$(document).ready(function() {
    var button_field = document.querySelector("button[value=submit]");
    button_field.disabled = true;
});



$(window).bind("load", function() {
    var button_field = document.querySelector("button[value=submit]");
    button_field.disabled = false;
});

