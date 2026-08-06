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

/*==================================================
                SIDEBAR ACTIVE MENU
==================================================*/

function highlightSidebar(){

    const currentPage=window.location.pathname;

    const links=document.querySelectorAll(".sidebar-menu a");

    links.forEach(link=>{

        const href=link.getAttribute("href");

        if(!href) return;

        if(currentPage.includes(href)){

            links.forEach(l=>l.classList.remove("active"));

            link.classList.add("active");

        }

    });

}

/*==================================================
                NOTIFICATION
==================================================*/

function initializeNotification(){

    const button=document.querySelector(".notification-btn");

    if(button){

        button.addEventListener("click",function(){

            showNotification();

        });

    }

}

/*==================================================
                DASHBOARD SEARCH
==================================================*/

function initializeDashboardSearch(){

    const search=document.querySelector(".search-box input");

    if(!search){

        return;

    }

    search.addEventListener("keyup",function(){

        const value=this.value.toLowerCase();

        const rows=document.querySelectorAll("table tbody tr");

        rows.forEach(row=>{

            row.style.display=row.innerText.toLowerCase().includes(value)

            ? ""

            : "none";

        });

    });

}

/*==================================================
                SUMMARY COUNTER
==================================================*/

function animateCounter(element,target){

    let count=0;

    const speed=25;

    const timer=setInterval(function(){

        count++;

        element.innerText=count;

        if(count>=target){

            clearInterval(timer);

        }

    },speed);

}

function initializeCounters(){

    document.querySelectorAll(".summary-card h1").forEach(card=>{

        const target=parseInt(card.innerText);

        if(!isNaN(target)){

            card.innerText="0";

            animateCounter(card,target);

        }

    });

}

/*==================================================
                TABLE ROW HOVER
==================================================*/

function highlightTableRows(){

    const rows=document.querySelectorAll("tbody tr");

    rows.forEach(row=>{

        row.addEventListener("mouseenter",function(){

            this.style.background="#EFF6FF";

        });

        row.addEventListener("mouseleave",function(){

            this.style.background="";

        });

    });

}

/*==================================================
                INITIALIZE ALL
==================================================*/

document.addEventListener("DOMContentLoaded",function(){

    initializeDashboard();

    initializeDashboardSearch();

    initializeCounters();

    highlightTableRows();

});