(function () {
  const configuredBaseUrl = window.SMART_TODDLER_API_BASE_URL;
  const API_BASE_URL = configuredBaseUrl || (window.location.protocol === "file:" ? "http://localhost:5000" : "");

  function getApiBaseUrl() {
    return API_BASE_URL;
  }

  async function requestJson(path, options) {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      headers: {
        "Content-Type": "application/json"
      },
      ...options
    });

    let payload = {};
    try {
      payload = await response.json();
    } catch (error) {
      payload = {};
    }

    if (!response.ok) {
      const message = payload.message || payload.error || `Request failed with status ${response.status}`;
      throw new Error(message);
    }

    return payload;
  }

  async function getHealth() {
    return requestJson("/api/health");
  }

  async function getStatus() {
    return requestJson("/api/status");
  }

  async function getEvents(limit = 50) {
    return requestJson(`/api/events?limit=${encodeURIComponent(limit)}`);
  }

  async function sendCommand(target, command, value) {
    return requestJson("/api/commands", {
      method: "POST",
      body: JSON.stringify({ target, command, value })
    });
  }

  async function resetAlert(alertId) {
    const body = alertId ? { alert_id: alertId } : {};
    return requestJson("/api/reset-alert", {
      method: "POST",
      body: JSON.stringify(body)
    });
  }

  window.SmartToddlerApi = {
    getApiBaseUrl,
    getHealth,
    getStatus,
    getEvents,
    sendCommand,
    resetAlert
  };
})();
