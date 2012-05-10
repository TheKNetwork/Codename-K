<?PHP
/** Basic JSON Store php script.
 *  You can use this if you have PHP installed, or implement your own.
 *
 *  Note: this is only as secure as the session mechanism you use.
 *
 *  TODO: define store interaction here
 *  update removes keys with null values
 */
session_start();
if ($_REQUEST['set']) {
    $setArr = json_decode(stripslashes($_REQUEST['set']));
    if ($setArr) {
        foreach ($setArr as $key => $value) {
            $_SESSION[$key] = $value;
        }
        print "OK";
    } else {
        print "Error " . $_REQUEST['set'];
    }
} elseif ($_REQUEST['get']) {
    foreach (split(",", $_REQUEST['get']) as $getvar) {
        $return_array[$getvar] = $_SESSION[$getvar];
    }
    print json_encode($return_array);
} elseif ($_REQUEST['del']) {
    foreach (split(",", $_REQUEST['del']) as $getvar) {
        unset($_SESSION[$getvar]);
    }
} else {
    print "JSONStore";
}
