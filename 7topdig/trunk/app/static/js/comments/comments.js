
$(document).ready(function(){


	function isValidEmailAddress(emailAddress) {
 		var pattern = new RegExp(/^(("[\w-\s]+")|([\w-]+(?:\.[\w-]+)*)|("[\w-\s]+")([\w-]+(?:\.[\w-]+)*))(@((?:[\w-]+\.)*\w[\w-]{0,66})\.([a-z]{2,6}(?:\.[a-z]{2})?)$)|(@\[?((25[0-5]\.|2[0-4][0-9]\.|1[0-9]{2}\.|[0-9]{1,2}\.))((25[0-5]|2[0-4][0-9]|1[0-9]{2}|[0-9]{1,2})\.){2}(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[0-9]{1,2})\]?$)/i);
 		return pattern.test(emailAddress);
	}
	
	
	function limitChars(textid, limit, infodiv)
	{
	var text = $('#'+textid).val(); 
	var textlength = text.length;
	if(textlength > limit)
	{
	$('#' + infodiv).html('Number of characters left: 0');
	$('#'+textid).val(text.substr(0,limit));
	return false;
	}
	else
	{
	$('#' + infodiv).html('Number of characters left: '+ (limit - textlength));
	return true;
	}
	}
	
	$(function(){
			   
	$('#comment').keyup(function(){
	limitChars('comment', 500, 'commentMaxChar');
	
	})
	}); 
	 
	 
	$(".commentWrapperSmall").click(function() {
			
		$(this).find(".commentCommentSmall").toggle();
		$(this).find(".commentCommentMore").toggle();
		
	});

    $("#saveComment").click(function(){
      	var name = $("#name").val(); 
		var email = $("#email").val(); 
		var comment = $("#comment").val();
		var sendCopyToEmail = "no"; if ($("#sendCopyToEmail").is(":checked")) { var sendCopyToEmail = "yes";}
		var commentProgress = "";
        name = $.trim(name);
		email = $.trim(email);
		comment = $.trim(comment);
		
		if(name.length < 3){
			var $errorDiv = $('<div/>', {'id': 'errorM'}).html('3 or more characters needed (Name)');
			$('#error').append($errorDiv);
			$errorDiv.fadeTo(4000, 0.00);
			$errorDiv.slideUp(2000, function(){$(this).remove();});
			return;
		}	
		
		if(comment.length < 3){
			var $errorDiv = $('<div/>', {'id': 'errorM'}).html('3 or more characters needed (Comment)');
			$('#error').append($errorDiv);
			$errorDiv.fadeTo(4000, 0.00);
			$errorDiv.slideUp(2000, function(){$(this).remove();});
			return;
		}	
		
        if(!(isValidEmailAddress(email))){
           	$("#saveComment").val("Post");
			$("#working").toggleClass("hide", true);
			$("#email").fadeOut(250);
			$("#email").fadeIn(250);
			var $errorDiv = $('<div/>', {'id': 'errorM'}).html('Please enter a valid email');
			$('#error').append($errorDiv);
			$errorDiv.fadeTo(3500, 0.00);
			$errorDiv.slideUp(2000, function(){$(this).remove();});
		   	return;
		}
		   
				var dataString = 'name=' + name + '&email=' + email + '&comment=' + comment + '&sendCopyToEmail=' + sendCopyToEmail + '&commentProgress=' + commentProgress;
				$("#working").toggleClass("hide", false);
				$("#saveComment").val("Posting..");
				$('#name, #email, #comment, #sendCopyToEmail, #saveComment').attr("disabled", true);
				
				$.ajax({
           		type: "POST",
            	url: "postComment.php",
            	data: dataString,
            	cache: false,
            	success: function(html){
				
				var $displayComment = $('<div/>', {'id': 'commentWrapper'}).html("<div id='commentTime'>Moments ago</div>" + "<div id='commentName'>" + name + "</div>" + "<div id='commentComment'>" + comment + "</div>");
				$('#comments').append($displayComment);
				
				$displayComment.hide();
				$displayComment.slideDown("slow");
                $("#saveComment").val("Post");
				$("#working").toggleClass("hide", true);
				$("#comment").val("");
				$('#name, #email, #comment, #sendCopyToEmail, #saveComment').attr("disabled", false);
            	},
				
            	error: function(result) {
					
                var $errorDiv = $('<div/>', {'id': 'errorM'}).html('Something went wrong, please try again.');
				$('#error').append($errorDiv);
				$errorDiv.fadeTo(4000, 0.00);
				$errorDiv.slideUp(2000, function(){$(this).remove();});
				$("#saveComment").val("Post");
				$("#working").toggleClass("hide", true);
            	}
            	}); 	
			 
        return false;
});	
	
	
});
