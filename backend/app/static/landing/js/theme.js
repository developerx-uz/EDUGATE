/**
 * EDUGATE Dynamic Dual Theme Manager (Light / Dark / Auto-System)
 * Supports segmented pill controls [ ☀️ | 🌙 ] and single toggle buttons.
 * Icon-only presentation: strictly no text labels.
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

        // Dispatch custom event for dynamic components (like SVG Map) to update their palettes
        try {
            window.dispatchEvent(new CustomEvent('edugate-theme-changed', { detail: { theme: effectiveTheme } }));
        } catch (e) {}
    }

    function updateThemeToggleIcons(effectiveTheme, userPref) {
        // 1. Dual Segmented Pill Buttons [ ☀️ | 🌙 ]
        document.querySelectorAll('.theme-btn-light, [data-theme-set="light"]').forEach(btn => {
            if (effectiveTheme === 'light') {
                btn.classList.add('active', 'bg-amber-500/20', 'text-amber-400', 'border', 'border-amber-500/40');
                btn.classList.remove('text-slate-400');
            } else {
                btn.classList.remove('active', 'bg-amber-500/20', 'text-amber-400', 'border', 'border-amber-500/40');
                btn.classList.add('text-slate-400');
            }
        });

        document.querySelectorAll('.theme-btn-dark, [data-theme-set="dark"]').forEach(btn => {
            if (effectiveTheme === 'dark') {
                btn.classList.add('active', 'bg-cyan-500/20', 'text-cyan-300', 'border', 'border-cyan-500/40');
                btn.classList.remove('text-slate-400');
            } else {
                btn.classList.remove('active', 'bg-cyan-500/20', 'text-cyan-300', 'border', 'border-cyan-500/40');
                btn.classList.add('text-slate-400');
            }
        });

        // 2. Legacy / Single Toggle Buttons (Strictly Icon Only)
        document.querySelectorAll('[data-theme-toggle]').forEach(btn => {
            const icon = btn.querySelector('i');
            const label = btn.querySelector('.theme-label');
            if (label) {
                label.remove(); // Enforce removal of text labels
            }

            if (effectiveTheme === 'light') {
                if (icon) icon.className = 'fas fa-moon text-amber-500 text-sm';
                btn.title = "Qorong'i rejimga o'tish";
            } else {
                if (icon) icon.className = 'fas fa-sun text-amber-400 text-sm';
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

    window.setEdugateTheme = function(mode) {
        if (mode !== 'light' && mode !== 'dark') return;
        localStorage.setItem(THEME_KEY, mode);
        applyTheme(mode);
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
        // Segmented pill buttons [data-theme-set="light"] and [data-theme-set="dark"]
        document.querySelectorAll('[data-theme-set]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const mode = btn.getAttribute('data-theme-set');
                window.setEdugateTheme(mode);
            });
        });

        // Single toggle buttons [data-theme-toggle]
        document.querySelectorAll('[data-theme-toggle]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                window.toggleEdugateTheme();
            });
        });

        // Synchronize DOM elements after render
        applyTheme(getSavedTheme());
    });
})();
