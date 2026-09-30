const API_BASE_URL = "/api/v1";

async function apiRequest(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const config = { method: "GET", credentials: "same-origin", ...options };
    config.headers = { Accept: "application/json", ...(options.headers || {}) };

    if (config.body && !(config.body instanceof FormData) && typeof config.body !== "string") {
        config.headers["Content-Type"] = "application/json";
        config.body = JSON.stringify(config.body);
    }

    const response = await fetch(url, config);
    if (!response.ok) {
        let errorData = null;
        try { errorData = await response.json(); } catch (_) {}
        const error = new Error(`API request failed with status ${response.status}`);
        error.status = response.status;
        error.data = errorData;
        throw error;
    }
    if (response.status === 204) return null;
    return response.json();
}

window.api = { request: apiRequest };
