function handle_keypress(element, keycode, myEvent){
    var input_number = keycode - 48;
    var element = $(element.querySelector("#label_select_" + input_number))[0];
    if(element.checked){
        element.checked = false;
    } else {
        element.checked = true;
    }
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
        if (event.keyCode === 13) {
            this.querySelector(".form").submit();
            return false;
         }
    });
});

