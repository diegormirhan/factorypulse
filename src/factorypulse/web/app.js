const scenarios = {
  nominal: { product_type: "M", air_temperature_k: 300.1, process_temperature_k: 309.8, rotational_speed_rpm: 1450, torque_nm: 41.2, tool_wear_min: 92 },
  stress: { product_type: "L", air_temperature_k: 303.9, process_temperature_k: 312.9, rotational_speed_rpm: 1342, torque_nm: 62.4, tool_wear_min: 214 },
};

const form = document.querySelector("#risk-form");
const button = document.querySelector("#assess-button");
const errorMessage = document.querySelector("#form-error");

document.querySelectorAll(".scenario").forEach((scenarioButton) => {
  scenarioButton.addEventListener("click", () => {
    Object.entries(scenarios[scenarioButton.dataset.scenario]).forEach(([field, value]) => {
      form.elements[field].value = value;
    });
    document.querySelectorAll(".scenario").forEach((item) => {
      const isSelected = item === scenarioButton;
      item.classList.toggle("active", isSelected);
      item.setAttribute("aria-pressed", String(isSelected));
    });
    resetPrediction();
  });
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  setLoading(true);
  errorMessage.textContent = "";
  try {
    const response = await fetch("/api/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(readForm()),
    });
    if (!response.ok) {
      const problem = await response.json();
      throw new Error(typeof problem.detail === "string" ? problem.detail : "The assessment could not be completed.");
    }
    renderPrediction(await response.json());
  } catch (error) {
    errorMessage.textContent = `${error.message} Check the model and try again.`;
  } finally {
    setLoading(false);
  }
});

function readForm() {
  const values = Object.fromEntries(new FormData(form));
  return {
    product_type: values.product_type,
    air_temperature_k: Number(values.air_temperature_k),
    process_temperature_k: Number(values.process_temperature_k),
    rotational_speed_rpm: Number(values.rotational_speed_rpm),
    torque_nm: Number(values.torque_nm),
    tool_wear_min: Number(values.tool_wear_min),
  };
}

function setLoading(isLoading) {
  button.disabled = isLoading;
  button.querySelector("span").textContent = isLoading ? "Assessing operating state…" : "Run risk assessment";
}

function resetPrediction() {
  document.querySelector("#probability").textContent = "—";
  document.querySelector("#risk-badge").textContent = "Pending";
  document.querySelector("#risk-badge").className = "decision-badge pending";
  document.querySelector("#signal-light").className = "signal-light";
  document.querySelector("#threshold-fill").style.transform = "scaleX(0)";
  document.querySelector("#route-risk").textContent = "awaiting input";
  document.querySelector("#route-decision").className = "route-stop active";
  document.querySelector("#decision-copy").textContent = "Run an assessment to compare this machine with the calibrated inspection threshold.";
  document.querySelector("#driver-list").innerHTML = '<p class="empty-state">Explanations will appear here after scoring.</p>';
}

function renderPrediction(prediction) {
  const percent = prediction.failure_probability * 100;
  const thresholdPercent = prediction.decision_threshold * 100;
  const riskLabel = prediction.risk_level === "critical" ? "Inspection required" : prediction.risk_level;
  document.querySelector("#probability").textContent = `${percent.toFixed(1)}%`;
  document.querySelector("#risk-badge").textContent = riskLabel;
  document.querySelector("#risk-badge").className = `decision-badge ${prediction.risk_level}`;
  document.querySelector("#signal-light").className = `signal-light ${prediction.risk_level}`;
  document.querySelector("#threshold-fill").style.transform = `scaleX(${Math.min(percent, 100) / 100})`;
  document.querySelector("#threshold-marker").style.left = `${Math.min(thresholdPercent, 100)}%`;
  document.querySelector("#threshold-label").textContent = `threshold ${thresholdPercent.toFixed(1)}%`;
  document.querySelector("#route-risk").textContent = `${prediction.risk_level} · ${percent.toFixed(1)}%`;
  document.querySelector("#route-decision").className = `route-stop active ${prediction.risk_level}`;
  document.querySelector("#decision-copy").textContent = prediction.requires_inspection
    ? "Risk crossed the calibrated threshold. Schedule a focused inspection before the next operating cycle."
    : "Risk remains below the inspection threshold. Continue monitoring the operating signals.";
  document.querySelector("#driver-list").innerHTML = prediction.drivers.map((driver) => {
    const sign = driver.impact >= 0 ? "+" : "";
    return `<div class="driver"><strong>${escapeHtml(driver.label)}</strong><span>${escapeHtml(String(driver.value))} · reference ${escapeHtml(String(driver.reference))}</span><span class="impact">${sign}${(driver.impact * 100).toFixed(1)} pp</span></div>`;
  }).join("");
}

async function loadModelEvidence() {
  const lamp = document.querySelector("#api-lamp");
  const status = document.querySelector("#api-status");
  try {
    const health = await fetch("/api/health").then((response) => response.json());
    if (health.status !== "ready") throw new Error("Model artifact missing");
    lamp.classList.add("ready");
    status.textContent = `Model ${health.model_version} ready`;
    const summary = await fetch("/api/model").then((response) => response.json());
    const metrics = summary.test_metrics;
    document.querySelector("#metric-ap").textContent = formatPercent(metrics.average_precision);
    document.querySelector("#metric-recall").textContent = formatPercent(metrics.recall);
    document.querySelector("#metric-brier").textContent = metrics.brier_score.toFixed(3);
    document.querySelector("#metric-samples").textContent = metrics.samples.toLocaleString();
    document.querySelector("#model-name").textContent = summary.selected_model.replaceAll("_", " ");
    document.querySelector("#model-version").textContent = summary.model_version;
    document.querySelector("#threshold-marker").style.left = `${summary.threshold * 100}%`;
    document.querySelector("#threshold-label").textContent = `threshold ${(summary.threshold * 100).toFixed(1)}%`;
  } catch (error) {
    lamp.classList.add("error");
    status.textContent = "Model unavailable";
    errorMessage.textContent = "The model is not ready. Run `uv run factorypulse train` before the demo.";
  }
}

function formatPercent(value) { return `${(value * 100).toFixed(1)}%`; }
function escapeHtml(value) { const element = document.createElement("span"); element.textContent = value; return element.innerHTML; }

loadModelEvidence();
