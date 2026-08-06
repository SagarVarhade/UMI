/*==================================================
                UMI MODAL JS
==================================================*/

document.addEventListener("DOMContentLoaded",function(){

    initializeModal();

});

/*==================================================
                INITIALIZE
==================================================*/

function initializeModal(){

    closeOnOutsideClick();

    closeOnEscape();

}

/*==================================================
                OPEN MODAL
==================================================*/

function openModal(modalId){

    const modal=document.getElementById(modalId);

    if(!modal){

        return;

    }

    modal.style.display="flex";

    document.body.style.overflow="hidden";

}

/*==================================================
                CLOSE MODAL
==================================================*/

function closeModal(modalId){

    const modal=document.getElementById(modalId);

    if(!modal){

        return;

    }

    modal.style.display="none";

    document.body.style.overflow="auto";

}

/*==================================================
            CLOSE ON OUTSIDE CLICK
==================================================*/

function closeOnOutsideClick(){

    window.addEventListener("click",function(e){

        document.querySelectorAll(".modal").forEach(modal=>{

            if(e.target===modal){

                modal.style.display="none";

                document.body.style.overflow="auto";

            }

        });

    });

}

/*==================================================
                ESC KEY
==================================================*/

function closeOnEscape(){

    document.addEventListener("keydown",function(e){

        if(e.key==="Escape"){

            document.querySelectorAll(".modal").forEach(modal=>{

                modal.style.display="none";

            });

            document.body.style.overflow="auto";

        }

    });

}

/*==================================================
            CONFIRM DELETE
==================================================*/

function confirmDeleteRecord(message){

    return confirm(message || "Are you sure you want to delete this record?");

}

/*==================================================
            CONFIRM LOGOUT
==================================================*/

function confirmLogout(){

    if(confirm("Are you sure you want to logout?")){

        window.location.href="/logout";

    }

}

/*==================================================
            SUCCESS POPUP
==================================================*/

function showSuccess(message){

    alert(message);

}

/*==================================================
            ERROR POPUP
==================================================*/

function showError(message){

    alert(message);

}