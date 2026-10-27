const METRIC_LABELS = {
  train_accuracy: "Train accuracy",
  test_accuracy: "Test accuracy",
  train_f1_macro: "Train F1",
  test_f1_macro: "Test F1",
  train_r2: "Train R²",
  test_r2: "Test R²",
  train_mae: "Train MAE",
  test_mae: "Test MAE",
  n_train: "Training rows",
  n_test: "Test rows",
  n_features: "Features",
};

const FIGURE_LABELS = {
  scores: "Train and test scores",
  confusion: "Confusion matrix",
  projection: "Two-feature view",
  importance: "Feature weight",
  predicted: "Predicted and actual",
  residuals: "Residuals",
};

const form = document.querySelector("#job-form");
const formStatus = document.querySelector("#form-status");
const formError = document.querySelector("#form-error");
const taskSelect = document.querySelector("#task");
const datasetSelect = document.querySelector("#dataset");
const estimatorSelect = document.querySelector("#estimator");
const datasetDescription = document.querySelector("#dataset-description");
const estimatorDescription = document.querySelector("#estimator-description");
const datasetParameters = document.querySelector("#dataset-parameters");
const estimatorParameters = document.querySelector("#estimator-parameters");
const sharedParameters = document.querySelector("#shared-parameters");
const submitButton = document.querySelector("#submit");
const jobList = document.querySelector("#job-list");
const detail = document.querySelector("#detail");
const boardNote = document.querySelector("#board-note");

let catalogData = null;
let jobs = [];
let selectedId = null;
let posting = false;
let listSignature = "";
let detailSignature = "";

form.addEventListener("submit", onSubmit);
taskSelect.addEventListener("change", () => {
  fillDatasets();
  fillEstimators();
});
// Rebuild that dataset's fields before a submit reads them.
datasetSelect.addEventListener("change", () => {
  showSelectedDataset();
  fillEstimators();
});
estimatorSelect.addEventListener("change", renderEstimatorParameters);

boot();

async function boot() {
  formStatus.textContent = "Reading the catalog…";
  try {
    const response = await fetch("/api/catalog");
    if (!response.ok) {
      throw new Error("catalog failed");
    }
    catalogData = await response.json();
    formStatus.textContent = "";
    fillTasks();
    fillShared();
    fillDatasets();
    fillEstimators();
    setFormEnabled(true);
    await refreshJobs();
    // The fit runs on a worker. Poll until its figures are ready.
    window.setInterval(() => {
      refreshJobs();
    }, 1000);
  } catch (error) {
    formStatus.textContent = "The catalog did not load. Refresh the page to try again.";
    submitButton.disabled = true;
  }
}

function fillTasks() {
  taskSelect.replaceChildren();
  for (const task of catalogData.tasks) {
    taskSelect.append(option(task.id, task.label));
  }
}

function fillDatasets() {
  const current = datasetSelect.value;
  datasetSelect.replaceChildren();
  for (const dataset of datasetsForTask()) {
    datasetSelect.append(option(dataset.id, dataset.label));
  }
  if ([...datasetSelect.options].some((item) => item.value === current)) {
    datasetSelect.value = current;
  }
  showSelectedDataset();
}

function showSelectedDataset() {
  const dataset = selectedDataset();
  datasetDescription.textContent = dataset ? dataset.description : "";
  renderParameterBlock(datasetParameters, dataset ? dataset.parameters : [], "data");
}

function fillEstimators() {
  const current = estimatorSelect.value;
  estimatorSelect.replaceChildren();
  const task = selectedDataset() ? selectedDataset().task : taskSelect.value;
  for (const estimator of catalogData.estimators) {
    if (estimator.task === task) {
      estimatorSelect.append(option(estimator.id, estimator.label));
    }
  }
  if ([...estimatorSelect.options].some((item) => item.value === current)) {
    estimatorSelect.value = current;
  }
  renderEstimatorParameters();
}

function renderEstimatorParameters() {
  const estimator = selectedEstimator();
  estimatorDescription.textContent = estimator ? estimator.description : "";
  renderParameterBlock(
    estimatorParameters,
    estimator ? estimator.parameters : [],
    "est",
  );
}

function fillShared() {
  renderParameterBlock(sharedParameters, catalogData.shared_parameters, "shared");
}

function datasetsForTask() {
  return catalogData.datasets.filter((dataset) => dataset.task === taskSelect.value);
}

function selectedDataset() {
  return catalogData.datasets.find((dataset) => dataset.id === datasetSelect.value);
}

function selectedEstimator() {
  return catalogData.estimators.find((estimator) => estimator.id === estimatorSelect.value);
}

