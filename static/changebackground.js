const wintermodusBtn = document.getElementById('wintermodus_starten');
const endwintermodusBtn = document.getElementById('wintermodus_beenden');
const body = document.body;

// Hintergrundbilder
const backgrounds = [
    'url("/static/winter-hike1.jpg")',
    'url("/static/winter-hike2.jpg")',
    'url("/static/winter-hike3.jpg")',
    'url("/static/winter-hike4.jpg")',
    'url("/static/winter-hike5.jpg")',
    'url("/static/winter-hike6.jpg")',
    'url("/static/winter-hike7.jpg")',
    'url("/static/winter-hike8.jpg")',
    'url("/static/winter-hike9.jpg")',
    'url("/static/winter-hike10.jpg")',
    'url("/static/winter-hike11.jpg")',
    'url("/static/winter-hike12.jpg")',
    'url("/static/winter-hike13.jpg")',
];

let currentBackgroundIndex = 0;
let intervalId; // Variable zur Speicherung der Intervall-ID

function startAutomaticChange() {
    // Setze das aktuelle Bild als Hintergrund ohne Übergang
    body.style.transition = 'none';
    body.style.backgroundImage = backgrounds[currentBackgroundIndex];

    // Starte dann das Intervall 
    intervalId = setInterval(function () {
        currentBackgroundIndex = (currentBackgroundIndex + 1) % backgrounds.length;
        body.style.transition = 'background-image 1s ease-in-out';
        body.style.backgroundImage = backgrounds[currentBackgroundIndex];
    }, 5000); // 5 Sekunden Intervall
}

function stopAutomaticChange() {
    // Stoppe das Intervall und setze counter auf 0
    clearInterval(intervalId);
    body.style.transition = 'background-image 1s ease-in-out';
    const background = 'url("/static/optionindex.jpg")';
    body.style.backgroundImage = background;
    currentBackgroundIndex = 0;
}

wintermodusBtn.addEventListener('click', function () {
    startAutomaticChange();
});

endwintermodusBtn.addEventListener('click', function () {
    stopAutomaticChange();
});