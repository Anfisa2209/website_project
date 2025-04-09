document.addEventListener('DOMContentLoaded', () => {
    const elements = document.querySelectorAll('.scheme-group');
    const menu_bar = document.querySelector('.menu-bar');

    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('force-visible');
                observer.unobserve(entry.target);

                document.getElementById('gear').style.width = '90px';
                document.getElementById('gear').style.height = '90px';

                document.getElementById('title').style = 'font-size:30px';
                if(menu_bar) {
                    menu_bar.style.opacity = '1';
                    menu_bar.style.visibility = 'visible';

                    menu_bar.style.animation = 'none';
                }

            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -100px 0px'
    });

    elements.forEach(el => observer.observe(el));
});