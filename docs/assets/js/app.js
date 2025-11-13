const SESSION_KEY = "facade-session";
const RULE_SET = {
  module_width: { target: 1.2, min: 0.8, max: 1.8, weight: 1.0 },
  module_height: { target: 3.2, min: 2.4, max: 4.2, weight: 1.2 },
  module_depth: { target: 0.26, min: 0.18, max: 0.35, weight: 0.9 },
  curvature_radius: { target: 36.0, min: 8.0, max: 60.0, weight: 1.1 },
  tilt_angle: { target: 4.5, min: -3.0, max: 9.0, weight: 0.8 },
  mullion_spacing: { target: 1.5, min: 1.0, max: 2.2, weight: 0.7 },
  panel_thickness: { target: 0.022, min: 0.016, max: 0.032, weight: 0.9 },
};

const MATERIAL_DENSITY = {
  aluminum: 27.0,
  glass: 25.0,
  steel: 78.5,
};

let dataset = null;
let charts = {};
let analysisHistory = [];

window.addEventListener("DOMContentLoaded", async () => {
  guardSession();
  bindLogout();
  await bootstrapDataset();
  bindParameterForm();
});

function guardSession() {
  const sessionRaw = window.localStorage.getItem(SESSION_KEY);
  if (!sessionRaw) {
    window.location.href = "index.html";
    return;
  }
  try {
    const session = JSON.parse(sessionRaw);
    document.getElementById("sessionUser").textContent = session.email;
  } catch (error) {
    console.warn("Session parse failed", error);
    window.localStorage.removeItem(SESSION_KEY);
    window.location.href = "index.html";
  }
}

function bindLogout() {
  document.getElementById("logoutBtn").addEventListener("click", () => {
    window.localStorage.removeItem(SESSION_KEY);
    window.location.href = "index.html";
  });
}

async function bootstrapDataset() {
  try {
    const response = await fetch("data/system_dataset.json", { cache: "no-store" });
    dataset = await response.json();
    document.getElementById("lastUpdated").textContent = new Date(dataset.generatedAt).toLocaleString();
    populateProfiles(dataset.profiles, dataset.activeProfileId);
    const activeProfile = dataset.profiles.find((item) => item.id === dataset.activeProfileId) || dataset.profiles[0];
    if (activeProfile) {
      applyProfileToForm(activeProfile);
      runAndRender(activeProfile, "导入基础配置");
    }
  } catch (error) {
    console.error("加载数据失败", error);
    dataset = getFallbackDataset();
    document.getElementById("lastUpdated").textContent = new Date(dataset.generatedAt).toLocaleString();
    populateProfiles(dataset.profiles, dataset.activeProfileId);
    const activeProfile = dataset.profiles.find((item) => item.id === dataset.activeProfileId) || dataset.profiles[0];
    if (activeProfile) {
      applyProfileToForm(activeProfile);
      runAndRender(activeProfile, "使用内置校核参数");
    }
    showToast("无法载入外部数据，已启用内置参数集。");
  }
}

function populateProfiles(profiles, activeId) {
  const selector = document.getElementById("profileSelector");
  selector.innerHTML = "";
  profiles.forEach((profile) => {
    const option = document.createElement("option");
    option.value = profile.id;
    option.textContent = `${profile.id} · ${profile.name}`;
    selector.appendChild(option);
  });
  selector.value = activeId;
  document.getElementById("activeProfileLabel").textContent = activeId;
  selector.addEventListener("change", (event) => {
    const selected = dataset.profiles.find((profile) => profile.id === event.target.value);
    if (selected) {
      document.getElementById("activeProfileLabel").textContent = selected.id;
      applyProfileToForm(selected);
      runAndRender(selected, "方案切换重新生成");
    }
  });
}

function applyProfileToForm(profile) {
  const form = document.getElementById("parameterForm");
  Object.entries(profile).forEach(([key, value]) => {
    if (form.elements[key]) {
      form.elements[key].value = value;
    }
  });
}

