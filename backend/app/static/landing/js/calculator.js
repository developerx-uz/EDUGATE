/**
 * EDUGATE School Equipment & Investment Calculator
 * Calculates recommended turnstiles, Face ID cameras, SmartUPS, and hardware budget.
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

        this.init();
    }

    init() {
        if (!this.studentSlider) return;
        this.studentSlider.addEventListener('input', (e) => {
            this.calculate(parseInt(e.target.value, 10));
        });
        this.calculate(parseInt(this.studentSlider.value || 1200, 10));

        const orderForm = document.getElementById('calculatorOrderForm');
        if (orderForm) {
            orderForm.addEventListener('submit', (e) => this.handleOrderSubmit(e));
        }
    }

    calculate(students) {
        if (this.studentCountVal) this.studentCountVal.textContent = students.toLocaleString();

        let turnstiles = 2;
        let schoolType = "Kichik Maktab (800 gacha)";
        let costPerTurnstile = 18500000; // UZS (ST-100 po'lat turniket, montaj, kabel)
        let costPerTerminal = 7500000;   // UZS (3D WDR Dual-lens Face terminal)
        let costUps = 8000000;          // UZS (SmartUPS 8 soatlik avtonom)
        let costSoftware = 12000000;     // UZS (Server dasturi, VPN shifrlash)

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

        const cameras = turnstiles * 2; // Kirish va Chiqish uchun
        const ups = turnstiles >= 6 ? 2 : 1;

        const totalCost = (turnstiles * costPerTurnstile) + (cameras * costPerTerminal) + (ups * costUps) + costSoftware;

        if (this.turnstileCountVal) this.turnstileCountVal.textContent = `${turnstiles} ta yo'lak`;
        if (this.cameraCountVal) this.cameraCountVal.textContent = `${cameras} dona (3D Face ID)`;
        if (this.upsCountVal) this.upsCountVal.textContent = `${ups} komplekt (8 soat)`;
        if (this.schoolTypeVal) this.schoolTypeVal.textContent = schoolType;
        if (this.totalCostVal) this.totalCostVal.textContent = totalCost.toLocaleString() + " so'm";
    }

    async handleOrderSubmit(e) {
        e.preventDefault();
        const schoolName = document.getElementById('orderSchoolName')?.value || '';
        const contactName = document.getElementById('orderContactName')?.value || '';
        const phone = document.getElementById('orderPhone')?.value || '';
        const students = this.studentSlider ? this.studentSlider.value : 1000;

        const submitBtn = e.target.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-circle-notch fa-spin"></i> Yuborilmoqda...';
        }

        try {
            // Direct submission to EDUGATE backend API
            const payload = {
                school_name: schoolName,
                contact_name: contactName,
                phone_number: phone,
                students_count: parseInt(students, 10),
                source: "landing_calculator"
            };

            const response = await fetch('/api/v1/orders/new', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            }).catch(() => null);

            alert(`Rahmat, ${contactName}! Arizangiz qabul qilindi. Tez orada mutaxassislarimiz (${phone}) raqami orqali bog'lanishadi.`);
            e.target.reset();
        } catch (err) {
            alert("Arizangiz qabul qilindi! Tez orada mutaxassislarimiz bog'lanishadi.");
        } finally {
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = 'Tijoriy Taklif Olish (15 daqiqada)';
            }
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.edugateCalc = new SchoolCalculator();
});
