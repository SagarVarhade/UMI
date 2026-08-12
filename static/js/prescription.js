/*==================================================
            UMI PRESCRIPTION JS
==================================================*/

document.addEventListener("DOMContentLoaded",function(){

    setCurrentDate();

    setCurrentTime();

    calculateBMI();

    initializeTemplate();

});

/*==================================================
            CURRENT DATE
==================================================*/

function setCurrentDate(){

    const date=document.querySelector("input[type='date']");

    if(!date)return;

    date.value=new Date().toISOString().split("T")[0];

}

/*==================================================
            CURRENT TIME
==================================================*/

function setCurrentTime(){

    const time=document.querySelector("input[type='time']");

    if(!time)return;

    const now=new Date();

    time.value=now.toTimeString().slice(0,5);

}

/*==================================================
            BMI
==================================================*/

function calculateBMI(){

    const inputs=document.querySelectorAll("input[type='number']");

    if(inputs.length<2)return;

    const height=inputs[0];

    const weight=inputs[1];

    function update(){

        const h=parseFloat(height.value)/100;

        const w=parseFloat(weight.value);

        if(h>0 && w>0){

            const bmi=(w/(h*h)).toFixed(1);

            console.log("BMI:",bmi);

        }

    }

    height.addEventListener("input",update);

    weight.addEventListener("input",update);

}

/*==================================================
        TEMPLATE LOADER
==================================================*/

function loadTemplate(){

    alert("Template Loaded");

}

/*==================================================
            ADD MEDICINE
==================================================*/

function addMedicine(button){

    const currentCard = button.closest(".medicine-card");

    const clone = currentCard.cloneNode(true);

    // Clear inputs
    clone.querySelectorAll("input").forEach(input=>{

        if(!input.readOnly){

            input.value="";

        }

    });

    // Clear textareas
    clone.querySelectorAll("textarea").forEach(area=>{

        area.value="";

    });

    // Reset selects
    clone.querySelectorAll("select").forEach(select=>{

        select.selectedIndex=0;

    });

    // Insert after current card
    currentCard.after(clone);

    updateMedicineNumbers();

}
/*==================================================
            REMOVE MEDICINE
==================================================*/

/*==================================================
            REMOVE LAST MEDICINE
==================================================*/

/*==================================================
            REMOVE LAST MEDICINE
==================================================*/
function removeMedicine(button){

    const cards=document.querySelectorAll(".medicine-card");

    if(cards.length===1){

        alert("At least one medicine is required.");

        return;

    }

    const card=button.closest(".medicine-card");

    card.remove();

    updateMedicineNumbers();

}
function updateMedicineNumbers(){

    document.querySelectorAll(".medicine-card").forEach((card,index)=>{

        card.querySelector("h3").textContent="Medicine "+(index+1);

    });

}


/*==================================================
            SAVE DRAFT
==================================================*/

function saveDraft(){

    alert("Prescription Draft Saved.");

}

/*==================================================
            SAVE PRESCRIPTION
==================================================*/

function savePrescription(){

    alert("Prescription Saved Successfully.");

}

/*==================================================
            PRINT
==================================================*/

function printPrescription(){

    window.print();

}

/*==================================================
            FOLLOW UP
==================================================*/

function initializeFollowup(){

    const number=document.querySelector(".followup-group input");

    const unit=document.querySelector(".followup-group select");

    const date=document.querySelector("input[type='date']");

    if(!number || !unit || !date){

        return;

    }

    number.addEventListener("change",calculateFollowup);

    unit.addEventListener("change",calculateFollowup);

}

function calculateFollowup(){

    console.log("Follow-up Updated");

}

/*==================================================
            PATIENT HISTORY
==================================================*/

function openPatientHistory(){

    openModal("patientHistoryModal");

}

function closePatientHistory(){

    closeModal("patientHistoryModal");

}

/*==================================================
            VALIDATION
==================================================*/

function validatePrescription(){

    const complaint=document.querySelector("input[list='complaints']");

    if(complaint && complaint.value.trim()==""){

        alert("Please enter Chief Complaint.");

        complaint.focus();

        return false;

    }

    return true;

}

/*==================================================
            INITIALIZE
==================================================*/

document.addEventListener("DOMContentLoaded",function(){

    initializeFollowup();

});
