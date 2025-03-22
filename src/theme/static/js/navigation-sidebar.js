document.addEventListener('DOMContentLoaded', function(){
    let navigation_sidebar = document.getElementById('navigation-sidebar')
    let main_body = document.getElementById('body')
    let hide_navigation_bar_button = document.getElementById('hide-navigation-bar-button')
    let show_navigation_bar_button = document.getElementById('show-navigation-bar-button')

    hide_navigation_bar_button.addEventListener('click', function(){
        navigation_sidebar.style.display = 'none';
        main_body.classList.remove('lg:w-5/6');
        show_navigation_bar_button.style.display = 'block';
    })

    show_navigation_bar_button.addEventListener('click', function(){
        navigation_sidebar.style.display = 'flex';
        main_body.classList.add('lg:w-5/6');
        show_navigation_bar_button.style.display = 'none';
    })
})