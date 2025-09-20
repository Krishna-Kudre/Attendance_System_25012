function onScanSuccess(decodedText, decodedResult) {
    // Send scanned data to backend
    fetch("/scan_attendance", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ qr_data: decodedText })
    })
    .then(res => res.json())
    .then(data => {
        const msg = document.getElementById("message");
        msg.innerText = data.message;
    });
}

// Initialize html5-qrcode scanner
let html5QrcodeScanner = new Html5QrcodeScanner(
    "reader", { fps: 10, qrbox: 250 }
);
html5QrcodeScanner.render(onScanSuccess);
