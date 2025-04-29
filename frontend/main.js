// Auto-search if a card was saved from trending page
window.onload = function() {
    const savedCard = localStorage.getItem("searchedCard");
    if (savedCard) {
        document.getElementById("cardNameInput").value = savedCard;
        localStorage.removeItem("searchedCard");
        searchCard();  // 🔥 Auto-run the search
    }
}

let chart = null; // Global chart variable

function calculateMovingAverage(data, windowSize) {
    let movingAverages = [];

    for (let i = 0; i < data.length; i++) {
        if (i < windowSize - 1) {
            movingAverages.push(null); // not enough data yet
        } else {
            let sum = 0;
            for (let j = 0; j < windowSize; j++) {
                sum += data[i - j];
            }
            movingAverages.push(sum / windowSize);
        }
    }

    return movingAverages;
}

async function searchCard() {
    const cardName = document.getElementById("cardNameInput").value;
    const selectedCondition = document.getElementById("conditionFilter").value;
    const selectedWindowSize = parseInt(document.getElementById("movingAverageWindow").value);
    const url = `http://127.0.0.1:8000/card/${encodeURIComponent(cardName)}`;

    const resultDiv = document.getElementById("result");
    const chartCanvas = document.getElementById("priceChart");
    const spinner = document.getElementById("spinner");

    // 🎯 Start spinner
    spinner.style.display = "block";
    resultDiv.innerHTML = "";

    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error("Card not found");
        }

        const data = await response.json();

        // 📈 Build the Chart with Filter
        let filteredSales = data.sales;

        if (selectedCondition !== "all") {
            filteredSales = data.sales.filter(sale => sale.condition === selectedCondition);
        }

        const dates = filteredSales.map(sale => sale.sold_date);
        const prices = filteredSales.map(sale => sale.price);

        // 🔥 Calculate moving average AFTER you have prices
        const movingAverage = calculateMovingAverage(prices, selectedWindowSize);

        // 🔥 Calculate price change %
        let priceChangeText = '';
        if (prices.length >= 2) {
            const firstPrice = prices[0];
            const lastPrice = prices[prices.length - 1];
            const priceChange = ((lastPrice - firstPrice) / firstPrice) * 100;

            const changeDirection = priceChange >= 0 ? 'up' : 'down';
            const changeColor = priceChange >= 0 ? 'green' : 'red';

            priceChangeText = `<h4>Price Change: <span style="color:${changeColor};">${priceChange.toFixed(2)}% ${changeDirection}</span></h4>`;
        }

        // 🧹 Build HTML output
        let html = `<h2>${data.card_name}</h2>`;
        html += `<h3>Set Number: ${data.set_number}</h3>`;
        html += priceChangeText; // 🔥 Add price change line here

        html += "<h4>Medians:</h4><ul>";
        for (const condition in data.medians) {
            html += `<li>${condition}: $${data.medians[condition].toFixed(2)}</li>`;
        }
        html += "</ul>";

        html += "<h4>Recent Sales:</h4><ul>";
        data.sales.forEach(sale => {
            html += `<li>$${sale.price} - ${sale.condition} - ${sale.sold_date}</li>`;
        });
        html += "</ul>";

        resultDiv.innerHTML = html;

        if (chart) {
            chart.destroy();
        }

        chart = new Chart(chartCanvas, {
            type: 'line',
            data: {
                labels: dates,
                datasets: [
                    {
                        label: `Sold Price ($) [${selectedCondition === "all" ? "All Conditions" : selectedCondition}]`,
                        data: prices,
                        borderColor: 'blue',
                        borderWidth: 2,
                        fill: false,
                        tension: 0.3
                    },
                    {
                        label: `Moving Average (${selectedWindowSize} sales)`,
                        data: movingAverage,
                        borderColor: 'red',
                        borderWidth: 2,
                        fill: false,
                        borderDash: [5, 5],
                        tension: 0.3
                    }
                ]
            },
            options: {
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Sold Date'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Price ($)'
                        },
                        beginAtZero: false
                    }
                }
            }
        });

        // 🎯 Only now stop spinner (success)
        spinner.style.display = "none";

    } catch (error) {
        resultDiv.innerHTML = `<p style="color:red;">${error.message}</p>`;
        if (chart) {
            chart.destroy();
        }
        // 🎯 Also stop spinner if there’s an error
        spinner.style.display = "none";
    }
}

