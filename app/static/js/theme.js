(() => {
    const html = document.documentElement;
    const button = document.getElementById('themeToggle');
    const savedTheme = localStorage.getItem('mindcare-theme') || 'light';

    html.setAttribute('data-bs-theme', savedTheme);

    if (button) {
        button.addEventListener('click', () => {
            const current = html.getAttribute('data-bs-theme') || 'light';
            const next = current === 'dark' ? 'light' : 'dark';
            html.setAttribute('data-bs-theme', next);
            localStorage.setItem('mindcare-theme', next);
        });
    }
})();