function renderParameterBlock(container, specs, prefix) {
  container.replaceChildren();
  for (const spec of specs) {
    container.append(field(spec, `${prefix}-${spec.name}`));
  }
}

function field(spec, id) {
  if (spec.type === "bool") {
    const label = document.createElement("label");
    label.className = "check";
    const input = document.createElement("input");
    input.type = "checkbox";
    input.id = id;
    input.checked = Boolean(spec.default);
    label.append(input, document.createTextNode(spec.label));
    return label;
  }
  const label = document.createElement("label");
  label.textContent = spec.label;
  label.append(control(spec, id));
  return label;
}

function control(spec, id) {
  if (spec.type === "choice") {
    const select = document.createElement("select");
    select.id = id;
    for (const choice of spec.choices) {
      select.append(option(choice, choice));
    }
    select.value = spec.default;
    return select;
  }
  const input = document.createElement("input");
  input.id = id;
  input.type = "number";
  if (spec.type === "int") {
    input.step = "1";
  } else if (spec.step != null) {
    input.step = String(spec.step);
  }
  if (!spec.nullable) {
    input.required = true;
    input.min = String(spec.min);
    input.max = String(spec.max);
    input.value = String(spec.default);
  } else {
    input.min = String(spec.min);
    input.max = String(spec.max);
    input.placeholder = "no limit";
    input.value = spec.default == null ? "" : String(spec.default);
  }
  return input;
}

function option(value, label) {
  const node = document.createElement("option");
  node.value = value;
  node.textContent = label;
  return node;
}

function readSpecs(specs, prefix) {
  const values = {};
  for (const spec of specs) {
    values[spec.name] = readControl(spec, document.querySelector(`#${prefix}-${spec.name}`));
  }
  return values;
}

function readControl(spec, input) {
  if (!input) {
    throw new Error(`Missing control for ${spec.name}.`);
  }
  if (spec.type === "bool") {
    return input.checked;
  }
  if (spec.type === "choice") {
    return input.value;
  }
  // An empty optional number means "no limit", stored by the server as null.
  if (spec.nullable && input.value === "") {
    return null;
  }
  const number = Number(input.value);
  if (spec.type === "int") {
    return Math.trunc(number);
  }
  return number;
}

