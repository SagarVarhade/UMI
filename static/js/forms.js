/*==================================================
                UMI FORMS JS
==================================================*/

document.addEventListener("DOMContentLoaded",function(){

    initializeForms();

});

/*==================================================
                INITIALIZE
==================================================*/

function initializeForms(){

    initializePasswordValidation();

    initializeRequiredFields();

    initializeDateRestriction();

    initializeNumberValidation();

}

/*==================================================
                PASSWORD MATCH
==================================================*/

function initializePasswordValidation(){

    const passwords=document.querySelectorAll("input[type='password']");

    if(passwords.length<2){

        return;

    }

    const password=passwords[0];

    const confirmPassword=passwords[1];

    confirmPassword.addEventListener("input",function(){

        if(password.value!==confirmPassword.value){

            confirmPassword.setCustomValidity("Passwords do not match");

        }

        else{

            confirmPassword.setCustomValidity("");

        }

    });

}

/*==================================================
                REQUIRED FIELDS
==================================================*/

function initializeRequiredFields(){

    const required=document.querySelectorAll("[required]");

    required.forEach(field=>{

        field.addEventListener("blur",function(){

            if(this.value.trim()===""){

                this.classList.add("error");

                this.classList.remove("success");

            }

            else{

                this.classList.remove("error");

                this.classList.add("success");

            }

        });

    });

}

/*==================================================
                DATE
==================================================*/

function initializeDateRestriction(){

    document.querySelectorAll("input[type='date']").forEach(field=>{

        if(field.dataset.future==="true"){

            field.min=new Date().toISOString().split("T")[0];

        }

    });

}

/*==================================================
                NUMBER ONLY
==================================================*/

function initializeNumberValidation(){

    document.querySelectorAll(".number-only").forEach(field=>{

        field.addEventListener("input",function(){

            this.value=this.value.replace(/[^0-9]/g,"");

        });

    });

}

/*==================================================
                MOBILE VALIDATION
==================================================*/

function initializeMobileValidation(){

    document.querySelectorAll(".mobile").forEach(field=>{

        field.setAttribute("maxlength","10");

        field.addEventListener("input",function(){

            this.value=this.value.replace(/[^0-9]/g,"");

            if(this.value.length>10){

                this.value=this.value.slice(0,10);

            }

        });

    });

}

/*==================================================
                EMAIL VALIDATION
==================================================*/

function initializeEmailValidation(){

    document.querySelectorAll("input[type='email']").forEach(field=>{

        field.addEventListener("blur",function(){

            const pattern=/^[^\s@]+@[^\s@]+\.[^\s@]+$/;

            if(this.value!=="" && !pattern.test(this.value)){

                this.classList.add("error");

                this.classList.remove("success");

            }

            else if(this.value!==""){

                this.classList.remove("error");

                this.classList.add("success");

            }

        });

    });

}

/*==================================================
                AUTO UPPERCASE
==================================================*/

function initializeUppercase(){

    document.querySelectorAll(".uppercase").forEach(field=>{

        field.addEventListener("input",function(){

            this.value=this.value.toUpperCase();

        });

    });

}

/*==================================================
                CLEAR FORM
==================================================*/

function clearCurrentForm(){

    const form=document.querySelector("form");

    if(form){

        form.reset();

    }

    document.querySelectorAll(".success,.error").forEach(field=>{

        field.classList.remove("success");

        field.classList.remove("error");

    });

}

/*==================================================
                RESET BUTTON
==================================================*/

function initializeResetButton(){

    const resetButton=document.querySelector(".secondary-btn");

    if(resetButton){

        resetButton.addEventListener("click",function(){

            if(confirm("Clear all entered data?")){

                clearCurrentForm();

            }

        });

    }

}
/*==================================================
                FORM SUBMIT
==================================================*/

function initializeFormSubmit(){

    document.querySelectorAll("form").forEach(form=>{

        form.addEventListener("submit",function(e){

            let valid=true;

            const required=form.querySelectorAll("[required]");

            required.forEach(field=>{

                if(field.value.trim()===""){

                    field.classList.add("error");

                    valid=false;

                }

            });

            if(!valid){

                e.preventDefault();

                alert("Please fill all required fields.");

                return;

            }

            disableSubmitButton(form);

        });

    });

}

/*==================================================
            DISABLE SUBMIT BUTTON
==================================================*/

function disableSubmitButton(form){

    const button=form.querySelector("button[type='submit']");

    if(button){

        button.disabled=true;

        button.innerHTML="Please Wait...";

    }

}

/*==================================================
            ENTER KEY NAVIGATION
==================================================*/

function initializeEnterNavigation(){

    const fields=document.querySelectorAll(

        "input,select,textarea"

    );

    fields.forEach((field,index)=>{

        field.addEventListener("keydown",function(e){

            if(e.key==="Enter"){

                e.preventDefault();

                if(fields[index+1]){

                    fields[index+1].focus();

                }

            }

        });

    });

}

/*==================================================
                AUTO FOCUS
==================================================*/

function focusFirstInput(){

    const first=document.querySelector(

        "input,select,textarea"

    );

    if(first){

        first.focus();

    }

}

/*==================================================
            TEXTAREA LIMIT
==================================================*/

function initializeTextareaLimit(){

    document.querySelectorAll("textarea").forEach(area=>{

        area.addEventListener("input",function(){

            const max=this.getAttribute("maxlength");

            if(max && this.value.length>max){

                this.value=this.value.substring(0,max);

            }

        });

    });

}

/*==================================================
            TRIM INPUTS
==================================================*/

function trimInputs(){

    document.querySelectorAll("input").forEach(field=>{

        field.addEventListener("blur",function(){

            this.value=this.value.trim();

        });

    });

}

/*==================================================
            INITIALIZE ALL
==================================================*/

document.addEventListener("DOMContentLoaded",function(){

    initializeForms();

    initializeFormSubmit();

    initializeEnterNavigation();

    initializeTextareaLimit();

    trimInputs();

    focusFirstInput();

});
