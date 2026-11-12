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
        this.initPhotoGallery();
        this.initTabSwitcher();
        this.initHardwareTabs();
        this.initContactForm();
    }

    initNavbar() {
        const header = document.querySelector('.site-header');
        window.addEventListener('scroll', () => {
            if (window.scrollY > 30) {
                header?.classList.add('shadow-2xl', 'bg-slate-950/98');
            } else {
                header?.classList.remove('shadow-2xl', 'bg-slate-950/98');
            }
        }, { passive: true });

        // Sliding Navigation Indicator & Precision Scrollspy
        const nav = document.querySelector('.nav-container');
        if (!nav) return;

        const navLinks = Array.from(nav.querySelectorAll('.nav-link'));
        const line = document.getElementById('navActiveLine');

        const moveLineTo = (el) => {
            if (!el || !line) return;
            const navRect = nav.getBoundingClientRect();
            const elRect = el.getBoundingClientRect();
            line.style.left = `${elRect.left - navRect.left}px`;
            line.style.width = `${elRect.width}px`;
            line.style.opacity = '1';
        };

        const getActiveLink = () => {
            return nav.querySelector('.nav-link.active') || navLinks[0];
        };

        const scrollToSection = (targetId) => {
            const target = document.getElementById(targetId);
            if (!target) return;
            const header = document.querySelector('.site-header');
            const headerHeight = header ? header.offsetHeight : 54;
            const targetTop = target.getBoundingClientRect().top + window.pageYOffset - headerHeight;
            window.scrollTo({
                top: Math.max(0, Math.round(targetTop)),
                behavior: 'smooth'
            });
        };

        // Smooth Hover & Precision Click Scroll
        navLinks.forEach(link => {
            link.addEventListener('mouseenter', () => moveLineTo(link));
            link.addEventListener('click', (e) => {
                const href = link.getAttribute('href');
                if (href && href.startsWith('#')) {
                    const id = href.substring(1);
                    if (id) {
                        e.preventDefault();
                        scrollToSection(id);
                        if (history.pushState) {
                            history.pushState(null, '', href);
                        }
                    }
                }
                navLinks.forEach(l => l.classList.remove('active'));
                link.classList.add('active');
                moveLineTo(link);
                isManualClick = true;
                setTimeout(() => { isManualClick = false; }, 900);
            });
        });

        nav.addEventListener('mouseleave', () => {
            moveLineTo(getActiveLink());
        });

        // High-Precision Viewport Tracking for Sections
        const sectionMap = navLinks.map(link => {
            const id = link.getAttribute('href')?.replace('#', '');
            const el = id ? document.getElementById(id) : null;
            return { link, el, id };
        }).filter(item => item.el !== null);

        let isManualClick = false;

        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                isManualClick = true;
                setTimeout(() => { isManualClick = false; }, 800);
            });
        });

        const updateActiveOnScroll = () => {
            if (isManualClick) return;

            // If at the very top of page
            if (window.scrollY < 120 && navLinks[0]) {
                navLinks.forEach(l => l.classList.remove('active'));
                navLinks[0].classList.add('active');
                moveLineTo(navLinks[0]);
                return;
            }

            // Find current section using getBoundingClientRect
            let currentItem = null;
            const threshold = 180; // 180px from viewport top

            for (let i = 0; i < sectionMap.length; i++) {
                const item = sectionMap[i];
                const rect = item.el.getBoundingClientRect();
                if (rect.top <= threshold && rect.bottom > threshold) {
                    currentItem = item;
                    break;
                }
            }

            // If reached the bottom of page, activate last item
            if ((window.innerHeight + window.scrollY) >= (document.documentElement.scrollHeight - 80)) {
                currentItem = sectionMap[sectionMap.length - 1];
            }

            if (currentItem) {
                navLinks.forEach(l => l.classList.remove('active'));
                currentItem.link.classList.add('active');
                moveLineTo(currentItem.link);
            }
        };

        // Sync with URL Hash on Page Load or Refresh
        const syncFromHash = () => {
            const hash = window.location.hash;
            if (hash) {
                const match = navLinks.find(l => l.getAttribute('href') === hash);
                if (match) {
                    navLinks.forEach(l => l.classList.remove('active'));
                    match.classList.add('active');
                    moveLineTo(match);
                    return true;
                }
            }
            return false;
        };

        window.addEventListener('scroll', updateActiveOnScroll, { passive: true });
        window.addEventListener('resize', () => moveLineTo(getActiveLink()), { passive: true });
        window.addEventListener('hashchange', syncFromHash);

        // Position immediately once fonts and layout are ready
        const initPosition = () => {
            if (!syncFromHash()) {
                updateActiveOnScroll();
            }
        };

        if (document.readyState === 'complete') {
            initPosition();
        } else {
            window.addEventListener('load', initPosition);
        }
        setTimeout(initPosition, 100);

        // Mobile menu toggle
        const toggleBtn = document.getElementById('mobileMenuToggle');
        const mobileNav = document.getElementById('mobileNavDrawer');
        if (toggleBtn && mobileNav) {
            toggleBtn.addEventListener('click', () => {
                mobileNav.classList.toggle('hidden');
            });
            mobileNav.querySelectorAll('a').forEach(a => {
                a.addEventListener('click', (e) => {
                    const href = a.getAttribute('href');
                    if (href && href.startsWith('#')) {
                        const id = href.substring(1);
                        if (id) {
                            e.preventDefault();
                            scrollToSection(id);
                            if (history.pushState) {
                                history.pushState(null, '', href);
                            }
                        }
                    }
                    mobileNav.classList.add('hidden');
                });
            });
        }
    }

    initLanguageSelector() {
        const trigger = document.getElementById('langDropdownTrigger');
        const menu = document.getElementById('langDropdownMenu');
        const chevron = document.getElementById('langChevron');
        const options = document.querySelectorAll('[data-lang-val]');

        const toggleMenu = () => {
            const isHidden = menu?.classList.contains('hidden');
            if (isHidden) {
                menu?.classList.remove('hidden');
                chevron?.classList.add('rotate-180');
            } else {
                menu?.classList.add('hidden');
                chevron?.classList.remove('rotate-180');
            }
        };

        trigger?.addEventListener('click', (e) => {
            e.stopPropagation();
            toggleMenu();
        });

        document.addEventListener('click', (e) => {
            if (!menu?.contains(e.target) && !trigger?.contains(e.target)) {
                menu?.classList.add('hidden');
                chevron?.classList.remove('rotate-180');
            }
        });

        options.forEach(opt => {
            opt.addEventListener('click', (e) => {
                const lang = opt.getAttribute('data-lang-val');
                this.switchLanguage(lang);
                menu?.classList.add('hidden');
                chevron?.classList.remove('rotate-180');
            });
        });

        // Mobile drawer language buttons
        document.querySelectorAll('[data-lang-btn]').forEach(b => {
            b.addEventListener('click', (e) => {
                const lang = b.getAttribute('data-lang-btn');
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
        
        // Update trigger button flag & code
        const meta = {
            'uz': { flag: '🇺🇿', code: 'UZ' },
            'en': { flag: '🇬🇧', code: 'EN' },
            'ru': { flag: '🇷🇺', code: 'RU' },
            'kz': { flag: '🇰🇿', code: 'KZ' },
            'kg': { flag: '🇰🇬', code: 'KG' }
        }[lang] || { flag: '🇺🇿', code: 'UZ' };

        const activeFlag = document.getElementById('activeLangFlag');
        const activeCode = document.getElementById('activeLangCode');
        if (activeFlag) activeFlag.textContent = meta.flag;
        if (activeCode) activeCode.textContent = meta.code;

        // Update dropdown checkmarks
        document.querySelectorAll('[data-lang-val]').forEach(opt => {
            const check = opt.querySelector('.lang-check');
            if (opt.getAttribute('data-lang-val') === lang) {
                opt.classList.add('bg-cyan-950/70', 'text-cyan-300', 'border-cyan-500/40');
                opt.classList.remove('text-slate-300', 'border-transparent');
                check?.classList.remove('hidden');
            } else {
                opt.classList.remove('bg-cyan-950/70', 'text-cyan-300', 'border-cyan-500/40');
                opt.classList.add('text-slate-300', 'border-transparent');
                check?.classList.add('hidden');
            }
        });

        // Mobile drawer buttons active state
        document.querySelectorAll('[data-lang-btn]').forEach(b => {
            if (b.getAttribute('data-lang-btn') === lang) {
                b.classList.add('bg-cyan-500/30', 'text-cyan-300', 'font-bold');
                b.classList.remove('text-slate-400');
            } else {
                b.classList.remove('bg-cyan-500/30', 'text-cyan-300', 'font-bold');
                b.classList.add('text-slate-400');
            }
        });

        // Translate data-i18n elements if any
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

        // Sync with presentation engine if initialized
        if (window.edugatePresentation && typeof window.edugatePresentation.setLanguage === 'function') {
            window.edugatePresentation.setLanguage(lang);
        }
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
        const tabContents = document.querySelectorAll('[data-platform-content]');
        const prevBtns = document.querySelectorAll('[data-dash-prev]');
        const nextBtns = document.querySelectorAll('[data-dash-next]');
        
        const tabsList = ['stat1', 'stat2', 'stat3', 'stat4'];
        let currentIndex = 0;

        const switchTab = (target, direction = 'next') => {
            const index = tabsList.indexOf(target);
            if (index !== -1) currentIndex = index;

            const animClass = direction === 'next' ? 'anim-slide-in-right' : 'anim-slide-in-left';

            tabContents.forEach(c => {
                c.classList.remove('anim-slide-in-right', 'anim-slide-in-left');
                if (c.getAttribute('data-platform-content') === target) {
                    c.classList.remove('hidden');
                    // Force browser reflow to reliably trigger CSS keyframe animation
                    void c.offsetWidth;
                    c.classList.add(animClass);
                } else {
                    c.classList.add('hidden');
                }
            });
        };

        prevBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const icon = btn.querySelector('.fa-arrow-left');
                if (icon) {
                    icon.classList.remove('btn-nudge-left');
                    void icon.offsetWidth;
                    icon.classList.add('btn-nudge-left');
                }
                currentIndex = (currentIndex - 1 + tabsList.length) % tabsList.length;
                switchTab(tabsList[currentIndex], 'prev');
            });
        });

        nextBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const icon = btn.querySelector('.fa-arrow-right');
                if (icon) {
                    icon.classList.remove('btn-nudge-right');
                    void icon.offsetWidth;
                    icon.classList.add('btn-nudge-right');
                }
                currentIndex = (currentIndex + 1) % tabsList.length;
                switchTab(tabsList[currentIndex], 'next');
            });
        });
    }

    initPhotoGallery() {
        const modal = document.getElementById('schoolGalleryModal');
        const heroTrigger = document.getElementById('heroPhotoCard');
        const fullscreenBtn = document.getElementById('heroFullscreenBtn');
        const closeBtn = document.getElementById('closeGalleryBtn');
        if (!modal) return;

        const openFullscreen = () => {
            modal.classList.remove('hidden');
            modal.classList.add('open');
            document.body.style.overflow = 'hidden';
        };

        const closeFullscreen = () => {
            modal.classList.remove('open');
            modal.classList.add('hidden');
            document.body.style.overflow = '';
        };

        fullscreenBtn?.addEventListener('click', (e) => {
            e.stopPropagation();
            openFullscreen();
        });
        heroTrigger?.addEventListener('click', (e) => {
            openFullscreen();
        });
        closeBtn?.addEventListener('click', closeFullscreen);
        modal.addEventListener('click', (e) => {
            if (e.target === modal) closeFullscreen();
        });

        window.addEventListener('keydown', (e) => {
            if (!modal.classList.contains('open')) return;
            if (e.key === 'Escape') closeFullscreen();
        });
    }

    initHardwareTabs() {
        const tabs = document.querySelectorAll('[data-hw-tab]');
        if (!tabs.length) return;

        const panels = {
            'turnstile': document.getElementById('hw-panel-turnstile'),
            'faceid': document.getElementById('hw-panel-faceid'),
            'ups': document.getElementById('hw-panel-ups')
        };

        const switchTab = (tabKey) => {
            tabs.forEach(btn => {
                const k = btn.getAttribute('data-hw-tab');
                if (k === tabKey) {
                    btn.className = "hw-tab-btn flex-1 py-2 px-3 rounded-lg text-xs font-mono font-bold flex items-center justify-center gap-1.5 transition cursor-pointer border border-cyan-400 bg-cyan-950/70 text-cyan-300 shadow-[0_0_15px_rgba(6,182,212,0.35)]";
                } else {
                    btn.className = "hw-tab-btn flex-1 py-2 px-3 rounded-lg text-xs font-mono font-bold flex items-center justify-center gap-1.5 transition cursor-pointer text-slate-400 hover:text-white border border-transparent";
                }
            });

            Object.entries(panels).forEach(([k, panel]) => {
                if (!panel) return;
                panel.classList.remove('anim-slide-in-right');
                if (k === tabKey) {
                    panel.classList.remove('hidden');
                    void panel.offsetWidth;
                    panel.classList.add('anim-slide-in-right');
                } else {
                    panel.classList.add('hidden');
                }
            });
        };

        tabs.forEach(btn => {
            btn.addEventListener('click', () => {
                const tabKey = btn.getAttribute('data-hw-tab');
                if (tabKey) switchTab(tabKey);
            });
        });
    }

    initContactForm() {
        const form = document.getElementById('contactLeadForm');
        const successMsg = document.getElementById('contactSuccessMsg');
        const submitBtn = document.getElementById('contactSubmitBtn');
        if (!form) return;

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());

            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin text-xs"></i> <span>YUBORILMOQDA...</span>';
            }

            try {
                await fetch('/api/contact', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                }).catch(() => null);
            } catch (err) {}

            setTimeout(() => {
                form.classList.add('hidden');
                if (successMsg) successMsg.classList.remove('hidden');
            }, 600);
        });
    }

}

document.addEventListener('DOMContentLoaded', () => {
    window.edugateApp = new EdugateApp();
});

