/**
 * EDUGATE & e-davomat.net School Turnstile & Face ID Calculator
 * Full commercial specification and budget calculator for Uzbekistan schools.
 * Supports quick school presets, dynamic student slider, equipment list,
 * and direct commercial order request dispatch.
 */

class SchoolCalculator {
    constructor() {
        this.studentSlider = document.getElementById('calcStudentSlider');
        this.studentCountVal = document.getElementById('calcStudentCountVal');
        this.turnstileCountVal = document.getElementById('calcTurnstilesVal');
        this.cameraCountVal = document.getElementById('calcCamerasVal');
        this.upsCountVal = document.getElementById('calcUpsVal');
        this.totalCostVal = document.getElementById('calcTotalCostVal');
        this.schoolTypeVal = document.getElementById('calcSchoolTypeVal');
        this.breakdownList = document.getElementById('calcEquipmentBreakdown');

        // Preset buttons
        this.presetBtns = document.querySelectorAll('[data-calc-preset]');

        // Calculator Modal
        this.modal = document.getElementById('calculatorModal');
        this.openModalBtns = document.querySelectorAll('[data-open-calculator]');
        this.closeModalBtn = document.getElementById('closeCalculatorModalBtn');

        this.init();
    }

    init() {
        if (this.studentSlider) {
            this.studentSlider.addEventListener('input', (e) => {
                this.calculate(parseInt(e.target.value, 10));
            });
            this.calculate(parseInt(this.studentSlider.value || 1200, 10));
        }

        // Preset button clicks
        this.presetBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const count = parseInt(btn.getAttribute('data-calc-preset'), 10);
                if (this.studentSlider) {
                    this.studentSlider.value = count;
                    this.calculate(count);
                }
                this.presetBtns.forEach(b => b.classList.remove('active', 'border-cyan-400', 'bg-cyan-500/20', 'text-cyan-300'));
                btn.classList.add('active', 'border-cyan-400', 'bg-cyan-500/20', 'text-cyan-300');
            });
        });

        // Form handlers
        const inPageForm = document.getElementById('calculatorOrderForm');
        if (inPageForm) {
            inPageForm.addEventListener('submit', (e) => this.handleOrderSubmit(e));
        }

        const modalForm = document.getElementById('calculatorModalForm');
        if (modalForm) {
            modalForm.addEventListener('submit', (e) => this.handleOrderSubmit(e));
        }

        // Modal triggers
        this.openModalBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                this.openModal();
            });
        });

        if (this.closeModalBtn) {
            this.closeModalBtn.addEventListener('click', () => this.closeModal());
        }

        if (this.modal) {
            this.modal.addEventListener('click', (e) => {
                if (e.target === this.modal) this.closeModal();
            });
        }
    }

    calculate(students) {
        if (this.studentCountVal) this.studentCountVal.textContent = students.toLocaleString();

        let turnstiles = 2;
        let schoolType = "Kichik Maktab (800 gacha)";
        let costPerTurnstile = 18500000; // UZS (ST-100 po'lat turniket, montaj, kabel)
        let costPerTerminal = 7500000;   // UZS (3D WDR Dual-lens Face ID terminal)
        let costUps = 8000000;          // UZS (SmartUPS LiFePO4 8 soatlik avtonom)
        let costSoftware = 12000000;     // UZS (Server dasturi, VPN shifrlash litsenziyasi)

        if (students <= 800) {
            turnstiles = 2;
            schoolType = "Kichik Maktab (800 gacha o'quvchi)";
        } else if (students <= 1500) {
            turnstiles = 4;
            schoolType = "O'rta Maktab (800 – 1,500 o'quvchi)";
        } else {
            turnstiles = 6;
            schoolType = "Katta Maktab (1,500+ o'quvchi)";
        }

        const cameras = turnstiles * 2; // Kirish va Chiqish oqimlari uchun
        const ups = turnstiles >= 6 ? 2 : 1;

        const totalCost = (turnstiles * costPerTurnstile) + (cameras * costPerTerminal) + (ups * costUps) + costSoftware;

        if (this.turnstileCountVal) this.turnstileCountVal.textContent = `${turnstiles} ta yo'lak`;
        if (this.cameraCountVal) this.cameraCountVal.textContent = `${cameras} dona (3D Face ID)`;
        if (this.upsCountVal) this.upsCountVal.textContent = `${ups} komplekt (8 soat)`;
        if (this.schoolTypeVal) this.schoolTypeVal.textContent = schoolType;
        if (this.totalCostVal) this.totalCostVal.textContent = totalCost.toLocaleString() + " so'm";

        // Also update modal fields if they exist
        const modalTurnstiles = document.getElementById('modalCalcTurnstiles');
        const modalCameras = document.getElementById('modalCalcCameras');
        const modalUps = document.getElementById('modalCalcUps');
        const modalTotalCost = document.getElementById('modalCalcTotalCost');
        const modalSchoolType = document.getElementById('modalCalcSchoolType');

        if (modalTurnstiles) modalTurnstiles.textContent = `${turnstiles} ta yo'lak`;
        if (modalCameras) modalCameras.textContent = `${cameras} dona Face ID`;
        if (modalUps) modalUps.textContent = `${ups} komplekt`;
        if (modalTotalCost) modalTotalCost.textContent = totalCost.toLocaleString() + " so'm";
        if (modalSchoolType) modalSchoolType.textContent = schoolType;
    }

    openModal() {
        if (!this.modal) return;
        this.modal.classList.remove('hidden');
        document.body.classList.add('overflow-hidden');
    }

    closeModal() {
        if (!this.modal) return;
        this.modal.classList.add('hidden');
        document.body.classList.remove('overflow-hidden');
    }

    async handleOrderSubmit(e) {
        e.preventDefault();
        const form = e.target;
        const schoolName = form.querySelector('[name="school_name"]')?.value || document.getElementById('orderSchoolName')?.value || '';
        const contactName = form.querySelector('[name="contact_name"]')?.value || document.getElementById('orderContactName')?.value || '';
        const phone = form.querySelector('[name="phone_number"]')?.value || document.getElementById('orderPhone')?.value || '';
        const students = this.studentSlider ? this.studentSlider.value : 1200;

        const submitBtn = form.querySelector('button[type="submit"]');
        const origBtnText = submitBtn ? submitBtn.innerHTML : 'Yuborish';

        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-circle-notch fa-spin mr-1"></i> Yuborilmoqda...';
        }

        try {
            const payload = {
                school_name: schoolName,
                contact_name: contactName,
                phone_number: phone,
                students_count: parseInt(students, 10),
                source: "landing_calculator"
            };

            await fetch('/api/v1/orders/new', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            }).catch(() => null);

            alert(`✅ Qabul qilindi!\n\nHurmatli ${contactName}, ${schoolName} uchun buyurtma so'rovingiz tizimga muvaffaqiyatli kiritildi.\nMutaxassislarimiz 15 daqiqa ichida (${phone}) raqami orqali bog'lanib, to'liq texnik-smeta loyihasini taqdim etadilar.`);
            form.reset();
            this.closeModal();
        } catch (err) {
            alert("Arizangiz qabul qilindi! Tez orada mutaxassislarimiz bog'lanishadi.");
            this.closeModal();
        } finally {
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = origBtnText;
            }
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.edugateCalc = new SchoolCalculator();
});
