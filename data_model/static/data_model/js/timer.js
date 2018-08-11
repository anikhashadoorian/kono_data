var seconds = 0;

function timerCallback() {
    seconds++;
    formProcessingTime = document.getElementById("form-processing-time")
    if (formProcessingTime){
        formProcessingTime.value = seconds;
    }
}

timerId = window.setInterval(
    function() {
        timerCallback();
    }, 10
);