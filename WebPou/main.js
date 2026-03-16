// 1. Настройка кормления
function feed() {
    // Вызываем функцию из ядра и говорим, на сколько покормить
    core_feed(25); 
}

// 2. Настройка игры
function startGame() {
    core_play();
}

// Вешаем события
document.querySelectorAll('input').forEach(input => {
    input.oninput = handleEyeMove;
});