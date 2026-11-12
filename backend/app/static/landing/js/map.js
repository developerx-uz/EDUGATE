/**
 * EDUGATE Uzbekistan Regional Interactive Attendance Map
 * Renders statistical metrics across all 14 administrative divisions of Uzbekistan.
 */

const UzbekistanRegionsData = {
    tashkent_city: { name: "Toshkent shahri", schools: 384, students: 485000, attendance: "98.9%", turnstiles: 1420 },
    tashkent_region: { name: "Toshkent viloyati", schools: 890, students: 540000, attendance: "98.1%", turnstiles: 2600 },
    samarkand: { name: "Samarqand viloyati", schools: 1250, students: 780000, attendance: "98.4%", turnstiles: 3400 },
    fergana: { name: "Farg'ona viloyati", schools: 960, students: 640000, attendance: "98.6%", turnstiles: 2850 },
    andijan: { name: "Andijon viloyati", schools: 780, students: 510000, attendance: "98.3%", turnstiles: 2300 },
    namangan: { name: "Namangan viloyati", schools: 710, students: 490000, attendance: "98.2%", turnstiles: 2100 },
    bukhara: { name: "Buxoro viloyati", schools: 540, students: 360000, attendance: "98.7%", turnstiles: 1650 },
    kashkadarya: { name: "Qashqadaryo viloyati", schools: 1180, students: 690000, attendance: "97.9%", turnstiles: 3100 },
    surkhandarya: { name: "Surxondaryo viloyati", schools: 948, students: 580000, attendance: "98.4%", turnstiles: 2800 },
    khorezm: { name: "Xorazm viloyati", schools: 530, students: 340000, attendance: "98.5%", turnstiles: 1550 },
    navoi: { name: "Navoiy viloyati", schools: 360, students: 220000, attendance: "98.8%", turnstiles: 1100 },
    jizzakh: { name: "Jizzax viloyati", schools: 550, students: 310000, attendance: "98.0%", turnstiles: 1400 },
    sirdarya: { name: "Sirdaryo viloyati", schools: 310, students: 180000, attendance: "98.2%", turnstiles: 920 },
    karakalpakstan: { name: "Qoraqalpog'iston Resp.", schools: 720, students: 390000, attendance: "97.8%", turnstiles: 1950 }
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

        // Active class update
        document.querySelectorAll('[data-region]').forEach(b => {
            if (b.getAttribute('data-region') === key) {
                b.classList.add('bg-cyan-500/20', 'border-cyan-400', 'text-cyan-300');
                b.classList.remove('bg-slate-800/60', 'border-slate-700/60', 'text-slate-300');
            } else {
                b.classList.remove('bg-cyan-500/20', 'border-cyan-400', 'text-cyan-300');
                b.classList.add('bg-slate-800/60', 'border-slate-700/60', 'text-slate-300');
            }
        });

        // DOM elements
        const nameEl = document.getElementById('mapSelectedRegionName');
        const schoolsEl = document.getElementById('mapSelectedSchools');
        const studentsEl = document.getElementById('mapSelectedStudents');
        const attendanceEl = document.getElementById('mapSelectedAttendance');
        const turnstilesEl = document.getElementById('mapSelectedTurnstiles');

        if (nameEl) nameEl.textContent = data.name;
        if (schoolsEl) schoolsEl.textContent = data.schools.toLocaleString() + " ta";
        if (studentsEl) studentsEl.textContent = data.students.toLocaleString() + " nafar";
        if (attendanceEl) attendanceEl.textContent = data.attendance;
        if (turnstilesEl) turnstilesEl.textContent = data.turnstiles.toLocaleString() + " ta yo'lak";
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.uzbekistanMap = new UzbekistanMapController();
});
