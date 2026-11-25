/**
 * EDUGATE Charts Manager
 * Initializes and updates real Chart.js charts using live backend data.
 */
const EdugateCharts = {
    attendanceChart: null,
    weeklyChart: null,

    getTextColor() {
        return document.documentElement.classList.contains('light') ? '#525252' : '#a3a3a3';
    },

    getGridColor() {
        return document.documentElement.classList.contains('light') ? 'rgba(0, 0, 0, 0.06)' : 'rgba(255, 255, 255, 0.06)';
    },

    setTheme(theme) {
        const textColor = (theme === 'light') ? '#525252' : '#a3a3a3';
        const gridColor = (theme === 'light') ? 'rgba(0, 0, 0, 0.06)' : 'rgba(255, 255, 255, 0.06)';

        if (this.attendanceChart && this.attendanceChart.options) {
            if (this.attendanceChart.options.plugins?.legend?.labels) {
                this.attendanceChart.options.plugins.legend.labels.color = textColor;
            }
            this.attendanceChart.update();
        }

        if (this.weeklyChart && this.weeklyChart.options) {
            if (this.weeklyChart.options.scales?.x) {
                this.weeklyChart.options.scales.x.ticks.color = textColor;
                this.weeklyChart.options.scales.x.grid.color = gridColor;
            }
            if (this.weeklyChart.options.scales?.y) {
                this.weeklyChart.options.scales.y.ticks.color = textColor;
                this.weeklyChart.options.scales.y.grid.color = gridColor;
            }
            if (this.weeklyChart.options.plugins?.legend?.labels) {
                this.weeklyChart.options.plugins.legend.labels.color = textColor;
            }
            this.weeklyChart.update();
        }
    },

    init(todayStats = {}, weeklyData = []) {
        if (typeof Chart === 'undefined') return;
        this.initAttendanceChart(todayStats);
        this.initWeeklyChart(weeklyData);
    },

    initAttendanceChart(stats = {}) {
        const ctx = document.getElementById('attendanceChart');
        if (!ctx) return;

        const onTime = stats.today_ontime || 0;
        const late = stats.today_lates || 0;
        const total = stats.students_count || 0;
        const absent = Math.max(0, total - (onTime + late));

        const hasRealData = (onTime > 0 || late > 0 || total > 0);
        const chartData = hasRealData ? [onTime, late, absent] : [1];
        const chartLabels = hasRealData 
            ? ["O'z vaqtida", "Kechikkan", "Kelmagan"] 
            : ["Davomat signallari kutilmoqda"];
        const chartColors = hasRealData 
            ? ['#10b981', '#f59e0b', '#ef4444'] 
            : ['#1f1f1f'];

        if (this.attendanceChart) {
            this.attendanceChart.destroy();
        }

        this.attendanceChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: chartLabels,
                datasets: [{
                    data: chartData,
                    backgroundColor: chartColors,
                    borderWidth: 0,
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '72%',
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: this.getTextColor(),
                            font: { size: 11, family: 'Plus Jakarta Sans' },
                            padding: 16,
                            usePointStyle: true,
                            pointStyleWidth: 8
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                if (!hasRealData) return " Hozircha qaydlar yo'q";
                                return ` ${context.label}: ${context.raw} ta`;
                            }
                        }
                    }
                }
            }
        });
    },

    initWeeklyChart(weeklyData = []) {
        const ctx = document.getElementById('weeklyChart');
        if (!ctx) return;

        let labels = ['Dush', 'Sesh', 'Chor', 'Pay', 'Jum', 'Shan', 'Yak'];
        let onTimeData = [0, 0, 0, 0, 0, 0, 0];
        let lateData = [0, 0, 0, 0, 0, 0, 0];

        if (Array.isArray(weeklyData) && weeklyData.length > 0) {
            labels = weeklyData.map(d => d.day_name || d.date);
            onTimeData = weeklyData.map(d => d.on_time || 0);
            lateData = weeklyData.map(d => d.late || 0);
        }

        if (this.weeklyChart) {
            this.weeklyChart.destroy();
        }

        this.weeklyChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: "O'z vaqtida kirishlar",
                        data: onTimeData,
                        borderColor: '#10b981',
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        fill: true,
                        tension: 0.35,
                        borderWidth: 2,
                        pointRadius: 4,
                        pointBackgroundColor: '#10b981'
                    },
                    {
                        label: 'Kechikkanlar',
                        data: lateData,
                        borderColor: '#f59e0b',
                        backgroundColor: 'rgba(245, 158, 11, 0.1)',
                        fill: true,
                        tension: 0.35,
                        borderWidth: 2,
                        pointRadius: 4,
                        pointBackgroundColor: '#f59e0b'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        grid: { color: this.getGridColor() },
                        ticks: { color: this.getTextColor(), font: { size: 11, family: 'Plus Jakarta Sans' } }
                    },
                    y: {
                        beginAtZero: true,
                        grid: { color: this.getGridColor() },
                        ticks: { color: this.getTextColor(), font: { size: 11, family: 'Plus Jakarta Sans' }, precision: 0 }
                    }
                },
                plugins: {
                    legend: {
                        labels: {
                            color: this.getTextColor(),
                            font: { size: 11, family: 'Plus Jakarta Sans' },
                            usePointStyle: true,
                            pointStyleWidth: 8
                        }
                    }
                }
            }
        });
    },

    update(todayStats = {}, weeklyData = []) {
        if (this.attendanceChart) {
            const onTime = todayStats.today_ontime || 0;
            const late = todayStats.today_lates || 0;
            const total = todayStats.students_count || 0;
            const absent = Math.max(0, total - (onTime + late));

            const hasRealData = (onTime > 0 || late > 0 || total > 0);
            this.attendanceChart.data.labels = hasRealData ? ["O'z vaqtida", "Kechikkan", "Kelmagan"] : ["Davomat signallari kutilmoqda"];
            this.attendanceChart.data.datasets[0].data = hasRealData ? [onTime, late, absent] : [1];
            this.attendanceChart.data.datasets[0].backgroundColor = hasRealData ? ['#10b981', '#f59e0b', '#ef4444'] : ['#1f1f1f'];
            this.attendanceChart.update();
        }

        if (this.weeklyChart && Array.isArray(weeklyData) && weeklyData.length > 0) {
            this.weeklyChart.data.labels = weeklyData.map(d => d.day_name || d.date);
            this.weeklyChart.data.datasets[0].data = weeklyData.map(d => d.on_time || 0);
            this.weeklyChart.data.datasets[1].data = weeklyData.map(d => d.late || 0);
            this.weeklyChart.update();
        }
    }
};

window.EdugateCharts = EdugateCharts;

