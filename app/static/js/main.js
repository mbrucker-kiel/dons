document.addEventListener("DOMContentLoaded", () => {
    const numberInputs = document.querySelectorAll("input[type='number']");
    numberInputs.forEach((input) => {
        input.addEventListener("input", () => {
            if (input.value === "") {
                input.value = 0;
            }
            if (Number(input.value) < 0) {
                input.value = 0;
            }
        });
    });

    const form = document.getElementById("catering-order-form");
    if (!form || !window.cateringConfig) {
        return;
    }

    const bagelPrices = window.cateringConfig.bagelPrices || {};
    const summaryList = document.getElementById("order-summary-list");
    const summaryTotal = document.getElementById("order-summary-total");
    const summaryEmpty = document.getElementById("order-summary-empty");

    const parseQty = (name) => {
        const element = form.querySelector(`[name='${name}']`);
        if (!element) {
            return 0;
        }
        const value = Number(element.value || 0);
        return Number.isFinite(value) && value > 0 ? value : 0;
    };

    const readValue = (name) => {
        const element = form.querySelector(`[name='${name}']`);
        return element ? String(element.value || "").trim() : "";
    };

    const renderRow = (label, priceLabel) => {
        const row = document.createElement("li");
        row.className = "flex justify-between gap-4";

        const left = document.createElement("span");
        left.textContent = label;
        row.appendChild(left);

        const right = document.createElement("strong");
        right.textContent = priceLabel;
        row.appendChild(right);

        summaryList.appendChild(row);
    };

    const updateSummary = () => {
        if (!summaryList || !summaryTotal) {
            return;
        }

        summaryList.innerHTML = "";
        let total = 0;
        let count = 0;

        [1, 2, 3].forEach((index) => {
            const qty = parseQty(`bagel_${index}_qty`);
            if (qty <= 0) {
                return;
            }
            const type = readValue(`bagel_${index}_type`) || "Bagel";
            const bread = readValue(`bagel_${index}_bread`);
            const unitPrice = Number(bagelPrices[type] || 0);
            const lineTotal = unitPrice * qty;
            const label = bread
                ? `Bagel (Typ: ${type}, Brot: ${bread}) × ${qty}`
                : `Bagel (Typ: ${type}) × ${qty}`;
            renderRow(label, `${lineTotal.toFixed(2)} €`);
            total += lineTotal;
            count += 1;
        });

        const zimtQty = parseQty("zimtschnecke_qty");
        if (zimtQty > 0) {
            const zimtType = readValue("zimtschnecke_type") || "Typ offen";
            renderRow(
                `Zimtschnecke (Typ: ${zimtType}) × ${zimtQty}`,
                "Preis auf Anfrage"
            );
            count += 1;
        }

        const kuchenQty = parseQty("kuchen_qty");
        if (kuchenQty > 0) {
            const kuchenType = readValue("kuchen_type") || "Typ offen";
            renderRow(`Kuchen (Typ: ${kuchenType}) × ${kuchenQty}`, "Preis auf Anfrage");
            count += 1;
        }

        if (summaryEmpty) {
            summaryEmpty.classList.toggle("hidden", count > 0);
        }
        summaryTotal.textContent = `${total.toFixed(2)} €`;
    };

    form.addEventListener("input", updateSummary);
    form.addEventListener("change", updateSummary);
    updateSummary();
});
