// static/script.js

async function generatePlate() {
    const number = document.getElementById("inputNumber").value;

    console.log("Generated number:", number);

    const response = await fetch('http://127.0.0.1:5000/generate_plate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ number: number })
    });

    if (response.ok) {
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const img = document.getElementById("ishiharaImage");
        img.src = url;
        img.style.display = 'block';
    } else {
        alert('Failed to generate Ishihara plate');
    }
}
