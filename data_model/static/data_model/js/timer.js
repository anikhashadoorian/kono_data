function onSubmitProcessing() {
    const performanceNavigation = performance.getEntriesByType("navigation")[0];
    const loadRequestStartTime = performanceNavigation.requestStart;
    const loadEventEndTime = performanceNavigation.loadEventEnd;

    const formLoadingTime =  loadEventEndTime - loadRequestStartTime;
    const formProcessingTime = performance.now() - formLoadingTime;
    var formLoadingTimeElement = document.getElementById("form-loading-time");
    if (formLoadingTimeElement){
        formLoadingTimeElement.value = formLoadingTime;
    }

    var formProcessingTimeElement = document.getElementById("form-processing-time");
    if (formProcessingTimeElement){
        formProcessingTimeElement.value = formProcessingTime;
    }
}
