$(document).on('submit', 'form#prod_form', (e) => {
    e.preventDefault()
    let url = $(e.target).attr("action")
    let data = new FormData(e.target)

    $('#save_btn').html(
        `
            <button class="btn btn-primary" type="button" disabled>
                <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                Loading...
            </button>
        `  
    )

    $.ajax({
        url: url,
        type: 'POST',
        processData: false,
        contentType: false,
        datatype: 'json', 
        data: data,
        success: (data) => {
            window.location = '/admin/windows'
        },
        error: (error) => {

            $('.messages').append(

                `
                <div class="alert alert-danger alert-dismissible fade show notifs" role="alert">
                    <strong>Ошибка!</strong> Форма заполнена неверно!
            
                    <!-- Button -->
                    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            
                </div>
            `
            )


            $('#save_btn').html(`<button class="btn btn-primary ms-2" onclick="$('#prod_form').submit()">Сохранить</button >`)
            $('.invalid-feedback').html('')

            let data = error.responseJSON

            for(let key in data) {
                let inputs = $(`.invalid-feedback[data-id='${key}']`)
                console.log(inputs.find('.invalid-feedback'))

                console.log(data[String(key)])

                for (let error_key in data[String(key)]){
                    console.log(error_key)
                    let error = data[String(key)][String(error_key)][0]
                    $(`.invalid-feedback[data-id='${key}'][data-key="${String(error_key)}"`).first().html(error)
                    console.log($(inputs).find(`[data-key="${error_key}"`))
                }
            }

        }
    })

})



$(document).on('click', '.delete_sub_variant.no-ajax', (e) => {
    if ($(e.target).parent().parent().parent().find('tr').length == 1) {
        $(e.target).parent().parent().parent().parent().parent().parent().remove()
    } else {
        $(e.target).parent().parent().remove()
    }
})



$(document).on('click', '.delete_img.with-ajax', (e) => {

    let result = confirm("Вы уверены, что хотите удалить изображение?")

    if (result) {
        let data = {}
        data['obj_id'] = $(e.target).attr("data-id");
        data['csrfmiddlewaretoken'] = $('input[name="csrfmiddlewaretoken"]').val()
        data['url'] = window.location.href


        $(e.target).parent().append(
            `
                <div class="display-image d-flex justify-content-center align-items-center">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                </div>
            `
        )

        $.ajax({
            url: '/admin/window_image/delete',
            type: 'POST',
            data: data,
            success: () => {
                $(e.target).parent().find('.display-image.d-flex.justify-content-center.align-items-center').remove()
                $(e.target).removeClass('active').removeClass('with-ajax').addClass('no-ajax')
                $(e.target).parent().find('.display-image').css('backgroundImage', '').removeClass("d-block").removeClass('d-flex')

                $('.messages').append(
                    `
                    <div class="alert alert-success notifs" role="alert">
                        Объект успешно удален.
                    </div>
                    `
                )
                setTimeout(() => {
                    $('.notifs').remove()
                }, 3000)
            }
        })
    }
})



$(document).on('click', '.delete_variant_btn.with-ajax', (e) => {
    let data = {}
    data['csrfmiddlewaretoken'] = $('input[name="csrfmiddlewaretoken"]').val()
    data.type = $(e.target).attr('data-type')

    let result = confirm('Вы уверены, что хотите удалить все эти варианты?')

    if (!result) {
        return;
    }


    $('.loader-block').addClass('d-flex')

    $.ajax({
        url: '/admin/delete_windows_by_type',
        type: 'POST',
        data: data,
        success: () => {
            $(e.target).parent().parent().remove()
            $('.loader-block').removeClass('d-flex')


            $('.messages').append(
                `
                <div class="alert alert-success notifs" role="alert">
                    Объект успешно удален.
                </div>
                `
            )
            setTimeout(() => {
                $('.notifs').remove()
            }, 3000)
        }
    })

})





$(document).on('click', '.delete_sub_variant.with-ajax', (e) => {
    let url = '/admin/delete'

    let result = confirm('Вы уверены, что хотите удалить этот вариант?')

    if (!result) {
        return;
    }

    let data = {}
    data['csrfmiddlewaretoken'] = $('input[name="csrfmiddlewaretoken"]').val()
    data.item_id = $(e.target).attr('data-id')
    data.model_name_del = 'Windows'
    data.app_name_del = 'main'
    data.url = $(e.target).attr("data-url")

    $('.loader-block').addClass('d-flex')
    

    $.ajax({
        url: url,
        type: 'POST',
        data: data,
        success: () => {
            if ($(e.target).parent().parent().parent().find('tr').length == 1) {
                $(e.target).parent().parent().parent().parent().parent().parent().remove()
            } else {
                $(e.target).parent().parent().remove()
            }
            $('.loader-block').removeClass('d-flex')


            $.ajax({
                url: '/admin/delete',
                type: 'POST',
                data: data,
                success: () => {
                    $(e.target).removeClass('active')
                    $(e.target).parent().find('.display-image').css('backgroundImage', '').removeClass("d-block").removeClass('d-flex')

                    $('.messages').html(
                        `
                        <div class="alert alert-success notifs" role="alert">
                            Объект успешно удален.
                        </div>
                        `
                    )
                    setTimeout(() => {
                        $('.notifs').remove()
                    }, 3000)
                }
            })
        },
        
    })
})



$(document).on("change", '.color-select', (e) => {
    let block = $(e.target).parent().parent().parent().parent().parent()
    let btn = $(block).find("button.add_sub_vars")

    let color_name = $(e.target).find(':selected').html();

    $(btn).attr('data-color', $(e.target).val())
    $(btn).attr('data-colorname', color_name)


    $(block).find('select.color-select').each((i, el) => {
        if (el != e.target) {
            $(el).html(`
                <option value="${$(e.target).val()}" selected>${color_name}</option>
            `)
        }
    })
})