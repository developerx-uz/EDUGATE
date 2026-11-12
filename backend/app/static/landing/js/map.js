/**
 * EDUGATE Uzbekistan 12 Viloyat Interactive Regional Telemetry Radar
 * With Interactive Vector SVG Map of Uzbekistan & Real-Time Regional Telemetry
 */

const UzbekistanRegionsData = {
    andijan: {
        name: "Andijon viloyati",
        short: "Andijon",
        schools: 780,
        students: 510000,
        attendance: "98.3%",
        turnstiles: 2300,
        topDistrict: "Andijon sh. (99.1%)",
        desc: "Farg'ona vodiysining aholi zich hududi, 780 ta umumta'lim maktabida Face ID va Telegram xabarnoma to'liq joriy etilgan."
    },
    bukhara: {
        name: "Buxoro viloyati",
        short: "Buxoro",
        schools: 540,
        students: 360000,
        attendance: "98.7%",
        turnstiles: 1650,
        topDistrict: "Buxoro sh. (99.4%)",
        desc: "Tarixiy va ta'lim salohiyati yuqori hudud, davomat barqarorligi bo'yicha respublikada yetakchi 3 talikda."
    },
    fergana: {
        name: "Farg'ona viloyati",
        short: "Farg'ona",
        schools: 960,
        students: 640000,
        attendance: "98.6%",
        turnstiles: 2850,
        topDistrict: "Farg'ona sh. (99.2%)",
        desc: "Keng qamrovli maktablar tarmog'i, 960 ta maktab yagona monitoring markaziga optik tolali VPN orqali bog'langan."
    },
    jizzakh: {
        name: "Jizzax viloyati",
        short: "Jizzax",
        schools: 550,
        students: 310000,
        attendance: "98.0%",
        turnstiles: 1400,
        topDistrict: "Jizzax sh. (98.8%)",
        desc: "Tog'li va dasht tumanlaridagi barcha maktablar uzluksiz SmartUPS batareyalari bilan ta'minlangan."
    },
    khorezm: {
        name: "Xorazm viloyati",
        short: "Xorazm",
        schools: 530,
        students: 340000,
        attendance: "98.5%",
        turnstiles: 1550,
        topDistrict: "Urganch sh. (99.0%)",
        desc: "Xiva va Urganch shaharlari hamda barcha tuman maktablari to'liq biometrik ro'yxatdan o'tkazilgan."
    },
    namangan: {
        name: "Namangan viloyati",
        short: "Namangan",
        schools: 710,
        students: 490000,
        attendance: "98.2%",
        turnstiles: 2100,
        topDistrict: "Namangan sh. (98.9%)",
        desc: "Ota-onalarga oniy Telegram xabarnoma yetkazish darajasi 99.4% ni tashkil qiladi."
    },
    navoi: {
        name: "Navoiy viloyati",
        short: "Navoiy",
        schools: 360,
        students: 220000,
        attendance: "98.8%",
        turnstiles: 1100,
        topDistrict: "Navoiy sh. (99.5%)",
        desc: "Sanoat va konchilik shaharlarida eng yuqori intizom ko'rsatkichlari qayd etilmoqda."
    },
    kashkadarya: {
        name: "Qashqadaryo viloyati",
        short: "Qashqadaryo",
        schools: 1180,
        students: 690000,
        attendance: "97.9%",
        turnstiles: 3100,
        topDistrict: "Qarshi sh. (98.6%)",
        desc: "Eng ko'p maktab soniga ega viloyat, 1,180 ta maktab bo'yicha markaziy MMTV nazorati o'rnatilgan."
    },
    samarkand: {
        name: "Samarqand viloyati",
        short: "Samarqand",
        schools: 1250,
        students: 780000,
        attendance: "98.4%",
        turnstiles: 3400,
        topDistrict: "Samarqand sh. (99.2%)",
        desc: "Respublika bo'yicha eng yirik ta'lim kontingenti: 780,000 nafar o'quvchi biometrik reyestrga kiritilgan."
    },
    sirdarya: {
        name: "Sirdaryo viloyati",
        short: "Sirdaryo",
        schools: 310,
        students: 180000,
        attendance: "98.2%",
        turnstiles: 920,
        topDistrict: "Guliston sh. (98.7%)",
        desc: "Ixcham va yuqori tezlikda boshqariladigan hududiy infratuzilma, 100% raqamlashgan davomat jurnali."
    },
    surkhandarya: {
        name: "Surxondaryo viloyati",
        short: "Surxondaryo",
        schools: 948,
        students: 580000,
        attendance: "98.4%",
        turnstiles: 2800,
        topDistrict: "Termiz sh. (99.3%)",
        desc: "Termiz shahri va 14 ta tumandagi barcha 948 ta maktab Milliy Gvardiya xulosasi bilan to'liq jihozlangan."
    },
    tashkent_region: {
        name: "Toshkent viloyati",
        short: "Toshkent vil.",
        schools: 890,
        students: 540000,
        attendance: "98.1%",
        turnstiles: 2600,
        topDistrict: "Chirchiq sh. (98.8%)",
        desc: "Poytaxt viloyati bo'ylab 890 ta maktabda yagona markaziy xavfsizlik va davomat ekotizimi faoliyat yuritmoqda."
    },
};

class UzbekistanMapController {
    constructor() {
        this.currentRegion = 'surkhandarya';
        this.init();
    }