function bindParameterForm() {
  const form = document.getElementById("parameterForm");
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    if (!form.checkValidity()) {
      form.classList.add("was-validated");
      return;
    }
    const parameters = getFormParameters(form);
    const profileName = document.getElementById("profileSelector").selectedOptions[0]?.textContent || "自定义输入";
    runAndRender(parameters, `参数重新计算 · ${profileName}`);
  });
}

function getFormParameters(form) {
  const entries = new FormData(form);
  const params = {};
  entries.forEach((value, key) => {
    params[key] = key === "material" ? value : parseFloat(value);
  });
  return params;
}

function runAndRender(input, remark) {
  const enrichedInput = mapInput(input);
  const integrity = computeIntegrity(enrichedInput);
  const geometry = generateGeometry(enrichedInput);
  const structural = runStructural(enrichedInput, geometry);
  const corrections = computeCorrections(enrichedInput, geometry);
  const association = computeAssociation(enrichedInput, corrections);

  updateIntegrityUI(integrity);
  updateGeometryUI(geometry);
  updateStructuralUI(structural);
  updateCorrectionsUI(corrections);
  updateAssociationUI(association);
  updateHistory(enrichedInput, structural, corrections, remark);
}

function mapInput(input) {
  if (input instanceof Element || input instanceof HTMLFormElement) {
    return getFormParameters(input);
  }
  return { ...input };
}

function computeIntegrity(params) {
  const requiredKeys = Object.keys(RULE_SET);
  const missing = requiredKeys.filter((key) => params[key] == null || Number.isNaN(params[key]));
  const completeness = Number(((1 - missing.length / requiredKeys.length) * 100).toFixed(2));

  let penalty = 0;
  const normalized = {};
  requiredKeys.forEach((key) => {
    const value = params[key];
    const rule = RULE_SET[key];
    const spread = rule.max - rule.min || rule.target || 1;
    const gap = Math.abs(value - rule.target) / (spread / 2);
    const normalizedGap = Math.min(gap, 1.8);
    normalized[key] = Number((100 - normalizedGap * 55 * rule.weight).toFixed(2));
    penalty += normalizedGap * rule.weight;
  });

  const ruleMatch = Number(Math.max(0, 100 - penalty * 18).toFixed(2));

  return {
    completenessScore: completeness,
    ruleMatchScore: ruleMatch,
    normalizedIndicators: normalized,
    missingParameters: missing,
    notes:
      completeness > 90 && ruleMatch > 72
        ? "参数集已满足生成逻辑，可进行几何重构。"
        : "建议校核高偏离项，提升规则匹配度。",
  };
}

function generateGeometry(params) {
  const area = params.module_width * params.module_height;
  const envelopeVolume = area * params.module_depth;
  const curvatureFactor = 1 / Math.max(params.curvature_radius, 1);
  const tiltFactor = (params.tilt_angle * Math.PI) / 180;
  const density = MATERIAL_DENSITY[params.material] ?? 30;
  const frameWeight = Number((envelopeVolume * density * 0.85).toFixed(2));

  const controlPoints = [
    [0, 0],
    [Number((params.module_width * 0.4).toFixed(3)), Number((params.module_height * 0.18).toFixed(3))],
    [Number((params.module_width * 0.65).toFixed(4)), Number((params.module_height * 0.55).toFixed(4))],
    [Number(params.module_width.toFixed(4)), Number(params.module_height.toFixed(4))],
  ];

  const rawWeights = [
    area,
    envelopeVolume * (1 + curvatureFactor * 12),
    frameWeight * (0.5 + Math.abs(tiltFactor)),
    params.panel_thickness * 10,
  ];
  const total = rawWeights.reduce((sum, val) => sum + val, 0);
  const pathWeights = rawWeights.map((value) => Number((value / total).toFixed(3)));

  return {
    projectedArea: Number(area.toFixed(3)),
    envelopeVolume: Number(envelopeVolume.toFixed(3)),
    frameWeight,
    controlPoints,
    pathWeights,
    dynamicCoefficients: {
      curvatureInfluence: Number((curvatureFactor * 120).toFixed(2)),
      tiltResponse: Number((Math.sin(tiltFactor) * 45).toFixed(2)),
      mullionCoupling: Number((params.mullion_spacing / params.module_width).toFixed(3)),
      thicknessRatio: Number((params.panel_thickness / params.module_depth).toFixed(3)),
    },
  };
}

