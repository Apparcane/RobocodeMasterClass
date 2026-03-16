// Состояние (Engine State)
let hunger = 100;
let happy = 100;
let alive = true;

// Функция обновления цифр (вызывается движком)
function updateStatsUI() {
    const h = document.getElementById("hunger");
    const s = document.getElementById("happy");
    if (h) h.textContent = Math.floor(hunger);
    if (s) s.textContent = Math.floor(happy);
}

// Система жизни (тикает сама)
setInterval(() => {
    if (!alive) return;
    hunger -= 1;
    happy -= 0.5;
    if (hunger <= 0) { alive = false; alert("Пет помер..."); }
    updateStatsUI();
}, 2000);

// ФУНКЦИИ ДЛЯ ВЫЗОВА В MAIN.JS

function core_feed(amount) {
    if (!alive) return;
    hunger = Math.min(100, hunger + amount);
    updateStatsUI();
}

function core_moveEye(side, x, y) {
    const eye = document.getElementById(side === 'left' ? "eyeL" : "eyeR");
    if (eye) eye.style.transform = `translate(${x}px, ${y}px)`;
}

function core_play() {
    if (!alive || hunger < 20) return;
    if(hunger < 10) {
        alert("Пет занадто голодний для гри!");
        return;
    }

    let game = document.getElementById("game");
    game.style.display = "block";
    game.innerHTML = "<h2 style='color:white; text-align:center; margin-top:20px;'>Збирай їжу!</h2>";

    let spawn = setInterval(() => {
        let food = document.createElement("div");
        let foodImg = document.createElement('img');

        // Картинка їжі в грі
        foodImg.src = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQEjE1irFZlrhJcINIhP7Yc_xDYpX3NlIyKLw&s";
        foodImg.style.width = "50px";
        food.appendChild(foodImg);

        food.className = "food";
        food.style.left = Math.random() * (window.innerWidth - 60) + "px";
        food.style.top = Math.random() * (window.innerHeight - 60) + "px";

        food.onclick = () => {
            // Кліки в міні-грі підвищують і голод, і щастя
            hunger = Math.min(100, hunger - 2);
            happy = Math.min(100, happy + 4);

            // Анімація радості пета при кожному кліку по їжі
            let petContainer = document.getElementById("pet");
            petContainer.classList.add("happy");
            setTimeout(() => petContainer.classList.remove("happy"), 300);

            food.remove();
        };

        game.appendChild(food);
    }, 600);

    setTimeout(() => {
        clearInterval(spawn);
        game.style.display = "none";

        // Пет втомлюється після біганини
        hunger = Math.max(0, hunger - 5);
        updateStats();
    }, 10000);
    console.log("Игра запущена через Engine");
}

// 3. Настройка глаз (связываем слайдеры с ядром)
function handleEyeMove() {
    const lx = document.getElementById("eyeLX").value;
    const ly = document.getElementById("eyeLY").value;
    const rx = document.getElementById("eyeRX").value;
    const ry = document.getElementById("eyeRY").value;

    core_moveEye('left', lx, ly);
    core_moveEye('right', rx, ry);
}

document.addEventListener("mousemove", (e) => {
    if (!alive) return;
    let pupils = document.querySelectorAll(".pupil");
    pupils.forEach(pupil => {
        let rect = pupil.getBoundingClientRect();
        let x = e.clientX - rect.left - rect.width / 2;
        let y = e.clientY - rect.top - rect.height / 2;
        let angle = Math.atan2(y, x);
        let moveX = Math.cos(angle) * 8;
        let moveY = Math.sin(angle) * 8;
        pupil.style.transform = `translate(${moveX}px,${moveY}px)`;
    });
});
