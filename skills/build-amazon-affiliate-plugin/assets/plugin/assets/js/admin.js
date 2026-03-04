/**
 * Admin JavaScript for Ad Symbiont
 */

jQuery(document).ready(function($) {
    // Clear cache button
    $('#ad-symbiont-clear-cache').on('click', function() {
        var $button = $(this);
        var $msg = $('#ad-symbiont-clear-cache-msg');
        
        $button.prop('disabled', true).text('Clearing...');
        
        $.ajax({
            url: adSymbiont.ajaxUrl,
            type: 'POST',
            data: {
                action: 'ad_symbiont_clear_cache',
                nonce: adSymbiont.nonce
            },
            success: function(response) {
                if (response.success) {
                    $msg.text('Cache cleared! (' + response.data.deleted + ' items)').addClass('ad-symbiont-success');
                    setTimeout(function() {
                        $msg.text('').removeClass('ad-symbiont-success');
                    }, 3000);
                } else {
                    $msg.text('Error clearing cache').addClass('ad-symbiont-error');
                }
            },
            error: function() {
                $msg.text('Error clearing cache').addClass('ad-symbiont-error');
            },
            complete: function() {
                $button.prop('disabled', false).text('Clear Cache Now');
            }
        });
    });
});
