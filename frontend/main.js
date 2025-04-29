// frontend/main.js

window.onload = function () {
    const savedCard = localStorage.getItem("searchedCard");
    if (savedCard) {
        document.getElementById("cardNameInput").value = savedCard;
        localStorage.removeItem("searchedCard");
        searchCard();
    }
};

let chart = null;

async function fetchSearchResults(query) {
    const response = await fetch(`https://poke-price-tracker.onrender.com/search?q=${encodeURIComponent(query)}`);
    return await response.json();
}

document.getElementById("cardNameInput").addEventListener("input", async (e) => {
    const resultsContainer = document.getElementById("searchResults");
    const query = e.target.value.trim();
    resultsContainer.innerHTML = "";

    if (query.length >= 2) {
        const results = await fetchSearchResults(query);

        results.forEach(card => {
            const div = document.createElement("div");
            div.className = "search-result";
            div.innerText = `${card.name} (${card.set_number})`;
            div.onclick = () => {
                document.getElementById("cardNameInput").value = card.name;
                resultsContainer.innerHTML = "";
                searchCard();
            };
            resultsContainer.appendChild(div);
        });
    }
});

// Add this container in index.html below the input:
// <div id="searchResults" class="search-results"></div>

async function searchCard() {
    const cardName = document.getElementById("cardNameInput").value;
    const selectedCondition = document.getElementById("conditionFilter")?.value || "all";
    const selectedWindowSize = parseInt(document.getElementById("movingAverageWindow")?.value || 3);
    const url = `https://poke-price-tracker.onrender.com/card/${encodeURIComponent(cardName)}`;

    const resultDiv = document.getElementById("result");
    const chartCanvas = document.getElementById("priceChart");
    const spinner = document.getElementById("spinner");
    spinner.style.display = "block";
    resultDiv.innerHTML = "";

    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error("Card not found");
        }
        const data = await response.json();
        spinner.style.display = "none";

        let html = `<h2>${data.card_name}</h2>`;
        html += `<h3>Set Number: ${data.set_number}</h3>`;

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

        const filteredSales = selectedCondition !== "all" ? data.sales.filter(s => s.condition === selectedCondition) : data.sales;
        const dates = filteredSales.map(s => s.sold_date);
        const prices = filteredSales.map(s => s.price);
        const movingAverage = calculateMovingAverage(prices, selectedWindowSize);

        if (chart) chart.destroy();

        chart = new Chart(chartCanvas, {
            type: 'line',
            data: {
                labels: dates,
                datasets: [
                    {
                        label: `Price [${selectedCondition}]`,
                        data: prices,
                        borderColor: 'blue',
                        borderWidth: 2,
                        tension: 0.3
                    },
                    {
                        label: `Moving Avg (${selectedWindowSize})`,
                        data: movingAverage,
                        borderColor: 'red',
                        borderDash: [5, 5],
                        borderWidth: 2,
                        tension: 0.3
                    }
                ]
            },
            options: {
                scales: {
                    x: { title: { display: true, text: 'Sold Date' } },
                    y: { title: { display: true, text: 'Price ($)' }, beginAtZero: false }
                }
            }
        });

    } catch (error) {
        resultDiv.innerHTML = `<p style="color:red;">${error.message}</p>`;
        if (chart) chart.destroy();
        spinner.style.display = "none";
    }
}

function calculateMovingAverage(data, windowSize) {
    const averages = [];
    for (let i = 0; i < data.length; i++) {
        if (i < windowSize - 1) averages.push(null);
        else averages.push(data.slice(i - windowSize + 1, i + 1).reduce((a, b) => a + b, 0) / windowSize);
    }
    return averages;
}
