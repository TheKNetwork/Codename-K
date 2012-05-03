function sendAjaxDataAndRefresh(jsonData, processorUrl, divToRefresh, divUrlSource) {
    $.ajax({
       type: "POST",
       data: jsonData,
       url: processorUrl,
       complete: function(data){
           $("#"+divToRefresh).load(divUrlSource);
       }
    });
}   