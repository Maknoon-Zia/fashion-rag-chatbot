export const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8000").replace(/\/$/, "");
export const TOKEN_KEY = "fashion_chatbot_token";
export const MAX_MESSAGE_CHARS = 2000; // keep in sync with MAX_MESSAGE_CHARS in backend/.env
