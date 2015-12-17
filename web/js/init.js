$(function(){

    var template_nodeList = Handlebars.compile($("#nodeList").html());
    Handlebars.registerPartial('nodeRow', $("#nodeRow").html());

    $.getJSON( "http://localhost:5000/api/v1/nodes", function( json ) {
        console.log(json);
        $.each(json.data.nodes, function( index, value ) {
            // Check if node is connected
            value.status = 0;  // Default value
            if(value.lastSeen === json.data.global_last_seen){
                value.status = 1;
            }
        });
        $('#list').html(template_nodeList(json.data))
    });


});
