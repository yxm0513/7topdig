$(function() {
    var socket = io.connect('http://10.109.17.204:8090');
    //$('input[type=text]').focus(function() {
    //  $(this).val('');
    //});
    $('.input').keypress(function (e) {
        if (e.which == 13) {
        $('#submit').focus().click();
        return false;
        }
    });
    var $output = $('#data');

    var $status = $('#status');
    socket.on('connect', function(){
        $status.removeClass('red');
        $status.text('Connected');
        $status.addClass('green');
    });
    socket.on('output', function(data){
        $output.append($('<p/>').text(data));
        $output.scrollTop($output[0].scrollHeight);
    });
    $output.scrollTop($output[0].scrollHeight);
    socket.on('end', function(data){
        if( data != 0){
            if( data == 2) {
               $('#actionstatus').html("Error: incomplete collection").addClass('orange');
            }else if( data == 3){
               $('#actionstatus').html("Error: system in Rescue Mode").addClass('orange');
            }else{
               $('#actionstatus').html("FAIL").addClass('red');
            }
        }else{
         $('#actionstatus').html("OK").addClass('green');
        }
    });
    $('#submit').click(function(){
        if(socket){
            var hostname = $('#hostname').val();
            var ar = $('#ar').val();
            if(hostname){
                $('#actionstatus').html('in pogress').removeClass('red').removeClass('green').removeClass('orange');
                socket.emit('post', {'hostname': hostname, 'ar': ar});  
            }
        }else{
            $status.removeClass('red');
            $status.text('Socket hasn\'t been connected');
        }
    });
});
