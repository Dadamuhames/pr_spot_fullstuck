const submit_categry_form = (e, url, data) => {
    $.ajax({
        url: url,
        type: 'POST',
        data: data,
        success: (data) => {
            window.location.reload();
        },
        error: (error) => {
            $(e.target).find(".invalid-feedback").css('display', 'block')
            $(e.target).find(".invalid-feedback").html(error.responseJSON.error.title)
        }
    })
}


$(document).on('click', '#add_category_modal', () => {
    $('#category_modal').find('.invalid-feedback').css('display', 'none')
    $('#category_modal').find('input[type="text"]').val("")
    $('#category_modal').modal("show")
})


$(document).on("submit", 'form#add_category_form', (e) => {
    e.preventDefault()
    let data = $(e.target).serialize();
    let url = $(e.target).attr('action')
    submit_categry_form(e, url, data)
})


$(document).on("click", '#edit_ctg_btn', (e) => {
    let id = $(e.target).attr('data-id');
    let url = '/admin/get_faq_ctg'
    $('#edit_category_form').find('.invalid-feedback').css('display', 'none')

    $.ajax({
        url: url,
        type: 'GET',
        data: {"id": id},
        success: (data) => {
            console.log(data)
            
            $('#edit_category_form').find('input[name="id"]').val(data.id)
            
            for (let [key, val] of Object.entries(data.title)) {
                $('#edit_category_form').find(`input[name="title#${key}"]`).val(val)
            }
        }
    })

    $('#edit_ctg_modal').modal("show")
})


$(document).on('submit', 'form#edit_category_form', (e) => {
    e.preventDefault()
    let data = $(e.target).serialize();
    let id = $(e.target).find('[name="id"]').val();
    let url = `/admin/faq/categories/${id}/edit`
    submit_categry_form(e, url, data);
})