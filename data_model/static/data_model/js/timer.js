var loadingSeconds = 0;
var processingSeconds = 0;
var timerId = null;
var isLoaded = false;

function timerCallback() {
    if (!isLoaded){
        loadingSeconds++;
        var fromLoadingTime = document.getElementById("form-loading-time");
        if (fromLoadingTime){
            fromLoadingTime.value = loadingSeconds;
        }
    } else {
        processingSeconds++;
        var formProcessingTime = document.getElementById("form-processing-time");
        if (formProcessingTime){
            formProcessingTime.value = processingSeconds;
        }
    }
}

timerId = window.setInterval(function() {
            timerCallback();
        }, 10);

$(window).bind("load", function() {
    isLoaded = true;
});

