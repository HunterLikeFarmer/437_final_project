(function () {
  function byId(id) {
    return document.getElementById(id);
  }

  function valueOrDash(value, suffix = "") {
    if (value === null || value === undefined || value === "") {
      return "--";
    }
    return `${value}${suffix}`;
  }

  function formatTime(value) {
    if (!value) {
      return "--";
    }

    const date = new Date(value);
    if (Number.isNaN(date.getTime())) {
      return value;
    }

    return date.toLocaleString([], {
      month: "short",
      day: "numeric",
      hour: "numeric",
      minute: "2-digit",
      second: "2-digit"
    });
  }

  function text(value) {
    return String(value === null || value === undefined ? "" : value);
  }

  function deviceBoolean(value) {
    if (typeof value === "boolean") {
      return value;
    }
    if (typeof value === "number") {
      return value !== 0;
    }
    if (typeof value === "string") {
      return ["1", "true", "yes", "close", "near", "locked"].includes(value.trim().toLowerCase());
    }
    return false;
  }

  function formatLockStatus(value) {
    if (value === "locked") {
      return "Locked";
    }
    if (value === "unlocked") {
      return "Unlocked";
    }
    return "Unknown";
  }

  function setText(id, value) {
    const element = byId(id);
    if (element) {
      element.textContent = value;
    }
  }

  function metricCard(label, value, note, stateClass = "") {
    const article = document.createElement("article");
    article.className = `metric-card ${stateClass}`.trim();

    const labelElement = document.createElement("div");
    labelElement.className = "label";
    labelElement.textContent = label;

    const valueElement = document.createElement("div");
    valueElement.className = "value";
    valueElement.textContent = value;

    const noteElement = document.createElement("div");
    noteElement.className = "note";
    noteElement.textContent = note;

    article.append(labelElement, valueElement, noteElement);
    return article;
  }

  function replaceChildren(id, children) {
    const element = byId(id);
    if (element) {
      element.replaceChildren(...children);
    }
  }

  function renderStatusCards(status) {
    const environment = status.environment || {};
    const safety = status.safety || {};
    const lock = status.lock || {};
    const motion = status.motion || {};
    const sound = status.sound || {};
    const alerts = Array.isArray(status.alerts) ? status.alerts : [];

    const kidsClose = safety.kids_close === undefined || safety.kids_close === null
      ? deviceBoolean(safety.boundary_alert)
      : deviceBoolean(safety.kids_close);
    const lockStatus = lock.lock_status || "unknown";
    const lockValue = lock.lock_value;
    const motionDetected = Boolean(motion.detected);
    const environmentStatus = environment.status || "waiting";
    const safetyStatus = safety.status || "waiting";
    const lockNodeStatus = lock.status || "waiting";

    replaceChildren("environment-cards", [
      metricCard("Temperature", valueOrDash(environment.temperature, " C"), "Room sensor reading"),
      metricCard("Humidity", valueOrDash(environment.humidity, "%"), "Relative humidity"),
      metricCard("Light", valueOrDash(environment.light || environment.light_level), "Ambient level")
    ]);

    replaceChildren("safety-cards", [
      metricCard("Kid Close", kidsClose ? "Yes" : "No", "ESP32 value: kids_close", kidsClose ? "bad" : "good"),
      metricCard("Lock", formatLockStatus(lockStatus), `ESP32 value: ${valueOrDash(lockValue)}`, lockStatus === "locked" ? "good" : "warn"),
      metricCard("Node", safety.node_id || "--", `Lock node: ${lock.node_id || "--"}`, safetyStatus === "ok" && lockNodeStatus === "ok" ? "good" : "")
    ]);

    replaceChildren("activity-cards", [
      metricCard("Motion", motionDetected ? "Detected" : "Quiet", "Last motion signal", motionDetected ? "warn" : "good"),
      metricCard("Sound", valueOrDash(sound.level), "Raw sound sensor value"),
      metricCard("Node", environment.node_id || "--", `Status: ${environmentStatus}`, environmentStatus === "ok" ? "good" : "")
    ]);

    const timestamps = [
      environment.last_updated,
      safety.last_updated,
      lock.last_updated,
      motion.last_updated,
      sound.last_updated
    ].filter(Boolean);
    const lastUpdated = timestamps.length > 0 ? timestamps.sort().at(-1) : null;

    setText("environment-updated", `Updated ${formatTime(environment.last_updated)}`);
    setText("safety-updated", `Updated ${formatTime(safety.last_updated || lock.last_updated)}`);
    setText("activity-updated", `Updated ${formatTime(motion.last_updated || sound.last_updated)}`);
    setText("environment-node-id", environment.node_id || "--");
    setText("safety-node-id", safety.node_id || "--");
    setText("lock-node-id", lock.node_id || "--");
    setText("command-status", environment.status || safety.status || lock.status ? "Receiving" : "Listening");
    setText("last-update", formatTime(lastUpdated));
    setText("active-alert-count", text(alerts.length));
    setText("overall-status", alerts.length > 0 || kidsClose || motionDetected ? "Needs attention" : "All clear");

    if (window.SmartToddlerControls) {
      window.SmartToddlerControls.updateLockControl(status);
    }
  }

  function renderAlerts(alerts) {
    const alertList = Array.isArray(alerts) ? alerts : [];
    const container = byId("alerts");
    if (!container) {
      return;
    }

    if (alertList.length === 0) {
      container.innerHTML = '<div class="empty-state">No active alerts.</div>';
      return;
    }

    const nodes = alertList.map((alert) => {
      const severity = (alert.severity || "low").toLowerCase();
      const item = document.createElement("article");
      item.className = `alert-item ${severity}`;

      const title = document.createElement("div");
      title.className = "item-title";
      title.innerHTML = `<span></span><span class="severity-badge"></span>`;
      title.children[0].textContent = alert.message || alert.alert_type || "Active alert";
      title.children[1].textContent = severity;

      const meta = document.createElement("div");
      meta.className = "meta";
      meta.textContent = `${alert.source || alert.node_id || "system"} - ${formatTime(alert.timestamp)}`;

      item.append(title, meta);
      return item;
    });

    container.replaceChildren(...nodes);
  }

  function renderEvents(response) {
    const events = Array.isArray(response) ? response : response.events || [];
    const container = byId("event-log");
    if (!container) {
      return;
    }

    if (events.length === 0) {
      container.innerHTML = '<div class="empty-state">No recent events yet.</div>';
      return;
    }

    const nodes = events.map((event) => {
      const severity = (event.severity || "low").toLowerCase();
      const item = document.createElement("article");
      item.className = `event-item ${severity}`;

      const title = document.createElement("div");
      title.className = "item-title";
      title.innerHTML = `<span></span><span class="severity-badge"></span>`;
      title.children[0].textContent = event.message || event.event_type || "Event";
      title.children[1].textContent = event.event_type || severity;

      const meta = document.createElement("div");
      meta.className = "meta";
      meta.textContent = `${event.source || "system"} - ${formatTime(event.timestamp)}`;

      item.append(title, meta);
      return item;
    });

    container.replaceChildren(...nodes);
  }

  function setConnectionStatus(isConnected, label) {
    const element = byId("connection-status");
    if (!element) {
      return;
    }

    element.classList.toggle("connected", isConnected);
    element.classList.toggle("disconnected", !isConnected);
    element.lastChild.textContent = ` ${label || (isConnected ? "Connected" : "Offline")}`;
  }

  function setCommandStatus(message) {
    setText("command-status", message);
  }

  window.SmartToddlerDashboard = {
    renderStatusCards,
    renderAlerts,
    renderEvents,
    setConnectionStatus,
    setCommandStatus,
    formatTime
  };
})();