function runStructural(params, geometry) {
  const exposure = 0.5 + params.module_height / 12;
  const windPressure = 0.613 * params.wind_speed ** 2 * exposure / 1000;
  const deadLoad = geometry.frameWeight * 0.0098;
  const nodes = 7;
  const step = params.module_height / (nodes - 1);
  const baselineStress = Math.sqrt(windPressure ** 2 + deadLoad ** 2);
  const curvatureInfluence = geometry.dynamicCoefficients.curvatureInfluence;

  const stressDistribution = Array.from({ length: nodes }, (_, index) => {
    const elevation = Number((step * index).toFixed(2));
    const gradient = 1 + (index / (nodes - 1)) * 0.32;
    const generated = baselineStress * gradient * (1 + curvatureInfluence / 400);
    const optimized = generated * (0.92 - index * 0.015);
    return {
      node: index + 1,
      elevation,
      baseline: Number((baselineStress * gradient).toFixed(3)),
      generated: Number(generated.toFixed(3)),
      optimized: Number(optimized.toFixed(3)),
    };
  });

  const stabilityIndex = Math.max(
    0,
    Math.min(
      100,
      Number(
        (
          100 -
          average(stressDistribution.map((item) => Math.abs(item.generated - item.optimized))) * 38
        ).toFixed(2)
      )
    )
  );

  return {
    windPressure: Number(windPressure.toFixed(3)),
    deadLoad: Number(deadLoad.toFixed(3)),
    stabilityIndex,
    stressDistribution,
  };
}

function computeCorrections(params, geometry) {
  const baseDeviation = geometry.dynamicCoefficients.curvatureInfluence * 0.18;
  const thermalEffect = params.thermal_gradient * 0.014;
  const drift = baseDeviation + thermalEffect;
  const iterations = [];

  for (let i = 0; i < 5; i += 1) {
    const reduction = 0.72 - i * 0.12;
    const deviationMm = Number((drift * reduction).toFixed(3));
    const shapeOffset = Number((geometry.dynamicCoefficients.tiltResponse * reduction).toFixed(3));
    const pathReweight = geometry.pathWeights[i % geometry.pathWeights.length];
    iterations.push({
      iteration: i + 1,
      deviationMm,
      shapeOffsetDeg: shapeOffset,
      pathReweight: Number(pathReweight.toFixed(3)),
    });
  }

  const residualDeviation = Number((iterations.at(-1).deviationMm * 0.45).toFixed(3));
  const assemblySuitability = Math.max(0, Math.min(100, Number((100 - residualDeviation * 12).toFixed(2))));

  return {
    iterations,
    residualDeviation,
    assemblySuitability,
  };
}

function computeAssociation(params, corrections) {
  const stages = ["Concept", "Design Freeze", "Mockup", "Fabrication", "Installation"];
  const base = 0.68 + corrections.assemblySuitability / 250;
  const correlations = stages.map((stage, index) => {
    const attenuation = 1 - index * 0.06;
    const value = Math.max(0.4, Math.min(0.98, base * attenuation + 0.05 * index));
    return { stage, correlation: Number(value.toFixed(3)) };
  });

  const linkageTable = correlations.map(({ stage }, index) => ({
    stage,
    designParam: Number((params.module_width * (1 + 0.015 * index)).toFixed(3)),
    fieldValue: Number((params.module_width * (1 + 0.01 * index)).toFixed(3)),
    syncLag: Math.max(0, (5 - index) * 2),
  }));

  return { correlations, linkageTable };
}

