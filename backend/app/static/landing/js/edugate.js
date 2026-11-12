/**
 * EDUGATE Main Frontend Ecosystem Controller
 * Manages language selection, tabs, modal previews, animations, and counters.
 */

class EdugateApp {
    constructor() {
        this.currentLang = localStorage.getItem('edugate_lang') || 'uz';
        this.init();
    }

    init() {
        this.initNavbar();
        this.initLanguageSelector();
        this.initModalViewer();
        this.initTabSwitcher();
    }

    initNavbar() {
        const header = document.querySelector('.site-header');
        window.addEventListener('scroll', () => {
            if (window.scrollY > 30) {
                header?.classList.add('shadow-2xl', 'border-cyan-500/20', 'bg-slate-950/95');
            } else {
                header?.classList.remove('shadow-2xl', 'border-cyan-500/20', 'bg-slate-950/95');
            }
        });

        // Scrollspy for active nav-link underline
        const navLinks = document.querySelectorAll('nav .nav-link');
        const sections = Array.from(navLinks)
            .map(link => {
                const id = link.getAttribute('href')?.replace('#', '');
                return id ? document.getElementById(id) : null;
            })
            .filter(Boolean);

        const updateActiveLink = () => {
            const scrollPos = window.scrollY + 140;
            let currentId = '';

            for (let i = sections.length - 1; i >= 0; i--) {
                const sec = sections[i];
                if (sec && scrollPos >= sec.offsetTop) {
                    currentId = sec.getAttribute('id');
                    break;
                }
            }

            if (!currentId && sections.length > 0) {
                currentId = sections[0].getAttribute('id');
            }

            navLinks.forEach(link => {
                const href = link.getAttribute('href');
                if (href === '#' + currentId) {
                    link.classList.add('active');
                } else {
                    link.classList.remove('active');
                }
            });
        };

        // On click, immediately set active
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                navLinks.forEach(l => l.classList.remove('active'));
                link.classList.add('active');
            });
        });

        window.addEventListener('scroll', updateActiveLink, { passive: true });
        updateActiveLink();

        // Mobile menu toggle
        const toggleBtn = document.getElementById('mobileMenuToggle');
        const mobileNav = document.getElementById('mobileNavDrawer');
        if (toggleBtn && mobileNav) {
            toggleBtn.addEventListener('click', () => {
                mobileNav.classList.toggle('hidden');
            });
            mobileNav.querySelectorAll('a').forEach(a => {
                a.addEventListener('click', () => mobileNav.classList.add('hidden'));
            });
        }
    }

    initLanguageSelector() {
        const langBtns = document.querySelectorAll('[data-lang-btn]');
        langBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const lang = e.currentTarget.getAttribute('data-lang-btn');
                this.switchLanguage(lang);
            });
        });
        this.applyLanguage(this.currentLang);
    }

    switchLanguage(lang) {
        if (!EdugateI18N[lang]) return;
        this.currentLang = lang;
        localStorage.setItem('edugate_lang', lang);
        this.applyLanguage(lang);
    }

    applyLanguage(lang) {
        const dict = EdugateI18N[lang] || EdugateI18N['uz'];
        document.querySelectorAll('[data-i18n]').forEach(el => {
            const keyPath = el.getAttribute('data-i18n').split('.');
            let val = dict;
            for (let k of keyPath) {
                if (val && val[k] !== undefined) {
                    val = val[k];
                } else {
                    val = null;
                    break;
                }
            }
            if (val) el.textContent = val;
        });

        document.querySelectorAll('[data-lang-btn]').forEach(b => {
            if (b.getAttribute('data-lang-btn') === lang) {
                b.classList.add('bg-cyan-500/30', 'text-cyan-300', 'font-bold');
            } else {
                b.classList.remove('bg-cyan-500/30', 'text-cyan-300', 'font-bold');
            }
        });
    }

    initModalViewer() {
        const modal = document.getElementById('highResModal');
        const modalImg = document.getElementById('highResModalImg');
        const modalTitle = document.getElementById('highResModalTitle');
        const closeBtn = document.getElementById('closeModalBtn');

        document.querySelectorAll('[data-preview-img]').forEach(trigger => {
            trigger.addEventListener('click', (e) => {
                const src = e.currentTarget.getAttribute('data-preview-img');
                const title = e.currentTarget.getAttribute('data-preview-title') || 'EDUGATE Retina Display';
                if (modal && modalImg) {
                    modalImg.src = src;
                    if (modalTitle) modalTitle.textContent = title;
                    modal.classList.add('open');
                }
            });
        });

        const closeModal = () => modal?.classList.remove('open');
        closeBtn?.addEventListener('click', closeModal);
        modal?.addEventListener('click', (e) => {
            if (e.target === modal) closeModal();
        });
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') closeModal();
        });
    }

    initTabSwitcher() {
        const tabBtns = document.querySelectorAll('[data-platform-tab]');
        const tabContents = document.querySelectorAll('[data-platform-content]');

        tabBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const target = e.currentTarget.getAttribute('data-platform-tab');
                tabBtns.forEach(b => {
                    b.classList.remove('bg-cyan-600', 'text-white', 'shadow-lg');
                    b.classList.add('bg-slate-800/80', 'text-slate-300');
                });
                e.currentTarget.classList.add('bg-cyan-600', 'text-white', 'shadow-lg');
                e.currentTarget.classList.remove('bg-slate-800/80', 'text-slate-300');

                tabContents.forEach(c => {
                    if (c.getAttribute('data-platform-content') === target) {
                        c.classList.remove('hidden');
                    } else {
                        c.classList.add('hidden');
                    }
                });
            });
        });
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.edugateApp = new EdugateApp();
});

