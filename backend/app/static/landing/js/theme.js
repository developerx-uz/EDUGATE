/**
 * EDUGATE Dynamic Dual Theme Manager (Light / Dark / Auto-System)
 * Standard default: Automatic OS System Detection.
 * User can toggle Light <-> Dark at any time, persisted in localStorage.
 */

(function() {
    const THEME_KEY = 'edugate_theme_preference';

    // Get current effective theme
    function getSystemTheme() {
        return window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark';
    }

    function getSavedTheme() {
        return localStorage.getItem(THEME_KEY); // 'light', 'dark', or null (system auto)
    }

    function applyTheme(theme) {
        const root = document.documentElement;
        const effectiveTheme = (theme === 'light' || theme === 'dark') ? theme : getSystemTheme();

        if (effectiveTheme === 'light') {
            root.classList.add('light');
            root.classList.remove('dark');
            root.setAttribute('data-theme', 'light');
        } else {
            root.classList.add('dark');
            root.classList.remove('light');
            root.setAttribute('data-theme', 'dark');
        }

        updateThemeToggleIcons(effectiveTheme, theme);
    }

    function updateThemeToggleIcons(effectiveTheme, userPref) {
        const toggleBtns = document.querySelectorAll('[data-theme-toggle]');
        toggleBtns.forEach(btn => {
            const icon = btn.querySelector('i');
            const label = btn.querySelector('.theme-label');

            if (effectiveTheme === 'light') {
                if (icon) {
                    icon.className = 'fas fa-moon text-amber-500';
                }
                if (label) {
                    label.textContent = "Qorong'i";
                }
                btn.title = "Qorong'i rejimga o'tish";
            } else {
                if (icon) {
                    icon.className = 'fas fa-sun text-amber-400';
                }
                if (label) {
                    label.textContent = "Yorug'";
                }
                btn.title = "Yorug' rejimga o'tish";
            }
        });
    }

    // Toggle theme manually
    window.toggleEdugateTheme = function() {
        const currentSaved = getSavedTheme();
        const effectiveCurrent = document.documentElement.classList.contains('light') ? 'light' : 'dark';
        const nextTheme = effectiveCurrent === 'light' ? 'dark' : 'light';

        localStorage.setItem(THEME_KEY, nextTheme);
        applyTheme(nextTheme);
    };

    // Reset to system auto
    window.resetEdugateThemeToSystem = function() {
        localStorage.removeItem(THEME_KEY);
        applyTheme('system');
    };

    // Initial run before DOMContentLoaded to prevent flash of wrong theme
    const initialPreference = getSavedTheme();
    applyTheme(initialPreference);

    // Watch OS system preference changes
    if (window.matchMedia) {
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
            if (!getSavedTheme()) {
                applyTheme('system');
            }
        });
    }

    // Bind click events on DOMContentLoaded
    document.addEventListener('DOMContentLoaded', () => {
        const toggleBtns = document.querySelectorAll('[data-theme-toggle]');
        toggleBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                window.toggleEdugateTheme();
            });
        });

        // Ensure icons are correctly in sync with DOM
        applyTheme(getSavedTheme());
    });
})();

