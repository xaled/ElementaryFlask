async function flasklySubmitForm(frm) {
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
                    flasklyToast(data.msg);
                    break;
                case 'redirect':
                    flasklyRedirect(data.destination);
                    break;
                case 'replace':
                    flasklyReplaceElement(frm, data.html);
                    break;
                case 'eval':
                    eval(data.code);

            }
        })
        .catch((error) => {
            console.error('Error:', error);
            flasklyToast(error);
        });


}

function flasklyToast(msg, type = 'error', title = '', sticky = false, timeout = 10) {
    alert(msg);
}

function flasklyRedirect(dst) {
    window.location.replace(dst);
}

function flasklyReplaceElement(el, new_content) {
    // document.open();
    // document.write(new_content);
    // document.close();
    el.outerHTML = new_content;

}