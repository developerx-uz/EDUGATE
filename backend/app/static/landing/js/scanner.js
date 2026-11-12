/**
 * EDUGATE Face ID Scanner Simulation Engine
 * Handles real-time landmark triangulation, liveness check simulation, and turnstile actuation.
 */

class FaceIDScannerSimulator {
    constructor() {
        this.canvas = document.getElementById('faceLandmarksCanvas');
        this.ctx = this.canvas ? this.canvas.getContext('2d') : null;
        this.students = [
            { name: "Eshboyev Farhod", class: "10-A sinf", school: "101-IDUM", time: "07:48:12", score: 99.87 },
            { name: "Karimova Madina", class: "8-B sinf", school: "101-IDUM", time: "07:51:30", score: 99.94 },
            { name: "Zokirov Jasur", class: "11-A sinf", school: "101-IDUM", time: "07:54:05", score: 99.72 },
            { name: "Rahimova Shahlo", class: "9-V sinf", school: "101-IDUM", time: "07:57:44", score: 99.89 }
        ];
        this.currentIndex = 0;
        this.isScanning = true;
        this.points = [];
        this.generatePoints();
        this.init();
    }

    generatePoints() {
        this.points = [];
        const basePoints = [
            {x: 0.5, y: 0.35}, // Burun uchi
            {x: 0.38, y: 0.28}, {x: 0.44, y: 0.28}, // Chap ko'z
            {x: 0.56, y: 0.28}, {x: 0.62, y: 0.28}, // O'ng ko'z
            {x: 0.36, y: 0.24}, {x: 0.44, y: 0.22}, // Chap qosh
            {x: 0.56, y: 0.22}, {x: 0.64, y: 0.24}, // O'ng qosh
            {x: 0.45, y: 0.45}, {x: 0.55, y: 0.45}, // Lab usti
            {x: 0.5, y: 0.52}, // Iyak markazi
            {x: 0.3, y: 0.35}, {x: 0.32, y: 0.45}, {x: 0.4, y: 0.55}, // Chap yanoq
            {x: 0.7, y: 0.35}, {x: 0.68, y: 0.45}, {x: 0.6, y: 0.55}  // O'ng yanoq
        ];
        this.points = basePoints;
    }

    init() {
        if (!this.canvas) return;
        this.resize();
        window.addEventListener('resize', () => this.resize());
        this.startAnimationLoop();
        this.startStudentCycle();
    }

    resize() {
        if (!this.canvas) return;
        this.canvas.width = this.canvas.parentElement.clientWidth || 400;
        this.canvas.height = this.canvas.parentElement.clientHeight || 500;
    }

    startAnimationLoop() {
        let frame = 0;
        const animate = () => {
            frame++;
            this.draw(frame);
            requestAnimationFrame(animate);
        };
        requestAnimationFrame(animate);
    }

    draw(frame) {
        if (!this.ctx || !this.canvas) return;
        const w = this.canvas.width;
        const h = this.canvas.height;
        this.ctx.clearRect(0, 0, w, h);

        const jitter = Math.sin(frame * 0.05) * 2;

        // Nuqtalarni chizish
        this.ctx.fillStyle = "#22D3EE";
        this.ctx.strokeStyle = "rgba(34, 211, 238, 0.4)";
        this.ctx.lineWidth = 1;

        const renderedPoints = this.points.map(p => ({
            x: p.x * w + Math.cos(frame * 0.08 + p.x * 10) * 1.5,
            y: p.y * h + jitter + Math.sin(frame * 0.08 + p.y * 10) * 1.5
        }));

        // Chiziqlar bilan bog'lash (Triangulyatsiya)
        this.ctx.beginPath();
        for (let i = 0; i < renderedPoints.length; i++) {
            for (let j = i + 1; j < renderedPoints.length; j++) {
                const dist = Math.hypot(renderedPoints[i].x - renderedPoints[j].x, renderedPoints[i].y - renderedPoints[j].y);
                if (dist < w * 0.16) {
                    this.ctx.moveTo(renderedPoints[i].x, renderedPoints[i].y);
                    this.ctx.lineTo(renderedPoints[j].x, renderedPoints[j].y);
                }
            }
        }
        this.ctx.stroke();

        // Biometrik nuqtalar
        for (let p of renderedPoints) {
            this.ctx.beginPath();
            this.ctx.arc(p.x, p.y, 2.5, 0, Math.PI * 2);
            this.ctx.fill();
        }
    }

    startStudentCycle() {
        setInterval(() => {
            this.currentIndex = (this.currentIndex + 1) % this.students.length;
            const student = this.students[this.currentIndex];

            const nameEl = document.getElementById('scanStudentName');
            const classEl = document.getElementById('scanStudentClass');
            const speedEl = document.getElementById('scanSpeedScore');
            const turnstileEl = document.getElementById('scanTurnstileStatus');
            const telegramAlert = document.getElementById('scanTelegramPopup');

            if (nameEl) nameEl.textContent = student.name;
            if (classEl) classEl.textContent = student.class;
            if (speedEl) speedEl.textContent = `Aniqlik: ${student.score}% (0.18s)`;
            
            if (turnstileEl) {
                turnstileEl.textContent = "Turniket Ochildi 🟢 (Kirishga ruxsat)";
                turnstileEl.classList.remove('text-amber-400');
                turnstileEl.classList.add('text-emerald-400');
            }

            if (telegramAlert) {
                telegramAlert.classList.remove('opacity-0', 'translate-y-4');
                telegramAlert.classList.add('opacity-100', 'translate-y-0');
                
                const notifText = document.getElementById('telegramNotifText');
                if (notifText) {
                    notifText.innerHTML = `Hurmatli ota-ona! Farzandingiz <b>${student.name}</b> bugun soat <b>${new Date().toLocaleTimeString()}</b> da maktabga kirdi.`;
                }

                setTimeout(() => {
                    telegramAlert.classList.remove('opacity-100', 'translate-y-0');
                    telegramAlert.classList.add('opacity-0', 'translate-y-4');
                }, 4000);
            }
        }, 6000);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.edugateScanner = new FaceIDScannerSimulator();
});

