const about = document.getElementById('about');
document.getElementById('about-button').addEventListener('click', () => about.showModal());
document.getElementById('close-about').addEventListener('click', () => about.close());
about.addEventListener('click', event => { if (event.target === about) about.close(); });
