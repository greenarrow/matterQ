$(document).ready(function() {
    function bind() {
        $("a.detail").click(function() {
            $.get($(this).attr("href"), function(data) {
                alert(data);
            });
            return false;
        });

        $("a.cancel").click(function() {
            $.get($(this).attr("href"), function(data) {
                alert(data);
                reload();
            });
            return false;
        });
    }

    function reload() {
        $("#status").load("/ajax/lp/status", bind);
        $("#queue").load("/ajax/lp/queue", bind);
    }

    reload();
    window.setInterval(reload, 5000);
});
