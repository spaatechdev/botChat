function message_store(message, message_type=null, redirect_path=null) {
    console.log(message);
    console.log(redirect_path);
    $.ajax({
        type: "POST",
        url: "/message_store",
        data: ({ message: message, message_type: message_type }),
        success: function (message_response) {
            if (redirect_path != null) {
                window.location.href = redirect_path
            } else {
                window.location.reload()
            }
        }
    });
}