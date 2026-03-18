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
    const bagelChoices = window.cateringConfig.bagelChoices || [];
    const summaryList = document.getElementById("order-summary-list");
    const summaryTotal = document.getElementById("order-summary-total");
    const summaryEmpty = document.getElementById("order-summary-empty");
    const container = document.getElementById("bagel-rows-container");
    const addBtn = document.getElementById("add-bagel-row");
    const rowTemplate = document.getElementById("bagel-row-template");
    const bagelsJsonInput = document.getElementById("bagel-rows-json");

    const MAX_BAGEL_ROWS = 20;

    function populateTypeSelect(select) {
        select.innerHTML = "";
        bagelChoices.forEach(({ value, label }) => {
            const opt = document.createElement("option");
            opt.value = value;
            opt.textContent = label;
            select.appendChild(opt);
        });
    }

    function addBagelRow() {
        if (container.querySelectorAll(".bagel-row").length >= MAX_BAGEL_ROWS) {
            return;
        }
        const clone = rowTemplate.content.cloneNode(true);
        const row = clone.querySelector(".bagel-row");

        populateTypeSelect(row.querySelector(".bagel-type"));

        row.querySelector(".bagel-remove").addEventListener("click", () => removeBagelRow(row));
        row.querySelector(".bagel-qty").addEventListener("input", updateSummary);
        row.querySelector(".bagel-type").addEventListener("change", updateSummary);
        row.querySelector(".bagel-bread").addEventListener("change", updateSummary);

        container.appendChild(row);
        updateSummary();
        updateAddButton();
    }

    function removeBagelRow(row) {
        if (container.querySelectorAll(".bagel-row").length <= 1) {
            return;
        }
        row.classList.remove("bagel-row-enter");
        row.classList.add("bagel-row-leave");
        row.addEventListener("animationend", () => {
            row.remove();
            updateSummary();
            updateAddButton();
        }, { once: true });
    }

    function updateAddButton() {
        if (addBtn) {
            addBtn.disabled = container.querySelectorAll(".bagel-row").length >= MAX_BAGEL_ROWS;
        }
    }

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

        container.querySelectorAll(".bagel-row").forEach((row) => {
            const qtyInput = row.querySelector(".bagel-qty");
            const typeSelect = row.querySelector(".bagel-type");
            const breadSelect = row.querySelector(".bagel-bread");
            const qty = qtyInput ? Math.max(0, Number(qtyInput.value || 0)) : 0;
            if (qty <= 0) {
                return;
            }
            const type = typeSelect ? String(typeSelect.value || "").trim() || "Bagel" : "Bagel";
            const bread = breadSelect ? String(breadSelect.value || "").trim() : "";
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

    function serializeBagelRows() {
        const rows = [];
        container.querySelectorAll(".bagel-row").forEach((row) => {
            const qtyInput = row.querySelector(".bagel-qty");
            const typeSelect = row.querySelector(".bagel-type");
            const breadSelect = row.querySelector(".bagel-bread");
            const qty = qtyInput ? Math.max(0, Number(qtyInput.value || 0)) : 0;
            if (qty <= 0) {
                return;
            }
            rows.push({
                qty: qty,
                type: typeSelect ? String(typeSelect.value || "").trim() : "",
                bread: breadSelect ? String(breadSelect.value || "").trim() : "",
            });
        });
        return rows;
    }

    form.addEventListener("submit", () => {
        if (bagelsJsonInput) {
            bagelsJsonInput.value = JSON.stringify(serializeBagelRows());
        }
    });

    form.addEventListener("input", updateSummary);
    form.addEventListener("change", updateSummary);

    if (addBtn) {
        addBtn.addEventListener("click", addBagelRow);
    }

    addBagelRow();
});
