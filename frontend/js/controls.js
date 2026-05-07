(function () {
  const Api = window.SmartToddlerApi;
  const Dashboard = window.SmartToddlerDashboard;

  function parseValue(rawValue) {
    if (rawValue === "true") {
      return true;
    }
    if (rawValue === "false") {
      return false;
    }
    if (rawValue === undefined || rawValue === null || rawValue === "") {
      return null;
    }
    return rawValue;
  }

  function setButtonsDisabled(isDisabled) {
    document.querySelectorAll("#controls button").forEach((button) => {
      button.disabled = isDisabled;
    });
  }

  async function handleControlClick(event) {
    const button = event.target.closest("button[data-action]");
    if (!button) {
      return;
    }

    const action = button.dataset.action;
    const target = button.dataset.target;
    const value = parseValue(button.dataset.value);

    setButtonsDisabled(true);
    Dashboard.setCommandStatus("Sending...");

    try {
      if (button.dataset.resetAlert === "true") {
        await Api.resetAlert();
      }

      await Api.sendCommand(target, action, value);
      Dashboard.setCommandStatus("Sent");
      window.dispatchEvent(new CustomEvent("smart-toddler:command-sent"));
    } catch (error) {
      Dashboard.setCommandStatus(error.message || "Command failed");
    } finally {
      setButtonsDisabled(false);
    }
  }

  function initializeControls() {
    const controls = document.getElementById("controls");
    if (!controls) {
      return;
    }

    controls.addEventListener("click", handleControlClick);
  }

  window.SmartToddlerControls = {
    initializeControls
  };
})();