async function onSubmit(event) {
  event.preventDefault();
  formError.textContent = "";
  if (!form.reportValidity()) {
    return;
  }
  let payload;
  try {
    payload = buildPayload();
  } catch (error) {
    formError.textContent = error.message;
    return;
  }
  posting = true;
  setFormEnabled(false);
  submitButton.textContent = "Queuing…";
  try {
    const response = await fetch("/api/jobs", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const body = await response.json();
    if (!response.ok) {
      formError.textContent = body.error || "The job was rejected.";
      return;
    }
    selectedId = body.id;
    detailSignature = "";
    await refreshJobs();
  } catch (error) {
    formError.textContent = "The bench could not queue that job.";
  } finally {
    posting = false;
    submitButton.textContent = "Run learning job";
    setFormEnabled(true);
  }
}

function buildPayload() {
  const dataset = selectedDataset();
  const estimator = selectedEstimator();
  if (!dataset || !estimator) {
    throw new Error("Choose a dataset and an estimator.");
  }
  const shared = readSpecs(catalogData.shared_parameters, "shared");
  return {
    dataset: dataset.id,
    estimator: estimator.id,
    dataset_parameters: readSpecs(dataset.parameters, "data"),
    parameters: readSpecs(estimator.parameters, "est"),
    test_size: shared.test_size,
    random_state: shared.random_state,
  };
}

function setFormEnabled(enabled) {
  const locked = !enabled || posting || !catalogData;
  for (const control of form.querySelectorAll("input, select, button")) {
    control.disabled = locked;
  }
}

async function cancelJob(jobId) {
  try {
    await fetch(`/api/jobs/${jobId}/cancel`, { method: "POST" });
    detailSignature = "";
    listSignature = "";
    await refreshJobs();
  } catch (error) {
    boardNote.textContent = "The cancel request did not reach the bench.";
  }
}

async function refreshJobs() {
  try {
    const response = await fetch("/api/jobs");
    if (!response.ok) {
      boardNote.textContent = "The job list could not be refreshed.";
      return;
    }
    const body = await response.json();
    jobs = body.jobs;
    if (selectedId && !jobs.some((job) => job.id === selectedId)) {
      selectedId = null;
    }
    if (!selectedId && jobs.length) {
      selectedId = jobs[0].id;
    }
    renderJobs();
    boardNote.textContent = jobs.some((job) => job.status === "running" || job.status === "queued")
      ? "A fit is on a worker. This page stays available."
      : "A fit runs in the background. You can queue another.";
  } catch (error) {
    boardNote.textContent = "The job list could not be refreshed.";
  }
}

function renderJobs() {
  // Redraw only when status, stage, or the selected job changes.
  // A poll that changes nothing else would otherwise rebuild the buttons.
  const signature = jobs
    .map((job) => `${job.id}:${job.status}:${job.stage}`)
    .join("|") + `#${selectedId}`;
  if (signature !== listSignature) {
    listSignature = signature;
    jobList.replaceChildren();
    for (const job of jobs) {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "job";
      if (job.id === selectedId) {
        button.setAttribute("aria-current", "true");
      }
      const title = document.createElement("strong");
      title.textContent = `${job.request.estimator_label} on ${job.request.dataset_label}`;
      const meta = document.createElement("span");
      meta.textContent = `${job.status} · ${formatTime(job.created_at)}`;
      button.append(title, meta);
      button.addEventListener("click", () => {
        selectedId = job.id;
        listSignature = "";
        detailSignature = "";
        renderJobs();
      });
      jobList.append(button);
    }
  }
  renderDetail();
}

function renderDetail() {
  const job = jobs.find((item) => item.id === selectedId);
  if (!job) {
    detailSignature = "";
    detail.replaceChildren();
    const empty = document.createElement("p");
    empty.className = "empty";
    empty.textContent = "No jobs yet. Set the parameters and run a learning job.";
    detail.append(empty);
    return;
  }
  const signature = JSON.stringify([
    job.id,
    job.status,
    job.stage,
    job.error,
    job.finished_at,
    job.figures,
    job.metrics,
  ]);
  if (signature === detailSignature) {
    return;
  }
  detailSignature = signature;
  detail.replaceChildren();
  const heading = document.createElement("h2");
  heading.textContent = `${job.request.estimator_label} on ${job.request.dataset_label}`;
  const chip = document.createElement("span");
  chip.className = `chip ${job.status}`;
  chip.textContent = job.status;
  const stage = document.createElement("p");
  stage.className = "meta";
  stage.textContent = stageText(job);
  detail.append(heading, chip, stage);
  if (job.status === "failed" && job.error) {
    const error = document.createElement("p");
    error.className = "form-error";
    error.textContent = job.error;
    detail.append(error);
  }
  if (job.status === "queued" || job.status === "running") {
    const cancel = document.createElement("button");
    cancel.type = "button";
    cancel.className = "secondary";
    cancel.textContent = "Cancel job";
    cancel.addEventListener("click", () => {
      cancelJob(job.id);
    });
    detail.append(cancel);
  }
  if (job.metrics) {
    detail.append(metricsTable(job.metrics));
  }
  if (job.figures.length) {
    const figures = document.createElement("div");
    figures.className = "figures";
    for (const name of job.figures) {
      const figure = document.createElement("figure");
      const image = document.createElement("img");
      image.alt = FIGURE_LABELS[name] || name;
      image.src = `/api/jobs/${job.id}/figures/${name}.png`;
      const caption = document.createElement("figcaption");
      caption.textContent = FIGURE_LABELS[name] || name;
      figure.append(image, caption);
      figures.append(figure);
    }
    detail.append(figures);
  }
}

function metricsTable(metrics) {
  const wrap = document.createElement("div");
  wrap.className = "metrics";
  for (const [key, label] of Object.entries(METRIC_LABELS)) {
    if (metrics[key] == null) {
      continue;
    }
    const card = document.createElement("div");
    card.className = "metric";
    const value = document.createElement("b");
    value.textContent = formatMetric(metrics[key]);
    card.append(value, document.createTextNode(label));
    wrap.append(card);
  }
  return wrap;
}

function formatMetric(value) {
  if (typeof value === "number" && !Number.isInteger(value)) {
    return value.toFixed(3);
  }
  return String(value);
}

function stageText(job) {
  if (job.status === "queued") {
    return "Waiting for a worker.";
  }
  if (job.status === "running") {
    return "Fitting on a worker. Figures appear when the job finishes.";
  }
  if (job.status === "cancelled") {
    return "Cancelled before the figures were kept.";
  }
  if (job.status === "succeeded") {
    return `Finished at ${formatTime(job.finished_at)}.`;
  }
  return job.stage;
}

function formatTime(iso) {
  if (!iso) {
    return "";
  }
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) {
    return iso;
  }
  return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
}
