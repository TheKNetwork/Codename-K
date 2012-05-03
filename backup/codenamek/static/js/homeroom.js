//popover on # of users to show the users in a class
$("a[rel=users]").popover();

//Shows Create Class input row if .create-class is clicked 
$("#create-class").bind('click', function () {
	$("#create-class-row").show("slow");
	$("#id_class_name").focus();
	$("#create-class").addClass("disabled");
});

//Hides Create Class input row if .cancel-class-creation is clicked
$("#cancel-class-creation").bind('click', function () {
	$("#create-class-row").hide()
	$("#create-class").removeClass("disabled");
});
