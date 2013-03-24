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
        d = new Date();
        $("#plateimg").attr("src", $("#plateimg").attr("src") + "?" + d.getTime());
    }

    $("a.clear").click(function() {
        $.get($(this).attr("href"), function(data) {
            reload();
            if (data == "true")
                alert("Bed cleared");
            else
                alert("Failed to clear bed");
        });
        return false;
    });

    reload();
    window.setInterval(reload, 5000);
});
