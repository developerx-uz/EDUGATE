/**
 * EDUGATE Charts Manager
 * Initializes and updates real Chart.js charts using live backend data.
 */
const EdugateCharts = {
    attendanceChart: null,
    weeklyChart: null,

    init(todayStats = {}, weeklyData = []) {
        this.initAttendanceChart(todayStats);
        this.initWeeklyChart(weeklyData);
    },

    initAttendanceChart(stats = {}) {
        const ctx = document.getElementById('attendanceChart');
        if (!ctx) return;

        const onTime = stats.today_ontime || 0;
        const late = stats.today_lates || 0;
        const total = stats.students_count || (onTime + late) || 1;
        const absent = Math.max(0, total - (onTime + late));

        // If no records yet, show clean zero state representation
        const chartData = (onTime === 0 && late === 0 && absent === 0) 
            ? [0, 0, 1] 
            : [onTime, late, absent];

        if (this.attendanceChart) {
            this.attendanceChart.destroy();
        }

        this.attendanceChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ["O'z vaqtida", 'Kechikkan', 'Kelmagan'],
                datasets: [{
                    data: chartData,
                    backgroundColor: ['#10b981', '#f59e0b', '#ef4444'],
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
                            color: '#94a3b8',
                            font: { size: 11, family: 'Plus Jakarta Sans' },
                            padding: 16,
                            usePointStyle: true,
                            pointStyleWidth: 8
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
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
                        label: "O'z vaqtida",
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
                        label: 'Kechikkan',
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
                        grid: { color: 'rgba(51,65,85,0.2)' },
                        ticks: { color: '#94a3b8', font: { size: 11, family: 'Plus Jakarta Sans' } }
                    },
                    y: {
                        beginAtZero: true,
                        grid: { color: 'rgba(51,65,85,0.2)' },
                        ticks: { color: '#94a3b8', font: { size: 11, family: 'Plus Jakarta Sans' }, precision: 0 }
                    }
                },
                plugins: {
                    legend: {
                        labels: {
                            color: '#94a3b8',
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
            const total = todayStats.students_count || (onTime + late) || 1;
            const absent = Math.max(0, total - (onTime + late));

            this.attendanceChart.data.datasets[0].data = [onTime, late, absent];
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
