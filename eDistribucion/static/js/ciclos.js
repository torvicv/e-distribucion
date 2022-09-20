document.addEventListener('DOMContentLoaded', iniciar);

function iniciar() {
    var h3 = document.querySelectorAll('.ciclos-h3 span');
    for (let i = 0; i < h3.length; i++) {
        h3[i].addEventListener('click', function() {
            let cycles = document.getElementsByClassName('cycles');
            Array.from(cycles).map(function(element) {
                element.classList.add('d-none');
                element.classList.remove('d-flex');
            });
            this.parentElement.parentElement.nextElementSibling.classList.remove('d-none');
            this.parentElement.parentElement.nextElementSibling.classList.add('d-flex');
        });
    }
}