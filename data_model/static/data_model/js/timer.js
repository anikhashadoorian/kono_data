var seconds = 0;

function timerCallback() {
    seconds++;
    var formProcessingTime = document.getElementById("form-processing-time")
    if (formProcessingTime){
        formProcessingTime.value = seconds;
    }
}

var timerId = window.setInterval(
    function() {
        timerCallback();
    }, 10
);