// ======================================
// STAR RATING
// ======================================

const stars = document.querySelectorAll(".star");

const ratingText = document.getElementById("rating-text");

const selectedRating =
    document.getElementById("selected-rating");


stars.forEach(function(star) {

    star.addEventListener("click", function() {

        const rating =
            Number(this.getAttribute("data-rating"));


        // Store selected rating

        selectedRating.value = rating;


        // Highlight stars

        stars.forEach(function(currentStar) {

            const starRating =
                Number(currentStar.getAttribute("data-rating"));


            if (starRating <= rating) {

                currentStar.classList.add("selected");

            } else {

                currentStar.classList.remove("selected");

            }

        });


        // Display rating message

        if (rating === 1) {

            ratingText.textContent = "Poor 😞";

        }

        else if (rating === 2) {

            ratingText.textContent = "Average 😐";

        }

        else if (rating === 3) {

            ratingText.textContent = "Good 🙂";

        }

        else if (rating === 4) {

            ratingText.textContent = "Very Good 😊";

        }

        else {

            ratingText.textContent = "Excellent! 😍";

        }

    });

});



// ======================================
// CHARACTER COUNTER
// ======================================

const feedbackBox =
    document.getElementById("feedback");

const charCount =
    document.getElementById("charCount");


feedbackBox.addEventListener("input", function() {

    charCount.textContent = this.value.length;

});



// ======================================
// FORM VALIDATION
// ======================================

const feedbackForm =
    document.getElementById("feedbackForm");


feedbackForm.addEventListener("submit", function(event) {

    if (selectedRating.value === "") {

        event.preventDefault();

        alert("Please select a rating before submitting.");

        return;

    }

});