$(".change_offer").on('click', (e) => {
    data = {}
    data.id = $(e.target).attr('data-id')
    data["csrfmiddlewaretoken"] = $('[name="csrfmiddlewaretoken"]').val()

    $.ajax({
        url: "/admin/offers/change_status",
        type: "POST",
        data: data,
        success: (data) => {
            $('.messages').append(
                `
                    <div class="alert alert-success notifs" role="alert">
                        Объект успешно изменен.
                    </div>
                    `
            )
            setTimeout(() => {
                $('.notifs').remove()
            }, 3000)
            
            if(data['status']) {
                $(e.target).html('<i class="fe fe-eye"></i>')
            } else {
                $(e.target).html('<i class="fe fe-eye-off"></i>')
            }
        }
    })

})
