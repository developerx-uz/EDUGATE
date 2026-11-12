/**
 * EDUGATE & e-davomat.net Interactive 9-Slide Presentation Deck
 * Complete standalone presentation engine with autoplay, keyboard shortcuts,
 * fullscreen mode, high-resolution visual previews, and detailed technical specifications.
 */

const PRESENTATION_SLIDES = [
    {
        id: 1,
        topic: "01 / TIZIM MAQSADI",
        title: "e-davomat.net & EDUGATE — Maktablar uchun xavfsizlik va davomat tizimi",
        overview: "Maktablarda o'quvchilar davomatini qulay yuritish, maktabga begona shaxslar kirishining oldini olish va ota-onalarni real vaqtda xabardor qilish uchun yaratilgan ishonchli apparat-dasturiy majmua.",
        image: "assets/turniket_ishlash_mexanizmi_1792321765311-Cyy4YXDA.jpg",
        imageBadge: "Avtomatlashtirilgan O'tish Mexanizmi",
        specs: [
            { label: "Tizim vazifasi", value: "Davomat va xavfsizlik" },
            { label: "Qamrov", value: "Umumta'lim maktablari" },
            { label: "Yuzni tanish", value: "Aqlli kamera tizimi (AI)" },
            { label: "Ma'lumotlar uzatish", value: "Xavfsiz va ishonchli VPN" }
        ],
        keyPoints: [
            "Qog'oz jurnallar o'rniga to'liq shaffof raqamli ro'yxatga olish",
            "O'quvchi maktab binosiga kirganda va chiqqanda aniq vaqtni sekundigacha qayd qilish",
            "Maktab hududiga begona va ruxsatsiz shaxslarning kirishining 100% oldini olish"
        ]
    },
    {
        id: 2,
        topic: "02 / USKUNALAR VA TURNIKETLAR",
        title: "Maktab kirishidagi qulay va xavfsiz tezkor turniketlar",
        overview: "Ertalabki gavjum vaqtlarda ham o'quvchilar navbatsiz, tez va erkin kirib-chiqishi uchun maxsus moslashtirilgan mustahkam zanglamaydigan turniketlar. Bolalar xavfsizligi to'liq ta'minlangan.",
        image: "assets/termiz_11_maktab_turniket_clean-B0ZTyEvY.jpg",
        imageBadge: "Termiz 11-Maktab Real O'rnatilgan Uskunalar",
        specs: [
            { label: "Korpus materiali", value: "AISI 304 Zanglamas po'lat" },
            { label: "O'tish qulayligi", value: "Navbatsiz, erkin va tez" },
            { label: "O'tish tezligi", value: "45-50 kishi / daqiqada" },
            { label: "Bolalar xavfsizligi", value: "Qisilib qolishdan infraqizil himoya" }
        ],
        keyPoints: [
            "Tirbandlik hosil qilmaydigan tezkor shisha va flap barrier qanotlari",
            "Bolalar qisilib qolishiga qarshi 8 juft infraqizil xavfsizlik datchiklari",
            "Favqulodda holat va yong'in signalizatsiyasida avtomatik ochiq qolish (Anti-panika)"
        ]
    },
    {
        id: 3,
        topic: "03 / VILOYAT ANALITIKASI",
        title: "Surxondaryo viloyati bo'yicha markaziy monitoring xaritasi",
        overview: "Tuman va shahar xalq ta'limi bo'limlari hamda viloyat hokimligi uchun hududdagi barcha maktablarning davomati va o'quvchilar sonini real vaqt rejimida ko'rsatuvchi interaktiv xarita paneli.",
        image: "assets/statistika1-DhCv2NLr.png",
        imageBadge: "Surxondaryo & Respublika Markaziy Monitoring Xaritasi",
        specs: [
            { label: "Qamrab olingan maktablar", value: "948 ta umumta'lim maktabi" },
            { label: "Jami o'quvchilar bazasi", value: "828,867 nafar o'quvchi" },
            { label: "Faol turniketlar", value: "2,840 ta xavfsiz o'tish yo'lagi" },
            { label: "Viloyat davomati", value: "98.4% kunlik ko'rsatkich" }
        ],
        keyPoints: [
            "14 ta tuman va Termiz shahri bo'yicha tezkor statistik tahlil",
            "O'g'il bolalar va qizlar balansi bo'yicha real vaqt grafigi",
            "Hududlar kesimida davomat pasaygan maktablarni oniy aniqlash va tekshirish"
        ]
    },
    {
        id: 4,
        topic: "04 / RAQAMLI DAVOMAT",
        title: "Sinflar kesimida kunlik va oylik elektron hisobotlar",
        overview: "O'qituvchilar va direktor o'rinbosarlari uchun qog'ozbozlikdan xoli elektron jurnal. Har bir o'quvchining o'quv kunlari, kelgan va dars qoldirgan kunlari sekundigacha aniq hisoblanadi.",
        image: "assets/edavomat-panel-1-CmvD_PlI.png",
        imageBadge: "Sinflar & Maktab Boshqaruvi Paneli",
        specs: [
            { label: "Hisobot turi", value: "Avtomatlashtirilgan elektron jurnal" },
            { label: "Aniqlik darajasi", value: "Sekundigacha kirish-chiqish vaqti" },
            { label: "Eksport formati", value: "Excel (.xlsx), PDF, API" },
            { label: "Filtrlash imkoni", value: "Sinf, sana, sababli/sababsiz" }
        ],
        keyPoints: [
            "O'quvchining haqiqiy ishtirok foizi avtomatik hisoblanishi",
            "Vaqtni tejash: o'qituvchi 15 daqiqa davomat olishi shart emas",
            "Soxta belgilashlar va inson omilining to'liq yo'q qilinishi"
        ]
    },
    {
        id: 5,
        topic: "05 / YUZNI TANISH (FACE ID)",
        title: "O'quvchilarni yuzidan bir zumda tanish tizimi",
        overview: "Har bir o'quvchi maktabga kirishda to'xtab turishi shart emas — aqlli kamera uning yuzini yaqinlashishi bilanoq taniydi va turniketni ochadi.",
        image: "assets/face_recognition_ai_scanner_1791053871354-Ix6loFC9.jpg",
        imageBadge: "3D WDR Dual-Lens Neyron Biometrik Skaner",
        specs: [
            { label: "Tanish usuli", value: "Aqlli 3D neyron yuzni tanish" },
            { label: "Tanish tezligi", value: "0.18 soniya (kutishlarsiz)" },
            { label: "Aniqlik darajasi", value: "99.87% (xatosiz tanish)" },
            { label: "Xotira sig'imi", value: "50,000+ o'quvchi bazasi" }
        ],
        keyPoints: [
            "O'quvchi ulg'ayganda yoki soch turmagi o'zgarganda ham taniydi",
            "Niqob, ko'zoynak yoki qishki kiyimda ham to'siqsiz tanish",
            "Surat yoki telefon ekranidagi videoni ko'rsatib aldab bo'lmaydi (Anti-Spoofing)"
        ]
    },
    {
        id: 6,
        topic: "06 / ELEKTRON JURNAL",
        title: "Avtomatlashtirilgan elektron jurnal va sinflar davomati",
        overview: "Turniketlardan o'tgan barcha o'quvchilar ma'lumotlari sinflar kesimida yagona elektron jurnalga to'planadi. O'qituvchilar dars vaqtini davomat olishga sarflamaydi, barchasi soniyalar ichida avtomatik qayd etiladi.",
        image: "assets/elektron-jadval-BFo-eBY-.png",
        imageBadge: "Avtomatik e-Maktab & Kundalik Moslashuvi",
        specs: [
            { label: "Jurnal formati", value: "Excel (XLSX), PDF, Onlayn jadval" },
            { label: "Qayd etish aniqligi", value: "07:58:12 (soniyasigacha aniq vaqt)" },
            { label: "Hisobot turlari", value: "Sinf, maktab, tuman kesimida" },
            { label: "Integratsiya", value: "e-maktab (Kundalik) tizimiga to'liq mos" }
        ],
        keyPoints: [
            "Sinf rahbarlari va o'qituvchilarning qog'ozbozlik yukini 100% bartaraf etish",
            "O'quvchilarning darsga kelish va ketish vaqtini shaffof va adolatli qayd etish",
            "Maktab rahbariyati uchun bir zumda umumiy elektron davomat tahlili"
        ]
    },
    {
        id: 7,
        topic: "07 / OTA-ONA BILDIRISHNOMASI",
        title: "Ota-onalarga zumda yetib boruvchi Telegram va SMS xabarlari",
        overview: "Farzandingiz maktabga kirgan va darsdan so'ng chiqqan zahoti ota-onaning telefoniga aniq vaqt ko'rsatilgan rasmiy xabarnoma keladi.",
        image: "assets/telegram_edavomat_xabarnoma_1792418685514-BhwRdhnc.jpg",
        imageBadge: "Telegram Bot Orqali Oniy Fotoxabarnoma",
        specs: [
            { label: "Xabar yetkazish", value: "Bir zumda ota-onaga boradi" },
            { label: "Yetkazilish kafolati", value: "100% har bir ota-onaga" },
            { label: "Xabar turlari", value: "Oddiy SMS va qulay Telegram bot" },
            { label: "Ota-ona uchun", value: "Ko'ngil to'liq xotirjam" }
        ],
        keyPoints: [
            "Ota-ona farzandining maktabga yetib borganidan ko'ngli to'liq to'q bo'ladi",
            "Darsdan so'ng maktabdan chiqqan vaqti ham darhol ko'rsatiladi",
            "Ota-ona va maktab ma'muriyati o'rtasida mustahkam ishonch ko'prigi"
        ]
    },
    {
        id: 8,
        topic: "08 / MA'LUMOTLAR XAVFSIZLIGI",
        title: "O'quvchilar ma'lumotlari to'liq va qat'iy himoyalangan",
        overview: "Maktab va o'quvchilarning ma'lumotlari begona ko'zlardan himoyalangan xavfsiz tizimda saqlanadi. Ma'lumotlarni faqat maktab ma'muriyati ko'ra oladi.",
        image: "assets/edavomat-panel-4-Cf-FRJvB.png",
        imageBadge: "Shifrlangan Kriptografik Xavfsizlik Paneli",
        specs: [
            { label: "Xavfsizlik darajasi", value: "100% himoyalangan va maxfiy" },
            { label: "Server joylashuvi", value: "O'zbekistondagi xavfsiz serverda" },
            { label: "Kirish huquqi", value: "Faqat maktab rahbariyati uchun" },
            { label: "Ishonchlilik", value: "Begona shaxslar kira olmaydi" }
        ],
        keyPoints: [
            "Biometrik ma'lumotlar tashqi begona tarmoqqa chiqmaydi",
            "Serverlar O'zbekiston hududida xavfsiz ma'lumotlar markazida joylashgan",
            "Faqat tasdiqlangan maktab direktorlari va inspektorlar kirishi mumkin"
        ]
    },
    {
        id: 9,
        topic: "09 / MILLIY GVARDIYA XULOSASI",
        title: "Tizimning maktablarda tartib-intizomni oshirishdagi amaliy natijasi",
        overview: "O'zbekiston Respublikasi Milliy Gvardiyasi Surxondaryo viloyati boshqarmasi tomonidan loyihaning ta'lim sifatiga va profilaktikaga ijobiy ta'siri rasman tasdiqlandi.",
        image: "assets/milliy_gvardiya_termiz_10_1792418655393-C6Z2hvMJ.jpg",
        imageBadge: "Milliy Gvardiya Xodimlari Bilan Joyidagi Nazorat",
        specs: [
            { label: "Mas'ul organ", value: "O'zbekiston Milliy Gvardiyasi" },
            { label: "Hudud", value: "Surxondaryo viloyati (Termiz shahri)" },
            { label: "Asosiy natija", value: "Dars qoldirish 74% ga kamaydi" },
            { label: "Status", value: "Barcha tumanlarda to'liq tasdiqlangan" }
        ],
        keyPoints: [
            "Maktab hududiga begona shaxslarning kirishi 100% cheklandi",
            "Davomat ko'rsatkichi viloyat bo'yicha 98.4% ga ko'tarildi",
            "Loyiha barcha hududlarda joriy etishga to'liq tavsiya etildi"
        ]
    }
];

