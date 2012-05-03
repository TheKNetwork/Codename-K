/**
 * This js file contains common methods that can be used
 * to interact with the knet api for classrooms and schools
 */

/**
* uses a simple ajax call to post data to a url, which is
* the equivalent of posting a form
*/
function add_class(school_id, classroom_name) {
    $.ajax({
        type: "POST",
        url: "#",
        data: { name: "John", location: "Boston" }
        }).done(function( msg ) {
            alert( "Data Saved: " + msg );
        });
}