function updateIntegrityUI(result) {
  document.getElementById("completenessScore").textContent = `${result.completenessScore}%`;
  document.getElementById("ruleMatchScore").textContent = `${result.ruleMatchScore}%`;
  document.getElementById("integrityNotes").textContent = result.notes;
  document.getElementById("completenessProgress").value = result.completenessScore;
  document.getElementById("ruleMatchProgress").value = result.ruleMatchScore;
  const radarData = Object.entries(result.normalizedIndicators).map(([_, value]) => value);
  const radarLabels = Object.keys(result.normalizedIndicators).map((label) => label.replaceAll("_", " "));
  if (!charts.integrityRadar) {
    charts.integrityRadar = new Chart(document.getElementById("integrityRadar"), {
      type: "radar",
      data: {
        labels: radarLabels,
        datasets: [
          {
            label: "指标归一化趋势",
            data: radarData,
            borderColor: "rgba(37, 99, 235, 0.8)",
            backgroundColor: "rgba(37, 99, 235, 0.2)",
            pointBackgroundColor: "rgba(37, 99, 235, 0.8)",
          },
        ],
      },
      options: {
        responsive: true,
        scales: {
          r: {
            beginAtZero: true,
            suggestedMax: 100,
            grid: { color: "rgba(15, 23, 42, 0.1)" },
            angleLines: { color: "rgba(37, 99, 235, 0.15)" },
          },
        },
        plugins: { legend: { display: false } },
      },
    });
  } else {
    charts.integrityRadar.data.labels = radarLabels;
    charts.integrityRadar.data.datasets[0].data = radarData;
    charts.integrityRadar.update();
  }
}

function updateGeometryUI(geometry) {
  document.getElementById("projectedArea").textContent = geometry.projectedArea;
  document.getElementById("envelopeVolume").textContent = geometry.envelopeVolume;
  document.getElementById("frameWeight").textContent = geometry.frameWeight;

  const labels = ["构造域", "包络调控", "受力均衡", "厚度调节"];
  if (!charts.pathWeights) {
    charts.pathWeights = new Chart(document.getElementById("pathWeightChart"), {
      type: "doughnut",
      data: {
        labels,
        datasets: [
          {
            data: geometry.pathWeights,
            backgroundColor: [
              "rgba(37, 99, 235, 0.85)",
              "rgba(56, 189, 248, 0.75)",
              "rgba(20, 184, 166, 0.8)",
              "rgba(99, 102, 241, 0.75)",
            ],
            borderWidth: 0,
          },
        ],
      },
      options: {
        plugins: {
          legend: {
            position: "bottom",
            labels: { usePointStyle: true },
          },
        },
      },
    });
  } else {
    charts.pathWeights.data.datasets[0].data = geometry.pathWeights;
    charts.pathWeights.update();
  }

  const dynamicContainer = document.getElementById("dynamicCoefficientGroup");
  dynamicContainer.innerHTML = "";
  Object.entries(geometry.dynamicCoefficients).forEach(([key, value]) => {
    const col = document.createElement("div");
    col.className = "col-6";
    col.innerHTML = `
      <div class="status-chip w-100 justify-content-between">
        <span>${formatLabel(key)}</span>
        <strong>${value}</strong>
      </div>`;
    dynamicContainer.appendChild(col);
  });
}

