document.addEventListener('DOMContentLoaded', () => {
    // Скрытие header при скролле
    let lastScrollY = window.scrollY;
    const header = document.getElementById('header');
    
    window.addEventListener('scroll', () => {
        if (window.scrollY > lastScrollY && window.scrollY > 100) {
            header.classList.add('hidden');
        } else {
            header.classList.remove('hidden');
        }
        
        lastScrollY = window.scrollY;
    });

    window.addEventListener('resize', () => {
        if (window.innerWidth > 992){
            bodyTeg.classList.remove('non-scroll')
        }
    });

    burgerButton = document.querySelector('.burger-menu')
    sidebar = document.querySelector('.sidebar')
    burgerButton.addEventListener('click', () => {
        sidebar.classList.toggle('active')
        burgerButton.classList.toggle('active')
        bodyTeg.classList.toggle('non-scroll')
    })
})
