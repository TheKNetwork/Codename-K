//popover on # of users to show the users in a class
$("a[rel=users]").popover();

//Shows Create Class input row if .create-class is clicked 
$("#create-class").bind('click', function () {
	$("#create-class-row").show("slow");
//	$("#create-class-row").css("display", "table-row");
	$("#id_class_name").focus();
});

//Hides Create Class input row if .cancel-class-creation is clicked
$("#cancel-class-creation").bind('click', function () {
	$("#create-class-row").hide()
//	$("#create-class-row").css("display", "hidden");
});

