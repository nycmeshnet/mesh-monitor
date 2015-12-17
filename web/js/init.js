$(function(){

    var template_nodeList = Handlebars.compile($("#nodeList").html());
    var template_nodeHeader = Handlebars.compile($("#nodeHeader").html());
    Handlebars.registerPartial('nodeRow', $("#nodeRow").html());

    $.getJSON( "/api/v1/nodes/count", function( json ) {
        $('#header').html(template_nodeHeader(json.data))
    });

    $.getJSON( "/api/v1/nodes", function( json ) {
        console.log(json);
        
        json.data.globalLastSeenFormatted = formatTime(json.data.globalLastSeen);

        $.each(json.data.nodes, function( index, value ) {
            // Check if node is connected
            value.status = 'error';  // Default value
            value.statusSortValue = 1;  // Default value
            if(value.lastSeen === json.data.globalLastSeen){
                value.status = 'success';
                value.statusSortValue = 0;
            }
            // Format last_seen
            value.lastSeenFormatted = formatTime(value.lastSeen)
        });
        $('#list').html(template_nodeList(json.data))
        $("#nodes-table").tablesorter();
    });

    function formatTime(epoch){
        var formattedTime = moment(epoch, 'X');
        return formattedTime.format('llll');
    }

});
