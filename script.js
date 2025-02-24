const API_URL = "https://your-flask-api.onrender.com";  // ✅ ใส่ URL ของ Flask API

async function sendBarcode(barcode) {
    const response = await fetch(`${API_URL}/scan`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ barcode })
    });

    const data = await response.json();
    console.log("📤 Response:", data);
    document.getElementById("result").innerText = "✅ บาร์โค้ด: " + barcode;
}

function downloadCSV() {
    window.location.href = `${API_URL}/export`;
}
