document.addEventListener("DOMContentLoaded", function () {

    const questions = document.querySelectorAll(".faq-question");

    questions.forEach(function(question){

        question.addEventListener("click", function(){

            const item = this.parentElement;
            const answer = item.querySelector(".faq-answer");
            const icon = item.querySelector(".faq-icon");

            if(answer.style.maxHeight){

                answer.style.maxHeight = null;
                icon.textContent = "+";
                item.classList.remove("active");

            }else{

                answer.style.maxHeight = answer.scrollHeight + "px";
                icon.textContent = "−";
                item.classList.add("active");

            }

        });

    });

});
