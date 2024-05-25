function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const init = () => {
    const base_url = window.location.origin;
    const question_cards = document.querySelectorAll(".question-card")
    const answer_cards = document.querySelectorAll(".answer-card")
    for (const card of question_cards) {
        const likeButton = card.querySelector(".card-like")
        const dislikeButton = card.querySelector(".card-dislike")
        const ratingCounter = card.querySelector(".card-counter")
        const questionId = card.dataset.questionId
        likeButton.addEventListener("click", () => {
            if (likeButton.classList.contains("border-dark")) {
                likeButton.classList.remove("border-dark")
            }
            else {
                likeButton.classList.add("border-dark")
                dislikeButton.classList.remove("border-dark")
            }
            const request = new Request(base_url + `/question/${questionId}/like`, {
                method: "post",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken"),
                },
                body: JSON.stringify({
                })
            })
            fetch(request)
            .then((response) => response.json())
            .then((data) => ratingCounter.value = data.rating)
        })
        dislikeButton.addEventListener("click", () => {
            if (dislikeButton.classList.contains("border-dark")) {
                dislikeButton.classList.remove("border-dark")
            }
            else {
                dislikeButton.classList.add("border-dark")
                likeButton.classList.remove("border-dark")
            }
            const request = new Request(base_url + `/question/${questionId}/dislike`, {
                method: "post",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken"),
                },
                body: JSON.stringify({
                })
            })
            fetch(request)
            .then((response) => response.json())
            .then((data) => ratingCounter.value = data.rating)
        })
    }

    for (const card of answer_cards) {
        const likeButton = card.querySelector(".card-like")
        const dislikeButton = card.querySelector(".card-dislike")
        const ratingCounter = card.querySelector(".card-counter")
        const answerId = card.dataset.answerId
        const checkbox = card.querySelector(".form-check-input")
        likeButton.addEventListener("click", () => {
            if (likeButton.classList.contains("border-dark")) {
                likeButton.classList.remove("border-dark")
            }
            else {
                likeButton.classList.add("border-dark")
                dislikeButton.classList.remove("border-dark")
            }
            const request = new Request(base_url + `/answer/${answerId}/like`, {
                method: "post",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken"),
                },
                body: JSON.stringify({
                })
            })
            fetch(request)
            .then((response) => response.json())
            .then((data) => ratingCounter.value = data.rating)
        })
        dislikeButton.addEventListener("click", () => {
            if (dislikeButton.classList.contains("border-dark")) {
                dislikeButton.classList.remove("border-dark")
            }
            else {
                dislikeButton.classList.add("border-dark")
                likeButton.classList.remove("border-dark")
            }
            const request = new Request(base_url + `/answer/${answerId}/dislike`, {
                method: "post",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken"),
                },
                body: JSON.stringify({
                })
            })
            fetch(request)
            .then((response) => response.json())
            .then((data) => ratingCounter.value = data.rating)
        })
        checkbox.addEventListener("change", () => {
            const is_correct = checkbox.checked
            const questionId = card.dataset.questionId
            const request = new Request(base_url + `/answer/${answerId}/is_correct`, {
                method: "post",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken"),
                },
                body: JSON.stringify({
                    questionId,
                    is_correct,
                })
            })
            fetch(request)
            .then((response) => response.json())
            .then((data) => {
                for (const card_tmp of answer_cards) {
                    const checkbox_tmp = card_tmp.querySelector(".form-check-input")
                    checkbox_tmp.checked = false
                }
                checkbox.checked = data.is_correct
            })
        })
    }
}
init()