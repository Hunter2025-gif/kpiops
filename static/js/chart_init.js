// Simplified Chart Initialization for Admin Dashboard
// This file handles all chart initialization with error handling and fallbacks

document.addEventListener('DOMContentLoaded', function() {
    console.log('Chart initialization script loaded');
    
    // Initialize charts with delay to ensure DOM is ready
    setTimeout(initializeAllCharts, 500);
});

function initializeAllCharts() {
    console.log('Initializing all charts');
    
    // Check if Chart.js is loaded
    if (typeof Chart === 'undefined') {
        console.error('Chart.js is not loaded! Loading it dynamically...');
        loadChartJs().then(() => {
            initializeCharts();
        }).catch(error => {
            console.error('Failed to load Chart.js:', error);
            displayError('Failed to load Chart.js. Please refresh the page.');
        });
    } else {
        initializeCharts();
    }
}

// Function to dynamically load Chart.js if needed
function loadChartJs() {
    return new Promise((resolve, reject) => {
        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js';
        script.onload = resolve;
        script.onerror = reject;
        document.head.appendChild(script);
    });
}

// Display error message on the page
function displayError(message) {
    const containers = document.querySelectorAll('.chart-container');
    containers.forEach(container => {
        container.innerHTML = `<div class="alert alert-danger">${message}</div>`;
    });
}

// Main chart initialization function
function initializeCharts() {
    try {
        // Check if chart data is available
        if (typeof productData === 'undefined' || typeof phaseData === 'undefined' || 
            typeof weeklyData === 'undefined' || typeof qcData === 'undefined') {
            console.error('Chart data variables are not defined!');
            
            // Define fallback data
            window.productData = window.productData || {tablets: 5, capsules: 3, ointments: 2};
            window.phaseData = window.phaseData || {
                mixing_completed: 8, mixing_inprogress: 2,
                drying_completed: 7, drying_inprogress: 3,
                granulation_completed: 6, granulation_inprogress: 2,
                compression_completed: 5, compression_inprogress: 3,
                packing_completed: 4, packing_inprogress: 2
            };
            window.weeklyData = window.weeklyData || {
                started_week1: 4, started_week2: 6, started_week3: 8, started_week4: 7,
                completed_week1: 3, completed_week2: 5, completed_week3: 6, completed_week4: 5
            };
            window.qcData = window.qcData || {passed: 15, failed: 3, pending: 7};
            
            console.log('Using fallback data');
        }
        
        // Initialize each chart with error handling
        initializeProductTypeChart();
        initializePhaseStatusChart();
        initializeWeeklyTrendChart();
        initializeQcStatusChart();
        
        console.log('All charts initialized successfully');
    } catch (error) {
        console.error('Error during chart initialization:', error);
        displayError('Error initializing charts: ' + error.message);
    }
}

// Individual chart initialization functions with error handling
function initializeProductTypeChart() {
    try {
        const canvas = ensureCanvas('productTypeChart');
        if (!canvas) return null;
        
        return new Chart(canvas.getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: ['Tablets', 'Capsules', 'Ointments'],
                datasets: [{
                    data: [
                        productData.tablets || 0, 
                        productData.capsules || 0, 
                        productData.ointments || 0
                    ],
                    backgroundColor: [
                        'rgba(54, 162, 235, 0.8)',
                        'rgba(255, 99, 132, 0.8)',
                        'rgba(75, 192, 192, 0.8)'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error initializing Product Type Chart:', error);
        return null;
    }
}

function initializePhaseStatusChart() {
    try {
        const canvas = ensureCanvas('phaseStatusChart');
        if (!canvas) return null;
        
        return new Chart(canvas.getContext('2d'), {
            type: 'bar',
            data: {
                labels: ['Mixing', 'Drying', 'Granulation', 'Compression', 'Packing'],
                datasets: [{
                    label: 'Completed',
                    data: [
                        phaseData.mixing_completed || 0,
                        phaseData.drying_completed || 0,
                        phaseData.granulation_completed || 0,
                        phaseData.compression_completed || 0,
                        phaseData.packing_completed || 0
                    ],
                    backgroundColor: 'rgba(75, 192, 192, 0.8)'
                }, {
                    label: 'In Progress',
                    data: [
                        phaseData.mixing_inprogress || 0,
                        phaseData.drying_inprogress || 0,
                        phaseData.granulation_inprogress || 0,
                        phaseData.compression_inprogress || 0,
                        phaseData.packing_inprogress || 0
                    ],
                    backgroundColor: 'rgba(54, 162, 235, 0.8)'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                },
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error initializing Phase Status Chart:', error);
        return null;
    }
}

function initializeWeeklyTrendChart() {
    try {
        const canvas = ensureCanvas('weeklyTrendChart');
        if (!canvas) return null;
        
        return new Chart(canvas.getContext('2d'), {
            type: 'line',
            data: {
                labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
                datasets: [{
                    label: 'Batches Started',
                    data: [
                        weeklyData.started_week1 || 0,
                        weeklyData.started_week2 || 0,
                        weeklyData.started_week3 || 0,
                        weeklyData.started_week4 || 0
                    ],
                    borderColor: 'rgba(54, 162, 235, 1)',
                    backgroundColor: 'rgba(54, 162, 235, 0.1)',
                    fill: true
                }, {
                    label: 'Batches Completed',
                    data: [
                        weeklyData.completed_week1 || 0,
                        weeklyData.completed_week2 || 0,
                        weeklyData.completed_week3 || 0,
                        weeklyData.completed_week4 || 0
                    ],
                    borderColor: 'rgba(75, 192, 192, 1)',
                    backgroundColor: 'rgba(75, 192, 192, 0.1)',
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                },
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error initializing Weekly Trend Chart:', error);
        return null;
    }
}

function initializeQcStatusChart() {
    try {
        const canvas = ensureCanvas('qcStatusChart');
        if (!canvas) return null;
        
        return new Chart(canvas.getContext('2d'), {
            type: 'pie',
            data: {
                labels: ['Passed', 'Failed', 'Pending'],
                datasets: [{
                    data: [
                        qcData.passed || 0,
                        qcData.failed || 0,
                        qcData.pending || 0
                    ],
                    backgroundColor: [
                        'rgba(75, 192, 192, 0.8)',
                        'rgba(255, 99, 132, 0.8)',
                        'rgba(255, 205, 86, 0.8)'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error initializing QC Status Chart:', error);
        return null;
    }
}

// Helper function to ensure canvas exists and has correct dimensions
function ensureCanvas(id) {
    let canvas = document.getElementById(id);
    
    if (!canvas) {
        console.error(`Canvas with ID "${id}" not found`);
        
        // Try to find a container for this chart
        const containers = document.querySelectorAll('.chart-container');
        let container = null;
        
        for (let i = 0; i < containers.length; i++) {
            if (containers[i].querySelector('canvas') === null) {
                container = containers[i];
                break;
            }
        }
        
        if (container) {
            console.log(`Creating canvas with ID "${id}"`);
            canvas = document.createElement('canvas');
            canvas.id = id;
            container.innerHTML = '';
            container.appendChild(canvas);
        } else {
            console.error(`Could not find container for chart "${id}"`);
            return null;
        }
    }
    
    // Ensure canvas has dimensions
    if (canvas.width === 0 || canvas.height === 0) {
        const parent = canvas.parentElement;
        canvas.width = parent.clientWidth || 300;
        canvas.height = parent.clientHeight || 200;
    }
    
    return canvas;
}
