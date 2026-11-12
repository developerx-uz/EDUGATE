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
    initPhotoGallery() {
        const modal = document.getElementById('schoolGalleryModal');
        const heroTrigger = document.getElementById('heroPhotoCard');
        if (!modal || !heroTrigger) return;

        const mainImg = document.getElementById('galleryMainImg');
        const titleEl = document.getElementById('galleryTitle');
        const descEl = document.getElementById('galleryDesc');
        const counterEl = document.getElementById('galleryCounter');
        const prevBtn = document.getElementById('galleryPrevBtn');
        const nextBtn = document.getElementById('galleryNextBtn');
        const closeBtn = document.getElementById('closeGalleryBtn');
        const thumbContainer = document.getElementById('galleryThumbnails');

        const galleryData = [
            {
                src: 'assets/termiz_11_maktab_turniket_clean-B0ZTyEvY.jpg',
                title: "Termiz 11-maktab — Real Turniket Tizimi",
                desc: "Surxondaryo viloyati Termiz shahridagi 11-maktabga o'rnatilgan ST-100 turniketlari va xavfsiz o'tish zali."
            },
            {
                src: 'assets/milliy_gvardiya_termiz_10_1792418655393-C6Z2hvMJ.jpg',
                title: "Milliy Gvardiya Xavfsizlik Nazorati",
                desc: "Maktab hududida xavfsizlikni ta'minlash va profilaktika inspektori tomonidan real vaqtda davomat nazorati."
            },
            {
                src: 'assets/face_recognition_ai_scanner_1791053871354-Ix6loFC9.jpg',
                title: "Face ID Biometrik AI Terminali",
                desc: "0.18 soniyada 128 ta yuz nuqtasini aniqlovchi infraqizil (IR) va optik kamerali aqlli biometrik terminal."
            },
            {
                src: 'assets/telegram_edavomat_xabarnoma_1792418685514-BhwRdhnc.jpg',
                title: "Ota-onalar Uchun Oniy Telegram Xabarnomasi",
                desc: "Farzand maktab turniketidan o'tishi bilan ota-onaning telefoniga kirish vaqti va fotosurati yetib boradi."
            },
            {
                src: 'assets/turniket_ishlash_mexanizmi_1792321765311-Cyy4YXDA.jpg',
                title: "ST-100 Turniket Ichki Mexanizmi",
                desc: "AISI-304 zanglamaydigan po'lat korpus, 24V brushless silliq motor va 8 soatlik avtonom UPS ta'minoti."
            }
        ];

        let currentIndex = 0;

        const renderSlide = (index) => {
            currentIndex = (index + galleryData.length) % galleryData.length;
            const item = galleryData[currentIndex];
            if (mainImg) mainImg.src = item.src;
            if (titleEl) titleEl.textContent = item.title;
            if (descEl) descEl.textContent = item.desc;
            if (counterEl) counterEl.textContent = `${currentIndex + 1} / ${galleryData.length}`;

            // Update thumbnails active state
            if (thumbContainer) {
                const thumbs = thumbContainer.querySelectorAll('button');
                thumbs.forEach((thumb, idx) => {
                    if (idx === currentIndex) {
                        thumb.classList.add('border-cyan-400', 'ring-2', 'ring-cyan-500/50', 'opacity-100');
                        thumb.classList.remove('opacity-50', 'border-slate-800');
                    } else {
                        thumb.classList.remove('border-cyan-400', 'ring-2', 'ring-cyan-500/50', 'opacity-100');
                        thumb.classList.add('opacity-50', 'border-slate-800');
                    }
                });
            }
        };

        // Render thumbnails
        if (thumbContainer && thumbContainer.children.length === 0) {
            galleryData.forEach((item, idx) => {
                const btn = document.createElement('button');
                btn.type = 'button';
                btn.className = 'rounded-lg overflow-hidden border aspect-[16/10] bg-black transition hover:opacity-100 ' + (idx === 0 ? 'border-cyan-400 ring-2 ring-cyan-500/50 opacity-100' : 'border-slate-800 opacity-50');
                btn.innerHTML = `<img src="${item.src}" alt="${item.title}" class="w-full h-full object-cover">`;
                btn.addEventListener('click', () => renderSlide(idx));
                thumbContainer.appendChild(btn);
            });
        }

        const openGallery = (idx = 0) => {
            renderSlide(idx);
            modal.classList.add('open');
            document.body.style.overflow = 'hidden';
        };

        const closeGallery = () => {
            modal.classList.remove('open');
            document.body.style.overflow = '';
        };

        heroTrigger.addEventListener('click', () => openGallery(0));
        closeBtn?.addEventListener('click', closeGallery);
        modal.addEventListener('click', (e) => {
            if (e.target === modal) closeGallery();
        });

        prevBtn?.addEventListener('click', (e) => {
            e.stopPropagation();
            renderSlide(currentIndex - 1);
        });

        nextBtn?.addEventListener('click', (e) => {
            e.stopPropagation();
            renderSlide(currentIndex + 1);
        });

        window.addEventListener('keydown', (e) => {
            if (!modal.classList.contains('open')) return;
            if (e.key === 'Escape') closeGallery();
            if (e.key === 'ArrowLeft') renderSlide(currentIndex - 1);
            if (e.key === 'ArrowRight') renderSlide(currentIndex + 1);
        });
    }

}

document.addEventListener('DOMContentLoaded', () => {
    window.edugateApp = new EdugateApp();
});