function updateStructuralUI(structural) {
  document.getElementById("windPressure").textContent = structural.windPressure;
  document.getElementById("deadLoad").textContent = structural.deadLoad;
  document.getElementById("stabilityIndex").textContent = structural.stabilityIndex;

  const labels = structural.stressDistribution.map((item) => `N${item.node}`);
  const generated = structural.stressDistribution.map((item) => item.generated);
  const optimized = structural.stressDistribution.map((item) => item.optimized);

  if (!charts.stress) {
    charts.stress = new Chart(document.getElementById("stressChart"), {
      type: "line",
      data: {
        labels,
        datasets: [
          {
            label: "生成应力",
            data: generated,
            borderColor: "rgba(37, 99, 235, 0.85)",
            tension: 0.32,
            fill: false,
            pointBackgroundColor: "rgba(37, 99, 235, 0.85)",
          },
          {
            label: "优化应力",
            data: optimized,
            borderColor: "rgba(20, 184, 166, 0.9)",
            tension: 0.35,
            fill: false,
            pointBackgroundColor: "rgba(20, 184, 166, 0.9)",
          },
        ],
      },
      options: {
        plugins: { legend: { position: "bottom" } },
        scales: {
          x: { grid: { color: "rgba(15, 23, 42, 0.08)" } },
          y: { grid: { color: "rgba(15, 23, 42, 0.08)" } },
        },
      },
    });
  } else {
    charts.stress.data.labels = labels;
    charts.stress.data.datasets[0].data = generated;
    charts.stress.data.datasets[1].data = optimized;
    charts.stress.update();
  }

  const tbody = document.querySelector("#stressTable tbody");
  tbody.innerHTML = "";
  structural.stressDistribution.slice(0, 5).forEach((row) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${row.node}</td>
      <td>${row.elevation}</td>
      <td>${row.generated}</td>
      <td>${row.optimized}</td>`;
    tbody.appendChild(tr);
  });
}

function updateCorrectionsUI(corrections) {
  document.getElementById("residualDeviation").textContent = corrections.residualDeviation;
  document.getElementById("assemblySuitability").textContent = corrections.assemblySuitability;

  const labels = corrections.iterations.map((item) => `I${item.iteration}`);
  const deviations = corrections.iterations.map((item) => item.deviationMm);
  const offsets = corrections.iterations.map((item) => item.shapeOffsetDeg);

  if (!charts.deviation) {
    charts.deviation = new Chart(document.getElementById("deviationChart"), {
      data: {
        labels,
        datasets: [
          {
            type: "line",
            label: "尺寸偏差 (mm)",
            data: deviations,
            borderColor: "rgba(37, 99, 235, 0.85)",
            backgroundColor: "rgba(37, 99, 235, 0.2)",
            tension: 0.35,
            fill: true,
          },
          {
            type: "bar",
            label: "形态偏移 (°)",
            data: offsets,
            backgroundColor: "rgba(20, 184, 166, 0.65)",
            borderRadius: 6,
          },
        ],
      },
      options: {
        plugins: { legend: { position: "bottom" } },
        scales: {
          y: { beginAtZero: true, grid: { color: "rgba(15, 23, 42, 0.08)" } },
        },
      },
    });
  } else {
    charts.deviation.data.labels = labels;
    charts.deviation.data.datasets[0].data = deviations;
    charts.deviation.data.datasets[1].data = offsets;
    charts.deviation.update();
  }

  const tbody = document.querySelector("#iterationTable tbody");
  tbody.innerHTML = "";
  corrections.iterations.forEach((row) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${row.iteration}</td>
      <td>${row.deviationMm}</td>
      <td>${row.shapeOffsetDeg}</td>
      <td>${row.pathReweight}</td>`;
    tbody.appendChild(tr);
  });
}

