experiments = function() {
    return {
        confirm_human: function() {
            //$.post("/experiments/confirm_human/");
            var xhr = new XMLHttpRequest();
            xhr.open('POST', '/experiments/confirm_human/');
            xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
            xhr.onload = function() {
                if (xhr.status < 200 || xhr.status > 299) {
                    throw 'POST to "/experiments/confirm_human/" failed. Returned status of ' + xhr.status;
                }
            };
            xhr.send();
        },
        goal: function(goal_name) {
            // $.post("/experiments/goal/" + goal_name);
            var xhr = new XMLHttpRequest();
            xhr.open('POST', '/experiments/goal/' + goal_name + '/');
            xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
            xhr.onload = function() {
                if (xhr.status !== 200) {
                    throw 'POST to "/experiments/goal/" failed. Returned status of ' + xhr.status;
                }
            };
            xhr.send();
        }
    };
}();


/**
 * Simple helper, prefixed only to avoid name collisions.
 */
function experimentsCreateCookie(name, value, path, days) {
    var expires;
    if (days) {
        var date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        expires = "; expires=" + date.toGMTString();
    }
    else {
        expires = "";
    }
    document.cookie = name + "=" + value + expires + "; path=" + path;
}

/**
 * Create a global delegate for click events.
 * Trigger a cookie if the required data attribute is present on the clicked node.
 */
if (document.addEventListener) {
    // sets the cookie in the capturing phase so that in the bubbling phase we guarantee that if a request is being issued it will contain the new cookie as well
    document.addEventListener("click", function(event) {
        var goal_name = event.target.getAttribute('data-experiments-goal');
        if (goal_name) {
            experimentsCreateCookie("experiments_goal", goal_name, '/')
            //$.cookie("experiments_goal", $(event.target).data('experiments-goal'), { path: '/' });
        }
    }, true);
} else { // IE 8
    // we don't care about IE8  B-)
    /*
    $(document).delegate('[data-experiments-goal]', 'click', function(e) {
        // if a request is fired by the click event, the cookie might get set after it, thus the goal will be recorded with the next request (if there will be one)
        $.cookie("experiments_goal", $(this).data('experiments-goal'), { path: '/' });
    });
    */
}
