"use strict";

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; ++i) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function ajax(url, callback) {
    var csrftoken = getCookie('csrftoken');
    var xhr = new XMLHttpRequest();
    xhr.open('POST', url, true);
    xhr.setRequestHeader('X-CSRFToken', csrftoken);
    xhr.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            callback(JSON.parse(this.responseText));
        }
    };
    xhr.send();
}

function responseHandlerMaker(rating_elem, pushed_elem, other_elem) {
    return function (response) {
        if (response.status === 'ok'){
            rating_elem.innerHTML = response.rating.toString();
            pushed_elem.classList.toggle('on');
            other_elem.classList.remove('on');
        }
        else if (response.message) alert(response.message);
    }
}

function init_voting_for_questions() {
    var questions = document.querySelectorAll('.question');
    for (var i = 0; i < questions.length; ++i){
        var question = questions[i];
        var question_id = question.getAttribute('data-id');
        var vote_for_elem = question.querySelector('.vote-for');
        var vote_against_elem = question.querySelector('.vote-against');
        var rating_elem = question.querySelector('.rating');

        var responseHandler = responseHandlerMaker(rating_elem, vote_for_elem, vote_against_elem);
        vote_for_elem.question_id = question_id;
        vote_for_elem.onclick = function (responseHandler) {
            return function () {
                ajax('/vote-question/' + this.question_id.toString() + '/for', responseHandler);
            };
        }(responseHandler);

        responseHandler = responseHandlerMaker(rating_elem, vote_against_elem, vote_for_elem);
        vote_against_elem.question_id = question_id;
        vote_against_elem.onclick = function (responseHandler) {
            return function () {
                ajax('/vote-question/' + this.question_id.toString() + '/against', responseHandler);
            };
        }(responseHandler);
    }
}

function init_voting_for_answers() {
    var answers = document.querySelectorAll('.answer');
    for (var i = 0; i < answers.length; ++i){
        var answer = answers[i];
        var answer_id = answer.getAttribute('data-id');
        var vote_for_elem = answer.querySelector('.vote-for');
        var vote_against_elem = answer.querySelector('.vote-against');
        var rating_elem = answer.querySelector('.rating');

        var responseHandler = responseHandlerMaker(rating_elem, vote_for_elem, vote_against_elem);
        vote_for_elem.answer_id = answer_id;
        vote_for_elem.onclick = function (responseHandler) {
            return function () {
                ajax('/vote-answer/' + this.answer_id.toString() + '/for', responseHandler);
            };
        }(responseHandler);

        responseHandler = responseHandlerMaker(rating_elem, vote_against_elem, vote_for_elem);
        vote_against_elem.answer_id = answer_id;
        vote_against_elem.onclick = function (responseHandler) {
            return function () {
                ajax('/vote-answer/' + this.answer_id.toString() + '/against', responseHandler);
            };
        }(responseHandler);
    }
}

function init_marking_answers() {
    function responseHandlerMaker(status_elem) {
        return function(response) {
            if (response.status === 'ok') {
                var all = document.querySelectorAll('.answer .status');
                for (var j = 0; j < all.length; ++j) {
                    all[j].classList.remove('correct');
                }
                status_elem.classList.add('correct');
            }
        };
    }
    var answers = document.querySelectorAll('.answer');
    for (var i = 0; i < answers.length; ++i){
        var answer = answers[i];
        var answer_id = answer.getAttribute('data-id');
        var status_elem = answer.querySelector('.status');

        status_elem.answer_id = answer_id;
        status_elem.onclick = function () {
            ajax('/mark-answer/' + this.answer_id.toString(), responseHandlerMaker(this));
        };
    }
}

function init(){
    init_voting_for_questions();
    init_voting_for_answers();
    init_marking_answers();
}

window.onload = init;
