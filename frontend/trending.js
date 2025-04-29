async function loadTrending() {
    const url = `http://127.0.0.1:8000/trending`;

    const trendingDiv = document.getElementById("trendingList");
    trendingDiv.innerHTML = "Loading...";

    try {
        const response = await fetch(url);
        const data = await response.json();

        let html = "<ol>";
        data.forEach(card => {
            html += `<li><a href="index.html" onclick="saveSearch('${card.card_name}')">${card.card_name} (Set: ${card.set_number})</a></li>`;
        });
        html += "</ol>";

        trendingDiv.innerHTML = html;

    } catch (error) {
        trendingDiv.innerHTML = `<p style="color:red;">Failed to load trending cards.</p>`;
    }
}

// Save card name into localStorage
function saveSearch(cardName) {
    localStorage.setItem("searchedCard", cardName);
}

loadTrending();
