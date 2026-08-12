/*==================================================
                UMI DASHBOARD JS
==================================================*/

document.addEventListener("DOMContentLoaded",function(){

    initializeDashboard();

});

/*==================================================
                INITIALIZE
==================================================*/

function initializeDashboard(){

    animateSummaryCards();

    initializeActionCards();

    initializeNotification();

    highlightSidebar();

}

/*==================================================
                SUMMARY CARD ANIMATION
==================================================*/

function animateSummaryCards(){

    const cards=document.querySelectorAll(".summary-card");

    cards.forEach((card,index)=>{

        card.style.opacity="0";

        card.style.transform="translateY(20px)";

        setTimeout(()=>{

            card.style.transition="0.5s";

            card.style.opacity="1";

            card.style.transform="translateY(0px)";

        },index*120);

    });

}

/*==================================================
                ACTION CARD CLICK EFFECT
==================================================*/

function initializeActionCards(){

    const cards=document.querySelectorAll(".action-card");

    cards.forEach(card=>{

        card.addEventListener("click",function(){

            this.style.transform="scale(0.98)";

            setTimeout(()=>{

                this.style.transform="";

            },120);

        });

    });

}
