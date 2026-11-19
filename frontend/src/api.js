// Relative paths: in production FastAPI serves the UI and the API from one origin.
// In dev, vite.config.js proxies these paths to http://localhost:8000.

async function request(path, options = {}) {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  let data = null;
  try {
    data = await res.json();
  } catch {
    /* non-JSON body */
  }

  if (!res.ok) {
    const detail = data?.detail;
    throw new Error(
      typeof detail === "string" ? detail : `Request failed (${res.status})`
    );
  }
  return data;
}

export const fetchItems = () => request("/items");

export const ingestContent = (payload) =>
  request("/ingest", { method: "POST", body: JSON.stringify(payload) });

export const queryKnowledge = (question) =>
  request("/query", {
    method: "POST",
    body: JSON.stringify({ question, top_k: 5 }),
  });