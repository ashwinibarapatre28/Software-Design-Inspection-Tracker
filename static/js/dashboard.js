document.addEventListener('DOMContentLoaded', function() {
    fetch('/analytics/data')
        .then(res => res.json())
        .then(data => {
            // 1. Severity Distribution Chart (Doughnut)
            const sevCtx = document.getElementById('severityChart');
            if (sevCtx) {
                new Chart(sevCtx, {
                    type: 'doughnut',
                    data: {
                        labels: data.severity.labels,
                        datasets: [{
                            data: data.severity.data,
                            backgroundColor: ['#ef4444', '#f97316', '#eab308', '#3b82f6', '#64748b'],
                            borderWidth: 2,
                            borderColor: '#ffffff'
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: { position: 'bottom', labels: { font: { family: 'Inter', size: 12 } } }
                        },
                        cutout: '68%'
                    }
                });
            }

            // 2. Category Distribution Chart (Horizontal Bar)
            const catCtx = document.getElementById('categoryChart');
            if (catCtx) {
                new Chart(catCtx, {
                    type: 'bar',
                    data: {
                        labels: data.category.labels,
                        datasets: [{
                            label: 'Defects Count',
                            data: data.category.data,
                            backgroundColor: '#4f46e5',
                            borderRadius: 6
                        }]
                    },
                    options: {
                        indexAxis: 'y',
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: { display: false }
                        },
                        scales: {
                            x: { grid: { color: '#f1f5f9' }, ticks: { stepSize: 1 } },
                            y: { grid: { display: false } }
                        }
                    }
                });
            }

            // 3. Status Distribution Chart (Pie)
            const statusCtx = document.getElementById('statusChart');
            if (statusCtx) {
                new Chart(statusCtx, {
                    type: 'pie',
                    data: {
                        labels: data.status.labels,
                        datasets: [{
                            data: data.status.data,
                            backgroundColor: ['#8b5cf6', '#3b82f6', '#0284c7', '#10b981', '#f59e0b', '#64748b', '#ef4444'],
                            borderWidth: 2,
                            borderColor: '#ffffff'
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: { position: 'bottom', labels: { font: { family: 'Inter', size: 11 } } }
                        }
                    }
                });
            }

            // 4. Project Comparison Chart (Bar)
            const projectCtx = document.getElementById('projectChart');
            if (projectCtx) {
                new Chart(projectCtx, {
                    type: 'bar',
                    data: {
                        labels: data.project.labels,
                        datasets: [{
                            label: 'Total Defects',
                            data: data.project.data,
                            backgroundColor: '#6366f1',
                            borderRadius: 8
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: { display: false }
                        },
                        scales: {
                            y: { beginAtZero: true, ticks: { stepSize: 1 } }
                        }
                    }
                });
            }
        })
        .catch(err => console.error('Error loading chart data:', err));
});
