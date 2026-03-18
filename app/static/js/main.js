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
});
