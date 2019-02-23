// $("li").click(function() {

// 	if($(this).css("color") === "rgb(128, 128, 128)") {
// 		// console.log("It is currently gray!");
// 		$(this).css({
// 			color: "black",
// 			textDecoration: "none"
// 		});
// 	}
// 	else {
// 		$(this).css({
// 			color: "gray",
// 			textDecoration: "line-through"
// 		});
// 	}	
// });


$("ul").on("click", "li", function() {
	$(this).toggleClass("completed");
});

$("ul").on("click", "span", function(event) {
	$(this).parent().fadeOut(500, function() {
		$(this).remove();
	});
	event.stopPropagation();
});

$("input[type='text']").keypress(function(event) {
	if(event.which === 13) {
		var todotext = $(this).val();

		$(this).val("");

		$("ul").append("<li><span><i class='fa fa-trash'></i></span> " + todotext + "</li>");
	}
});

$(".fa-plus").click(function() {
	$("input[type='text']").fadeToggle();
});