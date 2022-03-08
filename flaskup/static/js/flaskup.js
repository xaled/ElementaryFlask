async function flaskupSubmitForm(frm) {
    console.log(frm);
    fetch(frm.action, {
        method: 'POST',
        body: new FormData(frm),
    })
        .then(response => response.json())
        .then(data => {
            console.log(data);
            switch (data.action) {
                case 'toast':
                    flaskupToast(data.msg);
                    break;
                case 'redirect':
                    flaskupRedirect(data.destination);
                    break;
                case 'replace':
                    flaskupReplaceElement(frm, data.html);
                    break;
                case 'eval':
                    eval(data.code);

            }
        })
        .catch((error) => {
            console.error('Error:', error);
            flaskupToast(error);
        });


}

function flaskupToast(msg, type = 'error', title = '', sticky = false, timeout = 10) {
    alert(msg);
}

function flaskupRedirect(dst) {
    window.location.replace(dst);
}

function flaskupReplaceElement(el, new_content) {
    // document.open();
    // document.write(new_content);
    // document.close();
    el.outerHTML = new_content;

}