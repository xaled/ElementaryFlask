var Flaskly = {
    submitForm: async function (frm) {
        formData = new FormData(frm);
        var object = {};
        formData.forEach(function (value, key) {
            object[key] = value;
        });
        console.log(object);
        fetch(frm.action, {
            method: 'POST',
            body: new FormData(frm),
        })
            .then(response => response.json())
            .then(data => {
                Flaskly.formResponse(data, frm);

            })
            .catch((error) => {
                console.error('Error:', error);
                Flaskly.toast(error);
            });


    },

    formResponse: function (formResponseData, frm = null, el = null) {
        // console.log(data);
        for (formAction of formResponseData.actions) {
            switch (formAction.action) {
                case 'toast':
                    Flaskly.toast(
                        formAction.params.message,
                        formAction.params.message_type,
                        formAction.params.message_title,
                        formAction.params.sticky,
                        formAction.params.timeout,
                    );
                    break;
                case 'redirect':
                    Flaskly.redirect(formAction.params.destination);
                    break;
                case 'replace':
                    if (frm == null) {
                        console.error("Stateless element is not set!");
                        throw "Stateless element is not set!";
                    }
                    Flaskly.replaceElement(frm, formAction.params.html);
                    break;
                case 'eval':
                    eval(formAction.params.code);
                    break;
                case 'state':
                    if (el == null) {
                        console.error("Stateful element is not set!");
                        throw "Stateful element is not set!";
                    }
                    Flaskly.updateState(el, formAction.params.new_state);

            }
        }
    },

    toast: function (msg, type = 'error', title = '', sticky = false, timeout = 10) {
        alert(msg);
    },

    redirect: function (dst) {
        window.location.replace(dst);
    },

    replaceElement: function (el, new_content) {
        // document.open();
        // document.write(new_content);
        // document.close();
        el.outerHTML = new_content;

    },

    updateState: function (el, new_state) {
        Flaskly.updateDict(el, new_state);
    },


    updateDict: function (obj, src) {
        for (const key in src) {
            // console.log('Type of ' + key + ' is: ' + typeof src[key] + '/' + typeof obj[key]);
            // console.log(src[key]);
            if (key in obj && Array.isArray(src[key]) && Array.isArray(obj[key]))
                Flaskly.updateArray(obj[key], src[key]);
            else if (key in obj && typeof src[key] == 'object' && typeof obj[key] == 'object')
                Flaskly.updateDict(obj[key], src[key]);
            else
                obj[key] = src[key];
        }
    },

    updateArray: function (arr1, arr2) {
        arr1.length = 0;
        for (const key in arr2) arr1.push(arr2[key]);

    },

    statefulForm: function (formState) {
        return {
            formId: formState.id,
            formState: formState,
            formElement: null,
            // idSuffix: idSuffix,
            submitForm() {

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
                        Flaskly.formResponse(data, this.formElement, this);

                    })
                    .catch(() => {
                        console.error('Error:', error);
                        Flaskly.toast(error);
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
};