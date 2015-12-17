$(function(){

    var template_nodeList = Handlebars.compile($("#nodeList").html());
    Handlebars.registerPartial('nodeRow', $("#nodeRow").html());

    $.getJSON( "/api/v1/nodes", function( json ) {
        console.log(json);
        
        json.data.global_last_seen_formatted = formatTime(json.data.global_last_seen);

        $.each(json.data.nodes, function( index, value ) {
            // Check if node is connected
            value.status = 'error';  // Default value
            if(value.lastSeen === json.data.global_last_seen){
                value.status = 'success';
            }
            // Format last_seen
            value.last_seen_formatted = formatTime(value.lastSeen)
        });
        $('#list').html(template_nodeList(json.data))
    });

    function formatTime(epoch){
        var formattedTime = moment(epoch, 'X');
        return formattedTime.format('llll');
    }

});
