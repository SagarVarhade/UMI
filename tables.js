/*==================================================
                UMI TABLES JS
==================================================*/

document.addEventListener("DOMContentLoaded",function(){

    initializeTables();

});

/*==================================================
                INITIALIZE
==================================================*/

function initializeTables(){

    initializeTableSearch();

    initializeRowHover();

    initializeStatusHighlight();

}

/*==================================================
                SEARCH
==================================================*/

function initializeTableSearch(){

    const search=document.querySelector(".search-box input");

    if(!search){

        return;

    }

    search.addEventListener("keyup",function(){

        const value=this.value.toLowerCase();

        const rows=document.querySelectorAll("tbody tr");

        rows.forEach(row=>{

            row.style.display=row.innerText.toLowerCase().includes(value)

            ? ""

            : "none";

        });

    });

}

/*==================================================
                ROW HOVER
==================================================*/

function initializeRowHover(){

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
            STATUS COLORS
==================================================*/

function initializeStatusHighlight(){

    document.querySelectorAll("tbody tr").forEach(row=>{

        row.querySelectorAll("td").forEach(cell=>{

            const text=cell.innerText.trim().toLowerCase();

            if(text==="completed"){

                cell.style.color="#16A34A";

                cell.style.fontWeight="600";

            }

            else if(text==="pending"){

                cell.style.color="#F59E0B";

                cell.style.fontWeight="600";

            }

            else if(text==="cancelled"){

                cell.style.color="#DC2626";

                cell.style.fontWeight="600";

            }

            else if(text==="low stock"){

                cell.style.color="#F59E0B";

                cell.style.fontWeight="600";

            }

            else if(text==="out of stock"){

                cell.style.color="#DC2626";

                cell.style.fontWeight="700";

            }

        });

    });

}
document.addEventListener("DOMContentLoaded",function(){

    initializeTables();

    initializeSorting();

    initializeSelectAll();

    initializeRowNumbers();

});