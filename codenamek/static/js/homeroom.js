$("a[rel=users]").popover();

$(".create-class").bind('click', function () {
	$("#create-class-row").css("display", "table-row");
	$("#id_class_name").focus();
});

$(".cancel-class-creation'").bind('click', function () {
	$("#create-class-row").css("display", "none");
});