class PresentationEngine {
    constructor() {
        this.slides = PRESENTATION_SLIDES;
        this.currentIndex = 0;
        this.isPlaying = false;
        this.playTimer = null;
        this.slideDuration = 6000;

        this.initDOMElements();
        this.bindEvents();
        this.renderSlide(0);
    }

    initDOMElements() {
        // Dedicated standalone page elements
        this.pageTopic = document.getElementById('presSlideTopic');
        this.pageTitle = document.getElementById('presSlideTitle');
        this.pageOverview = document.getElementById('presSlideOverview');
        this.pageImage = document.getElementById('presSlideImage');
        this.pageImageBadge = document.getElementById('presSlideImageBadge');
        this.pageSpecsGrid = document.getElementById('presSlideSpecsGrid');
        this.pageKeyPoints = document.getElementById('presSlideKeyPoints');
        this.pageSlideCounter = document.getElementById('presSlideCounter');
        this.pageDotsContainer = document.getElementById('presDots');
        this.pagePrevBtn = document.getElementById('presPrevBtn');
        this.pageNextBtn = document.getElementById('presNextBtn');
        this.pageAutoBtn = document.getElementById('presAutoBtn');
        this.pageFullscreenBtn = document.getElementById('presFullscreenBtn');

        // Modal elements (if on index page)
        this.modal = document.getElementById('presentationModal');
        this.openModalBtns = document.querySelectorAll('[data-open-presentation]');
        this.closeModalBtn = document.getElementById('closePresentationModalBtn');
        this.modalTopic = document.getElementById('presModalTopic');
        this.modalTitle = document.getElementById('presModalTitle');
        this.modalOverview = document.getElementById('presModalOverview');
        this.modalImage = document.getElementById('presModalImage');
        this.modalImageBadge = document.getElementById('presModalImageBadge');
        this.modalSpecsGrid = document.getElementById('presModalSpecsGrid');
        this.modalKeyPoints = document.getElementById('presModalKeyPoints');
        this.modalSlideCounter = document.getElementById('presModalSlideCounter');
        this.modalDotsContainer = document.getElementById('presModalDots');
        this.modalPrevBtn = document.getElementById('presModalPrevBtn');
        this.modalNextBtn = document.getElementById('presModalNextBtn');
        this.modalAutoBtn = document.getElementById('presModalAutoBtn');
        this.modalFullscreenBtn = document.getElementById('presModalFullscreenBtn');

        // Build dots
        this.buildDotChips();
    }

