(function() {
    // Переменные для меню пользователя
    const toggle = document.getElementById('userMenuToggle');
    const userLi = document.querySelector('.nav-user');
    const redirectToSubscriptionButton = document.getElementById('redirectToSubscription');  // Кнопка перенаправления

    // Если toggle или userLi не найдены, завершаем выполнение
    if (!toggle || !userLi) return;

    // Открытие/закрытие меню пользователя при клике на кнопку
    toggle.addEventListener('click', function (e) {
        e.stopPropagation();  // Предотвращаем распространение события
        userLi.classList.toggle('open');  // Переключаем класс для открытия/закрытия меню
    });

    // Закрытие меню при клике на любую часть страницы (кроме самого меню)
    document.addEventListener('click', function () {
        userLi.classList.remove('open');  // Убираем класс открытия меню
    });

    // Чтобы клик внутри меню не закрывал его сразу
    const menu = userLi.querySelector('.user-menu');
    if (menu) {
        menu.addEventListener('click', function (e) {
            e.stopPropagation();  // Предотвращаем закрытие меню при клике внутри
        });
    }

    // Обработчик для кнопки "Копилка (требуется подписка)"
    // Добавим здесь логику, если кнопка "Копилка" требует подписки
    if (redirectToSubscriptionButton) {
        redirectToSubscriptionButton.addEventListener('click', function (e) {
            // Если пользователь не подписан, перенаправим его на страницу подписки
            window.location.href = '/stripe_test';  // Например, на страницу подписки
        });
    }

})();
