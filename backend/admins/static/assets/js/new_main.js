function submit_form(id) {
    console.log(id)
    let form = $(`#${id}`)
    let url = form.attr("action")
    let data = $(`#${id} :input`).serialize()

    $.ajax({
        url: url,
        data: data,
        type: 'POST',
        success: () => {
            $(form).parent().remove()
        }
    })

}

function form_submit_in_table(id) {
    $(`#${id}`).submit()
}

function copy(that) {
    var inp = document.createElement('input');
    document.body.appendChild(inp)
    inp.value = that.textContent.trim()
    inp.select();
    document.execCommand('copy', false);
    inp.remove();

    $('.messages').append(
        `
            <div class="alert alert-success notifs" role="alert">
                Скопировано
            </div>
        `
    )

    setTimeout(() => {
        $('.notifs').remove()
    }, 5000)
}


$(document).on("click", '.fe.fe-copy', (e) => {
    copy(e.target)
})


$('.dropzone').each((i, e) => {
    let accept = $(e).attr("data-accept")

    if (accept == undefined) {
        accept = '.jpg, .png, .jpeg, .webp, .ico'
    }

    Dropzone.options.myAwesomeDropzone = false;
    Dropzone.autoDiscover = false;
    var myDropzone = new Dropzone(e, {
        url: $(e).attr("data-url"),
        parallelUploads: 1,
        acceptedFiles: accept,
        maxFilesize: 2,
        maxFiles: $(e).attr('data-max'),
        params: {
            "csrfmiddlewaretoken": document.querySelector('input[name="csrfmiddlewaretoken"]').value,
            "key": $(e).attr('data-key'),
            'id': $('input[name="id"]').val(),
            'url': window.location.href
        },
        previewsContainer: `#${$(e).find('.dz-preview-container').attr('id')}`,
        success: (file, response) => {
            var removeButton = Dropzone.createElement(`<a class="dz-remove" data-dz-remove>Удалить</a>`);
            removeButton.addEventListener("click", function (ev) {
                ev.preventDefault();
                ev.stopPropagation();
                myDropzone.removeFile(file);

                data = {}
                data["csrfmiddlewaretoken"] = $('input[name="csrfmiddlewaretoken"]').val()
                data['key'] = $(e).attr('data-key')
                data['file'] = response

                $.ajax({
                    url: $(e).attr('data-delete'),
                    type: 'POST',
                    data: data,
                    success: () => {
                        console.log('success')
                    },
                    error: () => {
                        console.log('error')
                    }
                })

            });
            file.previewElement.appendChild(removeButton);
        }
    });


})



setTimeout(() => {
    $('.notifs').remove()
}, 3000)


