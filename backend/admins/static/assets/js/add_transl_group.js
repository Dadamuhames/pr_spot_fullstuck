$('[data-bs-target="#newGroupModal"]').on("click", (e) => {

    $('#newGroupModal').find('[name="title"]').val("")
    $('#newGroupModal').find('[name="sub_text"]').val("")
    $('#newGroupModal').find('#transl_group_key_error').html("")
    $('#newGroupModal').find('#transl_group_title_error').html("")

    $('#newGroupModal').modal('show')
})


$('#add_new_group_form').on("submit", (e) => {
    e.preventDefault()  
    let data = $(e.target).serialize()
    let url = $(e.target).attr('action') 
    console.log($(e))          

    $.ajax({
        url: url,
        type: 'POST',
        data: data,
        datatype: 'json',
        success: (data) => {
            if ('key_error' in data) {
                $('#transl_group_key_error').css('display', 'block')
                $("#transl_group_key_error").html(data.key_error)
                return;
            } else if('title_error' in data) {
                $("#transl_group_title_error").css('display', 'block')
                $('#transl_group_title_error').html(data.title_error)
                return;
            }

            console.log(data)
            $('#group_links').html(
                $('#group_links').html() + 
                `
                    <a href="/admin/translations/${ data.id }" class="btn btn-info me-3 bg-transparent text-info group-link">${ data.name }</a>
                `
            )

            $(e.target).find('[name="title"]').val("")
            $(e.target).find('[name="sub_text"]').val("")   
            $('#newGroupModal').modal("hide")
        }
    })




})