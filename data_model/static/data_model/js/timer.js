var seconds = 0;
var timerId = null;

function timerCallback() {
    seconds++;
    var formProcessingTime = document.getElementById("form-processing-time");
    if (formProcessingTime){
        formProcessingTime.value = seconds;
    }
}

$(window).bind("load", function() {
    timerId = window.setInterval(function() {
        timerCallback();
    }, 10);
});

