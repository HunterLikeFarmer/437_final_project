(function () {
  const Api = window.SmartToddlerApi;
  const Dashboard = window.SmartToddlerDashboard;
  const Controls = window.SmartToddlerControls;

  let statusTimer = null;
  let eventsTimer = null;
  let healthTimer = null;

  async function refreshHealth() {
    try {
      await Api.getHealth();
      Dashboard.setConnectionStatus(true, "Connected");
      return true;
    } catch (error) {
      Dashboard.setConnectionStatus(false, "Offline");
      return false;
    }
  }

  async function refreshDashboard() {
    try {
      const status = await Api.getStatus();
      Dashboard.renderStatusCards(status);
      Dashboard.renderAlerts(status.alerts || []);
      Dashboard.setConnectionStatus(true, "Connected");
    } catch (error) {
      Dashboard.setConnectionStatus(false, "Offline");
    }
  }

  async function refreshEvents() {
    try {
      const events = await Api.getEvents(50);
      Dashboard.renderEvents(events);
    } catch (error) {
      Dashboard.renderEvents({ events: [] });
    }
  }

  function initializeFooter() {
    const label = document.getElementById("api-base-label");
    if (!label) {
      return;
    }

    label.textContent = Api.getApiBaseUrl() || "same origin";
  }

  function initializeManualRefresh() {
    const button = document.getElementById("refresh-events");
    if (!button) {
      return;
    }

    button.addEventListener("click", async () => {
      button.disabled = true;
      await refreshEvents();
      button.disabled = false;
    });
  }

  function startPolling() {
    statusTimer = window.setInterval(refreshDashboard, 2000);
    eventsTimer = window.setInterval(refreshEvents, 5000);
    healthTimer = window.setInterval(refreshHealth, 10000);
  }

  function stopPolling() {
    [statusTimer, eventsTimer, healthTimer].forEach((timer) => {
      if (timer) {
        window.clearInterval(timer);
      }
    });
  }

  async function initializeDashboard() {
    initializeFooter();
    initializeManualRefresh();
    Controls.initializeControls();

    Dashboard.renderStatusCards({});
    Dashboard.renderAlerts([]);
    Dashboard.renderEvents({ events: [] });
    Dashboard.setConnectionStatus(false, "Connecting");

    await Promise.allSettled([
      refreshHealth(),
      refreshDashboard(),
      refreshEvents()
    ]);

    startPolling();
  }

  window.addEventListener("smart-toddler:command-sent", () => {
    refreshEvents();
    refreshDashboard();
  });

  window.addEventListener("beforeunload", stopPolling);

  document.addEventListener("DOMContentLoaded", initializeDashboard);
})();
