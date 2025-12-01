(function() {
    const toggle = document.getElementById('userMenuToggle');
    const userLi = document.querySelector('.nav-user');

    if (!toggle || !userLi) return;

    // открытие/закрытие по клику
    toggle.addEventListener('click', function (e) {
      e.stopPropagation();
      userLi.classList.toggle('open');
    });

    // клик вне меню — закрыть
    document.addEventListener('click', function () {
      userLi.classList.remove('open');
    });

    // чтобы клик внутри меню не закрывал сразу
    const menu = userLi.querySelector('.user-menu');
    if (menu) {
        menu.addEventListener('click', function (e) {
            e.stopPropagation();
        });
    }
  })();