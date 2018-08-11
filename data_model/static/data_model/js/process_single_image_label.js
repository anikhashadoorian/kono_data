function handleKeypress(element, keycode, myEvent){
    var inputNumber = keycode - 48;
    var labelSelect = $(element.querySelector("#label_select_" + inputNumber))[0];
    if(labelSelect.checked){
        labelSelect.checked = false;
    } else {
        labelSelect.checked = true;
    }
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
        if (event.keyCode === 13) {
            this.querySelector(".form").submit();
            return false;
         }
    });
});

