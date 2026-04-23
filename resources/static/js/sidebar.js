document.addEventListener("DOMContentLoaded", async () => {
    criarNavbar();
});

function criarNavbar() {
    const navbarHTML = `
      <nav class="relative bg-gray-800/50 after:absolute after:inset-x-0 after:bottom-0 after:h-px after:bg-white/10">
        <div class="mx-auto max-w-7xl px-2 sm:px-6 lg:px-8">
            <div class="relative flex h-16 items-center justify-between">
                <div class="hidden sm:ml-6 sm:block">
                    <div class="flex space-x-4" id="nav-links-container">
                        <a href="/" class="nav-link rounded-md px-3 py-2 text-sm font-medium text-gray-300 hover:bg-gray-950/50 hover:text-white">Home</a>
                        <a href="/deposit" class="nav-link rounded-md px-3 py-2 text-sm font-medium text-gray-300 hover:bg-gray-950/50 hover:text-white">Message</a>
                        <a href="/open_vault" class="nav-link rounded-md px-3 py-2 text-sm font-medium text-gray-300 hover:bg-gray-950/50 hover:text-white">Open Cofre</a>
                    </div>
                </div>
                
                </div>
        </div>
      </nav>
    `;

    const container = document.querySelector('#navbar-container'); 
    if (container) {
        container.innerHTML = navbarHTML;
        marcarItemAtivo();
    }
}

function marcarItemAtivo() {
    const currentPath = window.location.pathname;
    const links = document.querySelectorAll('.nav-link');

    links.forEach(link => {
        // Se o href do link for igual ao path atual
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('bg-gray-950/50', 'text-white');
            link.classList.remove('text-gray-300');
        }
    });
}