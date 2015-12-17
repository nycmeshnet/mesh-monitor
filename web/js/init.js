$(function(){

    var template_nodeList = Handlebars.compile($("#nodeList").html());
    Handlebars.registerPartial('nodeRow', $("#nodeRow").html());


    $.getJSON( "http://localhost:5000/api/v1/nodes", function( data ) {
        console.log(data);
        var html = template_nodeList(data);
        $('#list').html(html)
    });


});
