function handle_keypress(element, keycode, myEvent){
    var input_number = keycode - 48;
    var element = "#label_select_" + input_number;
    var state = $(element).prop("checked");
    $(element).prop("checked", !state).change();
}

$(document).ready(function(){
    $("html").keypress(function(event) {
        var keycode = (event.keyCode ? event.keyCode : event.which);
        if ((keycode >= 48) & (keycode <= 57)) {
            handle_keypress(this, keycode, "click");
        }
        event.stopPropagation();
    });

    $("html").keydown(function(event) {
        var button_field = document.querySelector("button[value=submit]");
        if ((event.keyCode === 13)  && (!button_field.disabled)){
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

