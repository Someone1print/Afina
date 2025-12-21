// static/js/dashboard_charts.js
// Красивые диаграммы с общими осями и крупными подписями

document.addEventListener("DOMContentLoaded", function () {

    // Универсальный layout для гистограмм
    function getBarLayout(maxValue) {
        const top = maxValue > 0 ? maxValue * 1.35 : 10; // запас сверху для подписей

        return {
            xaxis: {
                tickfont: { size: 14, color: '#444' },
                gridcolor: 'transparent'
            },
            yaxis: {
                title: 'KGS',
                titlefont: { size: 14, color: '#444' },
                tickfont: { size: 13, color: '#444' },
                zeroline: false,
                gridcolor: 'rgba(0,0,0,0.12)',
                rangemode: 'tozero',
                range: [0, top],
                automargin: true
            },
            plot_bgcolor: 'rgba(0,0,0,0)',
            paper_bgcolor: 'rgba(0,0,0,0)',
            margin: { t: 90, b: 60, l: 60, r: 20 },
            bargap: 0.2,
            autosize: true
        };
    }

    // ============================
    // 1–2. Гистограммы: расход + доход
    // ============================

    Promise.all([
        fetch("/api/dashboard/expenses-by-day/").then(r => r.json()),
        fetch("/api/dashboard/income-by-day/").then(r => r.json())
    ]).then(([expData, incomeData]) => {
        const expAmounts = expData.amounts || [];
        const incomeAmounts = incomeData.amounts || [];

        const maxVal = Math.max(
            ...(expAmounts.length ? expAmounts : [0]),
            ...(incomeAmounts.length ? incomeAmounts : [0])
        );

        const commonLayout = getBarLayout(maxVal);

        // ---------- Расходы по дням ----------
        const expensesTrace = {
            x: expData.days,
            y: expAmounts,
            type: 'bar',
            marker: {
                color: '#e91e63',
                line: { width: 0 }
            },
            text: expAmounts.map(a => a > 0 ? a.toLocaleString('ru-RU') : ''),
            textposition: 'outside', // над столбцом
            textfont: {
                size: 550,
                color: '#e91e63',
                family: '"Segoe UI", system-ui, sans-serif',
                weight: 'bold'
            },
            hovertemplate: '<b>%{x}</b><br>%{y:,.0f} KGS<extra></extra>'
        };

        Plotly.newPlot(
            'expenses-by-day-chart',
            [expensesTrace],
            commonLayout,
            { responsive: true, displayModeBar: false }
        );

        // ---------- Доходы по дням ----------
        const incomeTrace = {
            x: incomeData.days,
            y: incomeAmounts,
            type: 'bar',
            marker: {
                color: '#43a047'
            },
            text: incomeAmounts.map(a => a > 0 ? a.toLocaleString('ru-RU') : ''),
            textposition: 'outside',
            textfont: {
                size: 28,           // 🔥 ТЕ ЖЕ КРУПНЫЕ ЦИФРЫ
                color: '#43a047',
                family: '"Segoe UI", system-ui, sans-serif',
                weight: 'bold'
            },
            hovertemplate: '<b>%{x}</b><br>%{y:,.0f} KGS<extra></extra>'
        };

        // важный момент: layout лучше клонить, чтобы Plotly не мутировал объект
        const incomeLayout = JSON.parse(JSON.stringify(commonLayout));

        Plotly.newPlot(
            'income-by-day-chart',
            [incomeTrace],
            incomeLayout,
            { responsive: true, displayModeBar: false }
        );
    });

    // ============================
    // 3. Круговая — Расходы
    // ============================
    fetch("/api/dashboard/expenses-by-category/")
        .then(r => r.json())
        .then(data => {
            if (!data.amounts || data.amounts.every(a => a === 0)) {
                data = { categories: ["Нет данных"], amounts: [1] };
            }
            const trace = {
                labels: data.categories,
                values: data.amounts,
                type: 'pie',
                textinfo: 'label+percent',
                textposition: 'outside',
                marker: {
                    colors: ['#e91e63', '#1976d2', '#ffb300', '#43a047', '#7b1fa2', '#ff6f00', '#d81b60', '#546e7a'],
                    line: { color: '#fff', width: 4 }
                },
                hovertemplate:
                    '<b>%{label}</b><br>%{value:,.0f} KGS<br>%{percent}<extra></extra>'
            };

            Plotly.newPlot('expenses-by-category-chart', [trace], {
                showlegend: false,
                margin: { t: 40, b: 40, l: 20, r: 20 },
                paper_bgcolor: 'rgba(0,0,0,0)',
                plot_bgcolor: 'rgba(0,0,0,0)'
            }, { responsive: true, displayModeBar: false });
        });

    // ============================
    // 4. Круговая — Доходы
    // ============================
    fetch("/api/dashboard/income-by-category/")
        .then(r => r.json())
        .then(data => {
            if (!data.amounts || data.amounts.every(a => a === 0)) {
                data = { categories: ["Нет данных"], amounts: [1] };
            }
            const trace = {
                labels: data.categories,
                values: data.amounts,
                type: 'pie',
                textinfo: 'label+percent',
                marker: {
                    colors: ['#43a047', '#2e7d32', '#66bb6a', '#81c784', '#a5d6a7'],
                    line: { color: '#fff', width: 4 }
                },
                hovertemplate:
                    '<b>%{label}</b><br>%{value:,.0f} KGS<br>%{percent}<extra></extra>'
            };

            Plotly.newPlot('income-by-category-chart', [trace], {
                showlegend: false,
                margin: { t: 40, b: 40, l: 20, r: 20 },
                paper_bgcolor: 'rgba(0,0,0,0)'
            }, { responsive: true, displayModeBar: false });
        });

});
