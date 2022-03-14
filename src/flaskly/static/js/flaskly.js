async function flasklySubmitForm(frm) {
    fetch(frm.action, {
        method: 'POST',
        body: new FormData(frm),
    })
        .then(response => response.json())
        .then(data => {
            flasklyFormResponse(data, frm);

        })
        .catch((error) => {
            console.error('Error:', error);
            flasklyToast(error);
        });


}

function flasklyFormResponse(data, frm = null, el = null) {
    console.log(data);

    switch (data.action) {
        case 'toast':
            flasklyToast(data.msg);
            break;
        case 'redirect':
            flasklyRedirect(data.destination);
            break;
        case 'replace':
            if (frm == null) {
                console.error("Stateless element is not set!");
                throw "Stateless element is not set!";
            }
            flasklyReplaceElement(frm, data.html);
            break;
        case 'eval':
            eval(data.code);
            break;
        case 'state':
            if (el == null) {
                console.error("Stateful element is not set!");
                throw "Stateful element is not set!";
            }
            flasklyUpdateState(el, data.new_state);

    }
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

function flasklyUpdateState(el, new_state) {
    updateDict(el.formState, new_state);
}


function updateDict(obj, src) {
    for (const key in src) {
        // console.log('Type of ' + key + ' is: ' + typeof src[key] + '/' + typeof obj[key]);
        // console.log(src[key]);
        if (key in obj && typeof src[key] == 'object' && typeof obj[key] == 'object')
            updateDict(obj[key], src[key]);
        else
            obj[key] = src[key];
    }
}

function FlasklyStatefulForm(formState) {
    return {
        formId: formState.id,
        formState: formState,
        formElement: null,
        // idSuffix: idSuffix,
        submitForm() {
            this.formState.errors.push('test1');

            // this.formMessage = "";
            // this.formLoading = false;
            // this.buttonText = "Submitting...";
            fetch(this.formState.uri, {
                method: "POST",
                body: new FormData(this.getFormElement()),

                // headers: {
                //     "Content-Type": "application/json",
                //     Accept: "application/json",
                // },
                // body: JSON.stringify(this.formData),
            })
                .then(response => response.json())
                .then(data => {
                    flasklyFormResponse(data, this.formElement, this);

                })
                .catch(() => {
                    console.error('Error:', error);
                    flasklyToast(error);
                })
                .finally(() => {
                    // this.formLoading = false;
                    // this.buttonText = "Submit";
                });
        },
        getFormElement() {
            if (this.formElement == null) {
                this.formElement = document.getElementById(this.formState.id);
            }
            return this.formElement;
        },


    };
}