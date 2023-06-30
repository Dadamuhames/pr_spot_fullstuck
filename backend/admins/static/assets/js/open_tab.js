$(document).ready(() => {
    let url = window.location.href;

    let id = url.split("#").slice(-1)

    console.log(id);

    $(`[data-bs-target="#${id[0]}"]`).tab("show")
})