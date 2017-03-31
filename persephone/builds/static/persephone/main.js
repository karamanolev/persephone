$(function() {
    function aPost(showConfirm) {
        if (showConfirm && !confirm('Are you sure?')) {
            return;
        }
        var csrfToken = $(this).data('csrf-token'),
            csrfTokenInput = $('<input>')
                .attr('type', 'hidden')
                .attr('name', 'csrfmiddlewaretoken')
                .val(csrfToken);
        $('<form>')
            .attr('action', $(this).attr('href'))
            .attr('method', 'post')
            .append(csrfTokenInput)
            .appendTo($('body'))
            .submit();
    }

    $('*[data-action="confirm-post"]').click(function(e) {
        e.preventDefault();
        aPost.apply(this, true);
    });

    $('*[data-action="post"]').click(function(e) {
        e.preventDefault();
        aPost.apply(this, false);
    })
});
