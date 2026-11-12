/**
 * EDUGATE Uzbekistan 12 Viloyat Interactive Regional Telemetry Radar
 * Real-time monitoring metrics across all 12 regions of Uzbekistan.
 */

const UzbekistanRegionsData = {
    andijan: { 
        name: "Andijon viloyati", 
        schools: 780, 
        students: 510000, 
        attendance: "98.3%", 
        turnstiles: 2300, 
        topDistrict: "Andijon sh. (99.1%)",
        desc: "Farg'ona vodiysining eng zich aholiga ega hududi, 780 ta umumta'lim maktabida Face ID tizimi to'liq joriy etilgan."
    },
    bukhara: { 
        name: "Buxoro viloyati", 
        schools: 540, 
        students: 360000, 
        attendance: "98.7%", 
        turnstiles: 1650, 
        topDistrict: "Buxoro sh. (99.4%)",
        desc: "Tarixiy va ta'lim salohiyati yuqori hudud, davomat barqarorligi bo'yicha respublikada yetakchi 3 talikda."
    },
    fergana: { 
        name: "Farg'ona viloyati", 
        schools: 960, 
        students: 640000, 
        attendance: "98.6%", 
        turnstiles: 2850, 
        topDistrict: "Farg'ona sh. (99.2%)",
        desc: "Keng qamrovli maktablar tarmog'i, 960 ta maktab yagona monitoring markaziga optik tolali VPN orqali bog'langan."
    },
    jizzakh: { 
        name: "Jizzax viloyati", 
        schools: 550, 
        students: 310000, 
        attendance: "98.0%", 
        turnstiles: 1400, 
        topDistrict: "Jizzax sh. (98.8%)",
        desc: "Tog'li va dasht tumanlaridagi barcha maktablar uzluksiz SmartUPS batareyalari bilan ta'minlangan."
    },
    khorezm: { 
        name: "Xorazm viloyati", 
        schools: 530, 
        students: 340000, 
        attendance: "98.5%", 
        turnstiles: 1550, 
        topDistrict: "Urganch sh. (99.0%)",
        desc: "Xiva va Urganch shaharlari hamda barcha tuman maktablari to'liq biometrik ro'yxatdan o'tkazilgan."
    },
    namangan: { 
        name: "Namangan viloyati", 
        schools: 710, 
        students: 490000, 
        attendance: "98.2%", 
        turnstiles: 2100, 
        topDistrict: "Namangan sh. (98.9%)",
        desc: "Ota-onalarga oniy Telegram xabarnoma yetkazish darajasi 99.4% ni tashkil qiladi."
    },
    navoi: { 
        name: "Navoiy viloyati", 
        schools: 360, 
        students: 220000, 
        attendance: "98.8%", 
        turnstiles: 1100, 
        topDistrict: "Navoiy sh. (99.5%)",
        desc: "Sanoat va konchilik shaharlarida eng yuqori intizom ko'rsatkichlari qayd etilmoqda."
    },
    kashkadarya: { 
        name: "Qashqadaryo viloyati", 
        schools: 1180, 
        students: 690000, 
        attendance: "97.9%", 
        turnstiles: 3100, 
        topDistrict: "Qarshi sh. (98.6%)",
        desc: "Eng ko'p maktab soniga ega viloyat, 1,180 ta maktab bo'yicha markaziy MMTV nazorati o'rnatilgan."
    },
    samarkand: { 
        name: "Samarqand viloyati", 
        schools: 1250, 
        students: 780000, 
        attendance: "98.4%", 
        turnstiles: 3400, 
        topDistrict: "Samarqand sh. (99.2%)",
        desc: "Respublika bo'yicha eng yirik ta'lim kontingenti: 780,000 nafar o'quvchi biometrik reyestrga kiritilgan."
    },
    sirdarya: { 
        name: "Sirdaryo viloyati", 
        schools: 310, 
        students: 180000, 
        attendance: "98.2%", 
        turnstiles: 920, 
        topDistrict: "Guliston sh. (98.7%)",
        desc: "Ixcham va yuqori tezlikda boshqariladigan hududiy infratuzilma, 100% raqamlashgan davomat jurnali."
    },
    surkhandarya: { 
        name: "Surxondaryo viloyati", 
        schools: 948, 
        students: 580000, 
        attendance: "98.4%", 
        turnstiles: 2800, 
        topDistrict: "Termiz sh. (99.3%)",
        desc: "Termiz shahri va 14 ta tumandagi barcha 948 ta maktab Milliy Gvardiya xulosasi bilan to'liq jihozlangan."
    },
    tashkent_region: { 
        name: "Toshkent viloyati", 
        schools: 890, 
        students: 540000, 
        attendance: "98.1%", 
        turnstiles: 2600, 
        topDistrict: "Chirchiq sh. (98.8%)",
        desc: "Poytaxt viloyati bo'ylab 890 ta maktabda yagona markaziy xavfsizlik va davomat ekotizimi faoliyat yuritmoqda."
    }
};

class UzbekistanMapController {
    constructor() {
        this.currentRegion = 'surkhandarya';
        this.init();
    }

    init() {
        const regionButtons = document.querySelectorAll('[data-region]');
        regionButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const regKey = e.currentTarget.getAttribute('data-region');
                this.selectRegion(regKey);
            });
        });
        this.selectRegion(this.currentRegion);
    }

    selectRegion(key) {
        const data = UzbekistanRegionsData[key];
        if (!data) return;
        this.currentRegion = key;

        // Active class update on buttons
        document.querySelectorAll('[data-region]').forEach(b => {
            if (b.getAttribute('data-region') === key) {
                b.classList.add('border-cyan-400', 'bg-cyan-950/60', 'text-cyan-300', 'shadow-[0_0_15px_rgba(6,182,212,0.35)]');
                b.classList.remove('border-slate-800', 'bg-slate-900/70', 'text-white');
            } else {
                b.classList.remove('border-cyan-400', 'bg-cyan-950/60', 'text-cyan-300', 'shadow-[0_0_15px_rgba(6,182,212,0.35)]');
                b.classList.add('border-slate-800', 'bg-slate-900/70', 'text-white');
            }
        });

        // DOM elements
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
