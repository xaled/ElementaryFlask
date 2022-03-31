let Flaskly = {
    privateSubmitForm: function (frm, action, body) {
        fetch(action, {
            method: 'POST',
            body: body,
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
    submitForm: async function (frm) {
        Flaskly.privateSubmitForm(frm, frm.action, new FormData(frm))
    },

    listingCheckboxClick: function (el) {
        el.querySelector("input[type=checkbox]").click();
    },

    submitListingAction: async function (button, frm_id = null) {
        // let frm = document.getElementById(frm_id);
        // let data = Flaskly.serializeForm(frm);
        let frm = button.form;

        if (!frm) {
            if (frm_id) {
                frm = document.getElementById(frm_id);
            } else {
                frm = button.closest("form");
            }
        }

        let frmData = new FormData(frm);
        let button_info = JSON.parse(button.dataset.info);
        let ids = Array();

        if (button_info.item_id === 'batch') {
            if (!frmData.has('id')) {
                return null;
            }
            ids = frmData.getAll('id');

        } else {
            ids.push(button_info.item_id);
        }
        // frmData = FormData();
        for (const id_ of ids) {
            frmData.append("ids", id_);
        }
        frmData.append("action", button_info.action);
        frmData.delete("id");
        return Flaskly.privateSubmitForm(null, "", frmData);

    },

    serializeForm: function (frm, doseq = true) {
        return Flaskly.serializeFormData(new FormData(frm));

    },

    serializeFormData: function (formData, doseq = true) {
        let object = {};
        formData.forEach(function (value, key) {
            if (!(key in object && doseq)) {
                object[key] = value;
            } else {
                if (!Array.isArray(object[key])) {
                    object[key] = Array(object[key]);
                }
                object[key].push(value);

            }
        });
        return object;
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
                case 'refresh':
                    Flaskly.refresh_page();
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
        // window.location.replace(dst);
        window.location.href = dst;
    },

    refresh_page: function () {
        // window.location.replace(dst);
        window.location.reload();
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
    },

    initListingCheckboxes: function (parent = null) {
        let lastChecked = null;
        if (!parent) {
            parent = document;
        }

        const chkboxes = Array.from(parent.querySelectorAll('.fl-checkbox'));
        const links = Array.from(parent.querySelectorAll('.fl-select-link'));
        const batch_buttons = parent.querySelector('.fl-batch-buttons');
        const select_all_button = links[0];
        const select_all_checkbox = select_all_button.querySelector('input');
        // const select_all_checkbox = links[0];


        const is_checked = (el) => el.checked;
        const update_batch_buttons_visibility = (show) => {
            if (batch_buttons) {
                if (show) {
                    batch_buttons.classList.remove("d-none");
                } else {
                    batch_buttons.classList.add("d-none");
                }
            }
        };

        const update_select_all_checkbox = (state) => {
            if (select_all_checkbox) {
                switch (state) {
                    case 'all':
                        select_all_checkbox.checked = true;
                        select_all_checkbox.indeterminate = false;
                        // select_all_checkbox.innerHTML = '☐';
                        break;
                    case 'some':
                        select_all_checkbox.checked = false;
                        select_all_checkbox.indeterminate = true;
                        // select_all_checkbox.innerHTML = '☑';
                        break;
                    default:
                        select_all_checkbox.checked = false;
                        select_all_checkbox.indeterminate = false;
                    // select_all_checkbox.innerHTML = '';

                }
            }
        };


        const update_on_change = () => {
            let checked = chkboxes.filter(is_checked);
            if (checked.length === chkboxes.length) { // all
                update_batch_buttons_visibility(true);
                update_select_all_checkbox('all');
            } else if (checked.length > 0) { // some
                update_batch_buttons_visibility(true);
                update_select_all_checkbox('some');
            } else { // none
                update_batch_buttons_visibility(false);
                update_select_all_checkbox('none');
            }

        };

        chkboxes.forEach(item => {
            item.addEventListener('click', event => {
                let currentChecked = event.target;

                if (lastChecked) {
                    if (event.shiftKey) {
                        let start = chkboxes.indexOf(currentChecked);
                        let end = chkboxes.indexOf(lastChecked);


                        chkboxes.slice(Math.min(start, end), Math.max(start, end) + 1).forEach(item => {
                            item.checked = lastChecked.checked;
                        });
                    }
                }

                lastChecked = currentChecked;
                update_on_change();
                event.stopPropagation();
            })
        });

        links.forEach(item => {
            item.addEventListener('click', event => {
                let select_type = event.target.dataset.select;
                lastChecked = null;
                let default_state = !chkboxes.every(is_checked);

                chkboxes.forEach(item => {
                    switch (select_type) {
                        case 'all':
                            item.checked = true;
                            break;
                        case 'none':
                            item.checked = false;
                            break;
                        case 'reverse':
                            item.checked = !item.checked;
                            break;
                        default:
                            item.checked = default_state;

                    }

                });

                update_on_change();
                event.stopPropagation();

            })
        });

        // select_all_checkbox.addEventListener('click', event => {
        //     console.log('test');
        //     select_all_button.click();
        //     event.stopPropagation();
        // })

        update_on_change();

    }
};