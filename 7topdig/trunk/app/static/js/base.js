function sleep(milliseconds) {
  var start = new Date().getTime();
  for (var i = 0; i < 1e7; i++) {
    if ((new Date().getTime() - start) > milliseconds){
      break;
    }
  }
}

function ajax_post(url, params, on_success) {
	var _callback = function(response) {
		if (response.success) {
			if (response.redirect_url) {
				window.location.href = response.redirect_url;
            }
			if (response.reload) {
				window.location.reload();
            }
			if (on_success) {
				return on_success(response);
			}
		} else {
			notification(response.error, "error");
			sleep(240);
			if (response.redirect_url) {
				window.location.href = response.redirect_url;
			}
		}
	}
	$.post(url, params, _callback, "json");
}

function notification(message, category) {
	data = '<div class="' + category + '">' + message + '</div>';
	if ($.trim(data)) {
		$('#notification').sticky(data);
	}
}

function delete_post(url) {
	apprise('确定删除？', {'confirm':true}, function(r) {
		if(r) { 
			ajax_post(url, null);		
		} else { 
			/* do nothing here */
		}
	});
}

function delete_message(url) {
	apprise('确定删除？', {'confirm':true}, function(r) {
		if(r) { 
			ajax_post(url, null);		
		} else { 
			/* do nothing here */
		}
	});	
}


function delete_comment(url) {
	apprise('确定删除？', {'confirm':true}, function(r) {
		if(r) { 
			var callback = function(response) {
				notification("评论 "+response.comment_id+"成功删除", "successfully");
				$('#comment-' + response.comment_id).fadeOut('slow');
			}
			ajax_post(url, null, callback);		
		} else { 
			/* do nothing here */
		}
	});
}

function vote_post(url) {
	var callback = function(response) {
		$('#score-' + response.post_id).text(response.score);
	}

	ajax_post(url, null, callback);
}

function vote_comment(url) {
	var callback = function(response) {
		$('#vote-comment-' + response.comment_id).hide();
		$('#score-comment-' + response.comment_id).text(response.score);
	}

	ajax_post(url, null, callback);
}

function load_data() {
	var link = $('#link_submit').val();
	$.ajax({
		url : $SCRIPT_ROOT + "/load_data",
		data : {link : link},
		dataType : "json"
	}).done(function(data) {
		if ($.trim(data)) {
			$('#post_title').val(data.title);
			$('#post_link').val(data.link);
			$('#post_description').val(data.summary);
			$('#post_tags').val(data.tags.name);
		}
	});
	return false;
}


$(function() {
	if ( $('#notification').children().length > 0 ) {
		$('#notification').sticky();
	}
	
	$('#upload_submit').click(function(){
    	$('#loading_gif').show();
    });
    
    $('.post-summary').bind("mouseover", function(){
        var color  = $(this).css("background-color");
        $(this).css("background", "#FAFAFA");

        $(this).bind("mouseout", function(){
            $(this).css("background", color);
        }); 
    });
    var odd = {"background-color": "#D7E6F0", "border-top": "1px solid #AAAAAA"};
    var even = {"background-color": "#F6FAFC", "border-top":  "1px solid #AAAAAA"};
    
    /* header color */
	$("h3:odd").css(odd);
	$("h3:even").css(even);
});

