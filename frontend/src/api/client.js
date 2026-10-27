import { API_BASE_URL, TOKEN_KEY } from "../config.js";

export class ApiError extends Error {
  constructor(status, body) {
    super(body?.detail || "Something went wrong.");
    this.status = status;
    this.code = body?.code || "error";
    this.fieldErrors = body?.errors || [];
    this.userMessageId = body?.user_message_id || null; // set when a chat turn failed after saving the message
  }
}

export const tokenStore = {
  get: () => localStorage.getItem(TOKEN_KEY),
  set: (t) => localStorage.setItem(TOKEN_KEY, t),
  clear: () => localStorage.removeItem(TOKEN_KEY),
};

let onUnauthorized = () => {};
export function setUnauthorizedHandler(fn) {
  onUnauthorized = fn;
}

async function request(path, { method = "GET", body, auth = true } = {}) {
  const headers = {};
  if (body !== undefined) headers["Content-Type"] = "application/json";
  const token = tokenStore.get();
  if (auth && token) headers.Authorization = `Bearer ${token}`;

  let res;
  try {
    res = await fetch(`${API_BASE_URL}${path}`, {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });
  } catch {
    throw new ApiError(0, { detail: "Cannot reach the server. Check your connection and try again.", code: "network_error" });
  }

  if (res.status === 204) return null;
  let data = null;
  try {
    data = await res.json();
  } catch {
    /* non-JSON error body */
  }
  if (!res.ok) {
    if (res.status === 401 && auth) onUnauthorized();
    throw new ApiError(res.status, data);
  }
  return data;
}

export const api = {
  register: (payload) => request("/api/auth/register", { method: "POST", body: payload, auth: false }),
  login: (payload) => request("/api/auth/login", { method: "POST", body: payload, auth: false }),
  logout: () => request("/api/auth/logout", { method: "POST" }),
  me: () => request("/api/auth/me"),
  listConversations: (limit = 50, offset = 0) => request(`/api/conversations?limit=${limit}&offset=${offset}`),
  createConversation: () => request("/api/conversations", { method: "POST" }),
  getConversation: (id, { limit = 50, before } = {}) =>
    request(`/api/conversations/${id}?limit=${limit}${before ? `&before=${before}` : ""}`),
  renameConversation: (id, title) => request(`/api/conversations/${id}`, { method: "PATCH", body: { title } }),
  deleteConversation: (id) => request(`/api/conversations/${id}`, { method: "DELETE" }),
  sendMessage: (id, content, retryMessageId) =>
    request(`/api/conversations/${id}/messages`, {
      method: "POST",
      body: { content, ...(retryMessageId ? { retry_message_id: retryMessageId } : {}) },
    }),
};
