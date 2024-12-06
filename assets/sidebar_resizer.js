// sidebar_resizer.js

document.addEventListener('DOMContentLoaded', function() {
    const sidebarContainer = document.getElementById('sidebar-container');
    const resizer = document.getElementById('resizer');
    const mainContent = document.querySelector('.main-content');
    let isResizing = false;

    resizer.addEventListener('mousedown', initResize, false);

    function initResize(e) {
        isResizing = true;
        document.addEventListener('mousemove', resize, false);
        document.addEventListener('mouseup', stopResize, false);
    }

    function resize(e) {
        if (isResizing) {
            const newWidth = e.clientX - sidebarContainer.offsetLeft;
            if (newWidth > 300 && newWidth < window.innerWidth * 0.5) {
                sidebarContainer.style.width = newWidth + 'px';
            }
        }
    }

    function stopResize(e) {
        isResizing = false;
        document.removeEventListener('mousemove', resize, false);
        document.removeEventListener('mouseup', stopResize, false);
    }
});