    buildDotChips() {
        const renderDots = (container) => {
            if (!container) return;
            container.innerHTML = '';
            this.slides.forEach((slide, idx) => {
                const btn = document.createElement('button');
                btn.type = 'button';
                btn.className = `pres-dot px-3 py-1 rounded-lg text-xs font-mono font-bold transition ${
                    idx === this.currentIndex
                        ? 'bg-cyan-500 text-white shadow-[0_0_10px_rgba(6,182,212,0.7)]'
                        : 'bg-slate-800/80 text-slate-400 hover:text-white hover:bg-slate-700'
                }`;
                btn.textContent = `0${slide.id}`;
                btn.title = slide.title;
                btn.addEventListener('click', () => {
                    this.goToSlide(idx);
                });
                container.appendChild(btn);
            });
        };

        renderDots(this.pageDotsContainer);
        renderDots(this.modalDotsContainer);
    }

    bindEvents() {
        // Dedicated page buttons
        if (this.pagePrevBtn) this.pagePrevBtn.addEventListener('click', () => this.prevSlide());
        if (this.pageNextBtn) this.pageNextBtn.addEventListener('click', () => this.nextSlide());
        if (this.pageAutoBtn) this.pageAutoBtn.addEventListener('click', () => this.toggleAutoPlay());
        if (this.pageFullscreenBtn) this.pageFullscreenBtn.addEventListener('click', () => this.toggleFullscreen());

        // Modal buttons
        if (this.modalPrevBtn) this.modalPrevBtn.addEventListener('click', () => this.prevSlide());
        if (this.modalNextBtn) this.modalNextBtn.addEventListener('click', () => this.nextSlide());
        if (this.modalAutoBtn) this.modalAutoBtn.addEventListener('click', () => this.toggleAutoPlay());
        if (this.modalFullscreenBtn) this.modalFullscreenBtn.addEventListener('click', () => this.toggleFullscreen());

        if (this.closeModalBtn) {
            this.closeModalBtn.addEventListener('click', () => this.closeModal());
        }

        // Global keyboard listeners
        document.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowRight') {
                this.nextSlide();
            } else if (e.key === 'ArrowLeft') {
                this.prevSlide();
            } else if (e.key === ' ') {
                e.preventDefault();
                this.toggleAutoPlay();
            } else if (e.key.toLowerCase() === 'f') {
                this.toggleFullscreen();
            } else if (e.key === 'Escape') {
                if (this.modal && !this.modal.classList.contains('hidden')) {
                    this.closeModal();
                } else if (window.location.pathname.includes('presentation')) {
                    window.location.href = '/edugate/';
                }
            }
        });
    }

    renderSlide(index) {
        if (index < 0) index = this.slides.length - 1;
        if (index >= this.slides.length) index = 0;
        this.currentIndex = index;

        const slide = this.slides[index];

        const updateContent = (elements) => {
            if (!elements.topic) return;

            elements.topic.textContent = slide.topic;
            elements.title.textContent = slide.title;
            elements.overview.textContent = slide.overview;

            if (elements.image) {
                elements.image.src = slide.image;
                elements.image.alt = slide.title;
            }

            if (elements.imageBadge) {
                elements.imageBadge.textContent = slide.imageBadge;
            }

            if (elements.slideCounter) {
                elements.slideCounter.textContent = `${slide.id} / ${this.slides.length}`;
            }

            // Specs grid
            if (elements.specsGrid) {
                elements.specsGrid.innerHTML = slide.specs.map(spec => `
                    <div class="p-3 bg-slate-900/90 rounded-xl border border-slate-800">
                        <span class="text-[10px] uppercase text-slate-400 font-mono block">${spec.label}</span>
                        <h5 class="text-xs sm:text-sm font-bold text-cyan-300 mt-1">${spec.value}</h5>
                    </div>
                `).join('');
            }

            // Key Points
            if (elements.keyPoints) {
                elements.keyPoints.innerHTML = slide.keyPoints.map(point => `
                    <li class="flex items-start gap-2 text-xs sm:text-[13px] text-slate-300">
                        <i class="fas fa-check-circle text-emerald-400 text-xs mt-1 shrink-0"></i>
                        <span>${point}</span>
                    </li>
                `).join('');
            }
        };

        // Update dedicated page elements
        updateContent({
            topic: this.pageTopic,
            title: this.pageTitle,
            overview: this.pageOverview,
            image: this.pageImage,
            imageBadge: this.pageImageBadge,
            slideCounter: this.pageSlideCounter,
            specsGrid: this.pageSpecsGrid,
            keyPoints: this.pageKeyPoints
        });

        // Update modal elements
        updateContent({
            topic: this.modalTopic,
            title: this.modalTitle,
            overview: this.modalOverview,
            image: this.modalImage,
            imageBadge: this.modalImageBadge,
            slideCounter: this.modalSlideCounter,
            specsGrid: this.modalSpecsGrid,
            keyPoints: this.modalKeyPoints
        });

        // Update active dot indicators
        this.updateActiveDots();
    }

    updateActiveDots() {
        const update = (container) => {
            if (!container) return;
            const buttons = container.querySelectorAll('button');
            buttons.forEach((btn, idx) => {
                if (idx === this.currentIndex) {
                    btn.className = 'pres-dot px-3 py-1 rounded-lg text-xs font-mono font-bold transition bg-cyan-500 text-white shadow-[0_0_10px_rgba(6,182,212,0.7)]';
                } else {
                    btn.className = 'pres-dot px-3 py-1 rounded-lg text-xs font-mono font-bold transition bg-slate-800/80 text-slate-400 hover:text-white hover:bg-slate-700';
                }
            });
        };

        update(this.pageDotsContainer);
        update(this.modalDotsContainer);
    }

    goToSlide(index) {
        this.renderSlide(index);
        if (this.isPlaying) {
            this.restartAutoPlay();
        }
    }

    nextSlide() {
        this.goToSlide(this.currentIndex + 1);
    }

    prevSlide() {
        this.goToSlide(this.currentIndex - 1);
    }

    toggleAutoPlay() {
        this.isPlaying = !this.isPlaying;
        const updateBtn = (btn) => {
            if (!btn) return;
            if (this.isPlaying) {
                btn.innerHTML = '<i class="fas fa-pause text-[10px]"></i> <span>PAUZA</span>';
                btn.classList.add('bg-amber-500/20', 'text-amber-400', 'border-amber-500/40');
            } else {
                btn.innerHTML = '<i class="fas fa-play text-[10px]"></i> <span>AVTO</span>';
                btn.classList.remove('bg-amber-500/20', 'text-amber-400', 'border-amber-500/40');
            }
        };

        updateBtn(this.pageAutoBtn);
        updateBtn(this.modalAutoBtn);

        if (this.isPlaying) {
            this.startAutoPlayTimer();
        } else {
            this.stopAutoPlayTimer();
        }
    }

    startAutoPlayTimer() {
        this.stopAutoPlayTimer();
        this.playTimer = setInterval(() => {
            this.nextSlide();
        }, this.slideDuration);
    }

    stopAutoPlayTimer() {
        if (this.playTimer) {
            clearInterval(this.playTimer);
            this.playTimer = null;
        }
    }

    restartAutoPlay() {
        if (this.isPlaying) {
            this.startAutoPlayTimer();
        }
    }

    openModal() {
        if (!this.modal) return;
        this.modal.classList.remove('hidden');
        document.body.classList.add('overflow-hidden');
        this.renderSlide(this.currentIndex);
    }

    closeModal() {
        if (!this.modal) return;
        this.modal.classList.add('hidden');
        document.body.classList.remove('overflow-hidden');
        if (this.isPlaying) {
            this.toggleAutoPlay();
        }
    }

    toggleFullscreen() {
        if (!document.fullscreenElement) {
            if (document.documentElement.requestFullscreen) {
                document.documentElement.requestFullscreen();
            } else if (document.documentElement.webkitRequestFullscreen) {
                document.documentElement.webkitRequestFullscreen();
            }
        } else {
            if (document.exitFullscreen) {
                document.exitFullscreen();
            }
        }
    }

    initStandaloneMode() {
        this.renderSlide(0);
    }
}

// Initialize Presentation Engine
document.addEventListener('DOMContentLoaded', () => {
    window.edugatePresentation = new PresentationEngine();
});
