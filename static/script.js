async function searchProduct() {
  const query = document.getElementById('searchInput').value;
  const bestValueOnly = document.getElementById('bestValueOnly').checked;
  const sortOption = document.getElementById('sortOption').value;

  const res = await fetch(`/search?q=${query}`);
  const data = await res.json();

  const results = document.getElementById("results");
  results.innerHTML = "";

  // Flatten data into a list for easier filtering/sorting
  let allItems = [];
  for (let platform in data) {
    data[platform].forEach(item => {
      allItems.push({
        ...item,
        platform,
        priceValue: parseInt(item.price?.replace(/[₹,]/g, "")) || 0
      });
    });
  }

  // Filter by "Best Value" if checkbox is checked
  if (bestValueOnly) {
    allItems = allItems.filter(item => item.value_tag === "✅ Best Value");
  }

  // Sort logic
  if (sortOption === "priceLowHigh") {
    allItems.sort((a, b) => a.priceValue - b.priceValue);
  } else if (sortOption === "priceHighLow") {
    allItems.sort((a, b) => b.priceValue - a.priceValue);
  } else if (sortOption === "platform") {
    allItems.sort((a, b) => a.platform.localeCompare(b.platform));
  }

  // Group by platform for sectioning
  const grouped = {};
  for (let item of allItems) {
    if (!grouped[item.platform]) grouped[item.platform] = [];
    grouped[item.platform].push(item);
  }

  // Render results
  for (let platform in grouped) {
    results.innerHTML += `<h3>${platform.toUpperCase()}</h3><div style="display: flex; flex-wrap: wrap; gap: 10px;">`;

    grouped[platform].forEach(item => {
      results.innerHTML += `
        <div style="border: 1px solid #ccc; border-radius: 8px; padding: 10px; width: 300px;">
          <a href="${item.link}" target="_blank" style="font-weight: bold; color: blue;">${item.title}</a>
          <p><strong>Price:</strong> ${item.price}</p>
          ${item.value_tag ? `<p><strong>Deal:</strong> ${item.value_tag}</p>` : ""}
        </div>`;
    });

    results.innerHTML += `</div><hr/>`;
  }
}
