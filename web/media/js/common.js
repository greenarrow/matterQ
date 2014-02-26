$(document).ready(function() {
    function bind() {
        $("a.detail").unbind("click").click(function() {
            $.get($(this).attr("href"), function(data) {
                alert(data);
            });
            return false;
        });

        $("a.cancel").unbind("click").click(function() {
            $.get($(this).attr("href"), function(data) {
                reload();
                if (data != "true")
                    alert("Failed to cancel");
            });
            return false;
        });
    }

    function reload() {
        $("#status").load("/ajax/lp/status", bind);
        $("#queue").load("/ajax/lp/queue", bind);
        $("#log").load("/ajax/lp/log", bind);
        d = new Date();
        $("#plateimg").attr("src", $("#plateimg").attr("src").split("?", 1)[0]
                                   + "?" + d.getTime());
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

    $("div.menu > select").change(function() {
        if (confirm("Are you sure you want to " +
                    $(this).val() + "?") == true) {
            $.get("/ajax/menu/" + $(this).val());
        }

        $(this).val("");
    });

    $("#ulform").ajaxForm({
        beforeSend: function() {
            $("#ulprogress").show();

            var percentVal = "0%";
            $("#ulprogress > .bar").width(percentVal);
            $("#ulprogress > .percent").html(percentVal);
        },
        uploadProgress: function(event, position, total, percentComplete) {
            var percentVal = percentComplete + "%";
            $("#ulprogress > .bar").width(percentVal)
            $("#ulprogress > .percent").html(percentVal);
        },
        complete: function(xhr) {
            $("#ulprogress").hide();
            alert(xhr.responseText);
        }
    });

    reload();
    window.setInterval(reload, 5000);
});
