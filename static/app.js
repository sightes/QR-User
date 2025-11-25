console.log("app.js cargado");

// ---------- Utilidades RUT ----------

// Normaliza el RUT: quita puntos y guion, y lo pasa a mayúsculas
function normalizarRut(value) {
    return value.replace(/\./g, "").replace(/-/g, "").toUpperCase();
}

// Valida un RUT chileno (mismo algoritmo que en el backend)
function validarRut(value) {
    const rut = normalizarRut(value);

    if (rut.length < 2) return false;

    const cuerpo = rut.slice(0, -1);
    const dv = rut.slice(-1);

    if (!/^\d+$/.test(cuerpo)) return false;

    let suma = 0;
    let factor = 2;

    for (let i = cuerpo.length - 1; i >= 0; i--) {
        suma += parseInt(cuerpo[i], 10) * factor;
        factor = factor === 7 ? 2 : factor + 1;
    }

    const resto = 11 - (suma % 11);
    let dvEsperado;

    if (resto === 11) {
        dvEsperado = "0";
    } else if (resto === 10) {
        dvEsperado = "K";
    } else {
        dvEsperado = String(resto);
    }

    return dv === dvEsperado;
}

// ---------- Inicialización ----------

document.addEventListener("DOMContentLoaded", () => {
    // --- Validación RUT en formulario 1 a 1 ---
    const form = document.getElementById("form-trabajador");
    const rutInput = document.getElementById("rut");

    if (form && rutInput) {
        // Crea (si no existe) un contenedor de error específico para JS
        function ensureErrorElement() {
            let errorDiv = rutInput.parentElement.querySelector(".error.js-error-rut");
            if (!errorDiv) {
                errorDiv = document.createElement("div");
                errorDiv.classList.add("error", "js-error-rut");
                rutInput.insertAdjacentElement("afterend", errorDiv);
            }
            return errorDiv;
        }

        // Limpia mensaje de error cuando el usuario escribe
        rutInput.addEventListener("input", () => {
            const errorDiv = rutInput.parentElement.querySelector(".error.js-error-rut");
            if (errorDiv) {
                errorDiv.textContent = "";
            }
        });

        form.addEventListener("submit", (e) => {
            const rut = rutInput.value.trim();
            const errorDiv = ensureErrorElement();

            if (!rut) {
                errorDiv.textContent = "El RUT no puede estar vacío.";
                e.preventDefault();
                return;
            }

            if (!validarRut(rut)) {
                errorDiv.textContent = "RUT inválido. Verifique el número y el dígito verificador.";
                e.preventDefault();
                return;
            }

            // Si pasa la validación, se envía el formulario normalmente
        });
    }

    // --- Manejo de pestañas (tabs) ---
    const tabButtons = document.querySelectorAll(".tab-button");
    const tabPanels = document.querySelectorAll(".tab-panel");

    function activarTab(nombreTab) {
        tabButtons.forEach((btn) => {
            const target = btn.getAttribute("data-tab");
            if (target === nombreTab) {
                btn.classList.add("active");
            } else {
                btn.classList.remove("active");
            }
        });

        tabPanels.forEach((panel) => {
            if (panel.id === `tab-${nombreTab}`) {
                panel.classList.add("active");
            } else {
                panel.classList.remove("active");
            }
        });
    }

    tabButtons.forEach((button) => {
        button.addEventListener("click", () => {
            const target = button.getAttribute("data-tab");
            activarTab(target);
        });
    });

    // Si hay una tabla de Excel cargada, activar automáticamente la pestaña "excel"
    const tablaExcel = document.querySelector("#tab-excel table");
    if (tablaExcel) {
        activarTab("excel");
    } else {
        activarTab("manual"); // por defecto
    }
});