function updateAssociationUI(association) {
  const labels = association.correlations.map((item) => item.stage);
  const values = association.correlations.map((item) => item.correlation);
  if (!charts.correlation) {
    charts.correlation = new Chart(document.getElementById("correlationChart"), {
      type: "bar",
      data: {
        labels,
        datasets: [
          {
            label: "设计-施工关联度",
            data: values,
            backgroundColor: "rgba(56, 189, 248, 0.8)",
            borderRadius: 12,
          },
        ],
      },
      options: {
        scales: {
          y: {
            beginAtZero: true,
            suggestedMax: 1,
            ticks: {
              callback: (value) => value.toFixed(1),
            },
            grid: { color: "rgba(15, 23, 42, 0.08)" },
          },
          x: { grid: { display: false } },
        },
        plugins: { legend: { display: false } },
      },
    });
  } else {
    charts.correlation.data.labels = labels;
    charts.correlation.data.datasets[0].data = values;
    charts.correlation.update();
  }

  const tbody = document.querySelector("#linkageTable tbody");
  tbody.innerHTML = "";
  association.linkageTable.forEach((row) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${row.stage}</td>
      <td>${row.designParam}</td>
      <td>${row.fieldValue}</td>
      <td>${row.syncLag}</td>`;
    tbody.appendChild(tr);
  });
}

function updateHistory(params, structural, corrections, remark) {
  const historyEntry = {
    timestamp: new Date().toLocaleString(),
    profile: params.id || document.getElementById("profileSelector").value,
    stabilityIndex: structural.stabilityIndex,
    assemblySuitability: corrections.assemblySuitability,
    remark,
  };
  analysisHistory.unshift(historyEntry);
  if (analysisHistory.length > 12) analysisHistory.pop();
  renderHistory();
}

function renderHistory() {
  const hint = document.getElementById("historyHint");
  const tbody = document.querySelector("#historyTable tbody");
  tbody.innerHTML = "";
  if (!analysisHistory.length) {
    hint.classList.remove("d-none");
    return;
  }
  hint.classList.add("d-none");
  analysisHistory.forEach((entry) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${entry.timestamp}</td>
      <td>${entry.profile}</td>
      <td>${entry.stabilityIndex}</td>
      <td>${entry.assemblySuitability}</td>
      <td>${entry.remark}</td>`;
    tbody.appendChild(tr);
  });
}

function average(values) {
  if (!values.length) return 0;
  return values.reduce((sum, value) => sum + value, 0) / values.length;
}

function formatLabel(label) {
  return label
    .replace(/([a-z])([A-Z])/g, "$1 $2")
    .replaceAll("_", " ")
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

function showToast(message) {
  const toast = document.createElement("div");
  toast.className = "toast align-items-center text-bg-danger border-0 position-fixed top-0 end-0 m-4";
  toast.style.zIndex = "1080";
  toast.innerHTML = `
    <div class="d-flex">
      <div class="toast-body">${message}</div>
      <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
    </div>`;
  document.body.appendChild(toast);
  const toastBootstrap = new bootstrap.Toast(toast, { delay: 4000 });
  toastBootstrap.show();
  toast.addEventListener("hidden.bs.toast", () => toast.remove());
}

function getFallbackDataset() {
  return {
    generatedAt: new Date().toISOString(),
    activeProfileId: "DX-01",
    profiles: [
      {
        id: "DX-01",
        name: "Hyperbolic East Atrium",
        module_width: 1.25,
        module_height: 3.45,
        module_depth: 0.24,
        curvature_radius: 28.0,
        tilt_angle: 3.5,
        mullion_spacing: 1.42,
        panel_thickness: 0.021,
        wind_speed: 34.0,
        thermal_gradient: 16.0,
        material: "aluminum",
      },
      {
        id: "DX-02",
        name: "North Tower Ribbon",
        module_width: 1.1,
        module_height: 3.0,
        module_depth: 0.22,
        curvature_radius: 45.0,
        tilt_angle: 2.0,
        mullion_spacing: 1.5,
        panel_thickness: 0.019,
        wind_speed: 38.0,
        thermal_gradient: 12.0,
        material: "glass",
      },
      {
        id: "DX-03",
        name: "Skywalk Link Gallery",
        module_width: 1.35,
        module_height: 3.8,
        module_depth: 0.27,
        curvature_radius: 24.0,
        tilt_angle: 5.2,
        mullion_spacing: 1.32,
        panel_thickness: 0.024,
        wind_speed: 42.0,
        thermal_gradient: 18.0,
        material: "steel",
      },
    ],
  };
}
