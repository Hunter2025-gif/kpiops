document.addEventListener('DOMContentLoaded', function() {
    // Production by Product Type Chart
    if (document.getElementById('productTypeChart')) {
        const productTypeCtx = document.getElementById('productTypeChart').getContext('2d');
        const productTypeChart = new Chart(productTypeCtx, {
            type: 'doughnut',
            data: {
                labels: ['Tablets', 'Capsules', 'Ointments'],
                datasets: [{
                    data: [productData.tablets || 5, productData.capsules || 3, productData.ointments || 2],
                    backgroundColor: [
                        'rgba(54, 162, 235, 0.8)',
                        'rgba(255, 99, 132, 0.8)',
                        'rgba(75, 192, 192, 0.8)'
                    ],
                    borderColor: [
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 99, 132, 1)',
                        'rgba(75, 192, 192, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    },
                    title: {
                        display: true,
                        text: 'Production by Product Type',
                        font: {
                            size: 16
                        }
                    }
                }
            }
        });
    }

    // Phase Status Chart
    if (document.getElementById('phaseStatusChart')) {
        const phaseStatusCtx = document.getElementById('phaseStatusChart').getContext('2d');
        const phaseStatusChart = new Chart(phaseStatusCtx, {
            type: 'bar',
            data: {
                labels: ['Mixing', 'Drying', 'Granulation', 'Compression', 'Packing'],
                datasets: [{
                    label: 'Completed',
                    data: [
                        phaseData.mixing_completed || 12,
                        phaseData.drying_completed || 10,
                        phaseData.granulation_completed || 8,
                        phaseData.compression_completed || 7,
                        phaseData.packing_completed || 6
                    ],
                    backgroundColor: 'rgba(75, 192, 192, 0.8)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1
                }, {
                    label: 'In Progress',
                    data: [
                        phaseData.mixing_inprogress || 3,
                        phaseData.drying_inprogress || 4,
                        phaseData.granulation_inprogress || 2,
                        phaseData.compression_inprogress || 3,
                        phaseData.packing_inprogress || 5
                    ],
                    backgroundColor: 'rgba(54, 162, 235, 0.8)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Number of Batches'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Production Phases'
                        }
                    }
                },
                plugins: {
                    legend: {
                        position: 'bottom'
                    },
                    title: {
                        display: true,
                        text: 'Phase Completion Status',
                        font: {
                            size: 16
                        }
                    }
                }
            }
        });
    }

    // Weekly Production Trend Chart
    if (document.getElementById('weeklyTrendChart')) {
        const weeklyTrendCtx = document.getElementById('weeklyTrendChart').getContext('2d');
        const weeklyTrendChart = new Chart(weeklyTrendCtx, {
            type: 'line',
            data: {
                labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
                datasets: [{
                    label: 'Batches Started',
                    data: [weeklyData.started_week1 || 8, weeklyData.started_week2 || 12, weeklyData.started_week3 || 10, weeklyData.started_week4 || 14],
                    borderColor: 'rgba(54, 162, 235, 1)',
                    backgroundColor: 'rgba(54, 162, 235, 0.1)',
                    borderWidth: 2,
                    tension: 0.4,
                    fill: true
                }, {
                    label: 'Batches Completed',
                    data: [weeklyData.completed_week1 || 6, weeklyData.completed_week2 || 10, weeklyData.completed_week3 || 8, weeklyData.completed_week4 || 11],
                    borderColor: 'rgba(75, 192, 192, 1)',
                    backgroundColor: 'rgba(75, 192, 192, 0.1)',
                    borderWidth: 2,
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Number of Batches'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Weeks'
                        }
                    }
                },
                plugins: {
                    legend: {
                        position: 'bottom'
                    },
                    title: {
                        display: true,
                        text: 'Weekly Production Trend',
                        font: {
                            size: 16
                        }
                    }
                }
            }
        });
    }

    // Quality Control Pass/Fail Chart
    if (document.getElementById('qcStatusChart')) {
        const qcStatusCtx = document.getElementById('qcStatusChart').getContext('2d');
        const qcStatusChart = new Chart(qcStatusCtx, {
            type: 'pie',
            data: {
                labels: ['Passed', 'Failed', 'Pending'],
                datasets: [{
                    data: [qcData.passed || 85, qcData.failed || 5, qcData.pending || 10],
                    backgroundColor: [
                        'rgba(75, 192, 192, 0.8)',
                        'rgba(255, 99, 132, 0.8)',
                        'rgba(255, 205, 86, 0.8)'
                    ],
                    borderColor: [
                        'rgba(75, 192, 192, 1)',
                        'rgba(255, 99, 132, 1)',
                        'rgba(255, 205, 86, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    },
                    title: {
                        display: true,
                        text: 'Quality Control Status',
                        font: {
                            size: 16
                        }
                    }
                }
            }
        });
    }
});