    init() {
        // 1. Click on SVG Region Paths
        const svgPaths = document.querySelectorAll('.map-region-path');
        svgPaths.forEach(path => {
            path.addEventListener('click', (e) => {
                const regKey = e.currentTarget.getAttribute('data-region');
                if (regKey && UzbekistanRegionsData[regKey]) {
                    this.selectRegion(regKey);
                }
            });

            // Hover effect
            path.addEventListener('mouseenter', (e) => {
                const regKey = e.currentTarget.getAttribute('data-region');
                if (regKey !== this.currentRegion) {
                    e.currentTarget.setAttribute('fill', '#075985');
                    e.currentTarget.setAttribute('stroke', '#38bdf8');
                    e.currentTarget.setAttribute('stroke-width', '2.2');
                }
            });

            path.addEventListener('mouseleave', (e) => {
                const regKey = e.currentTarget.getAttribute('data-region');
                if (regKey !== this.currentRegion) {
                    e.currentTarget.setAttribute('fill', '#0c1e36');
                    e.currentTarget.setAttribute('stroke', '#1e3a5f');
                    e.currentTarget.setAttribute('stroke-width', '1.5');
                }
            });
        });

        // 2. Click on Quick Button Pills
        const buttons = document.querySelectorAll('.region-btn, [data-region]:not(.map-region-path)');
        buttons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const regKey = e.currentTarget.getAttribute('data-region');
                if (regKey && UzbekistanRegionsData[regKey]) {
                    this.selectRegion(regKey);
                }
            });
        });

        // Initialize with default region
        this.selectRegion(this.currentRegion);
    }

    selectRegion(key) {
        const data = UzbekistanRegionsData[key];
        if (!data) return;
        this.currentRegion = key;

        // 1. Update SVG Region Paths
        document.querySelectorAll('.map-region-path').forEach(path => {
            const regKey = path.getAttribute('data-region');
            if (regKey === key) {
                path.classList.add('active');
                path.setAttribute('fill', '#0284c7');
                path.setAttribute('stroke', '#38bdf8');
                path.setAttribute('stroke-width', '2.5');
                path.setAttribute('filter', 'url(#map-glow-active)');
            } else {
                path.classList.remove('active');
                path.setAttribute('fill', '#0c1e36');
                path.setAttribute('stroke', '#1e3a5f');
                path.setAttribute('stroke-width', '1.5');
                path.removeAttribute('filter');
            }
        });

        // 2. Update SVG Pins & Labels
        document.querySelectorAll('.map-region-label').forEach(lbl => {
            const regKey = lbl.getAttribute('data-region');
            const dot = lbl.querySelector('circle[id^="svg-dot-"]');
            const ping = lbl.querySelector('circle[id^="svg-ping-"]');
            const txt = lbl.querySelector('text[id^="svg-txt-"]');

            if (regKey === key) {
                if (dot) {
                    dot.setAttribute('fill', '#38bdf8');
                    dot.setAttribute('r', '4.5');
                }
                if (ping) ping.classList.remove('hidden');
                if (txt) {
                    txt.setAttribute('fill', '#38bdf8');
                    txt.setAttribute('font-weight', '800');
                    txt.setAttribute('font-size', '11.5');
                }
            } else {
                if (dot) {
                    dot.setAttribute('fill', '#06b6d4');
                    dot.setAttribute('r', '3');
                }
                if (ping) ping.classList.add('hidden');
                if (txt) {
                    txt.setAttribute('fill', '#cbd5e1');
                    txt.setAttribute('font-weight', '600');
                    txt.setAttribute('font-size', '10.5');
                }
            }
        });

        // 3. Update Quick Buttons
        document.querySelectorAll('.region-btn').forEach(btn => {
            const regKey = btn.getAttribute('data-region');
            if (regKey === key) {
                btn.className = "region-btn px-2.5 py-1.5 rounded-lg border text-[11px] font-mono whitespace-nowrap transition cursor-pointer flex items-center gap-1.5 border-cyan-400 bg-cyan-950/70 text-cyan-300 shadow-[0_0_12px_rgba(6,182,212,0.35)]";
            } else {
                btn.className = "region-btn px-2.5 py-1.5 rounded-lg border text-[11px] font-mono whitespace-nowrap transition cursor-pointer flex items-center gap-1.5 border-slate-800 bg-slate-900/70 text-slate-300 hover:border-cyan-500/60 hover:text-white";
            }
        });

        // 4. Update Right Telemetry Console DOM Elements
        const nameEl = document.getElementById('mapSelectedRegionName');
        const schoolsEl = document.getElementById('mapSelectedSchools');
        const studentsEl = document.getElementById('mapSelectedStudents');
        const attendanceEl = document.getElementById('mapSelectedAttendance');
        const turnstilesEl = document.getElementById('mapSelectedTurnstiles');
        const districtEl = document.getElementById('mapSelectedDistrict');
        const descEl = document.getElementById('mapSelectedDesc');

        if (nameEl) nameEl.textContent = data.name;
        if (schoolsEl) schoolsEl.textContent = data.schools.toLocaleString() + " ta";
        if (studentsEl) studentsEl.textContent = data.students.toLocaleString() + " nafar";
        if (attendanceEl) attendanceEl.textContent = data.attendance;
        if (turnstilesEl) turnstilesEl.textContent = data.turnstiles.toLocaleString() + " ta yo'lak";
        if (districtEl) districtEl.textContent = data.topDistrict;
        if (descEl) descEl.textContent = data.desc;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.uzbekistanMap = new UzbekistanMapController();
});
