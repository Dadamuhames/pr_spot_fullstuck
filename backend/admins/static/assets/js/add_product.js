$(document).on('submit', 'form', (e) => {
    if ($('#product_ctg_select').val() == '') {
        e.preventDefault()
        $('#ctg_error').css('display', 'block')
    }
})