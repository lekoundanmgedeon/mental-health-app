(() => {
    const canvas = document.getElementById('probabilityChart');
    if (!canvas || !window.probabilityLabels || !window.probabilityValues) return;

    new Chart(canvas, {
        type: 'bar',
        data: {
            labels: window.probabilityLabels,
            datasets: [{
                label: 'Probability (%)',
                data: window.probabilityValues,
                borderWidth: 1,
                borderRadius: 12
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: (context) => `${context.raw}%`
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        callback: (value) => `${value}%`
                    }
                }
            }
        }
    });
})();
