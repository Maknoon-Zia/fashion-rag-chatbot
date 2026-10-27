import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { api, setUnauthorizedHandler, tokenStore } from "../api/client.js";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [status, setStatus] = useState(tokenStore.get() ? "loading" : "anonymous");
  const [notice, setNotice] = useState("");

  const clearSession = useCallback((message = "") => {
    tokenStore.clear();
    setUser(null);
    setStatus("anonymous");
    setNotice(message);
  }, []);

  // Any 401 from an authenticated call ends the session and returns to the login page.
  useEffect(() => {
    setUnauthorizedHandler(() => clearSession("Your session has expired. Please sign in again."));
  }, [clearSession]);

  // Restore the session after a page refresh.
  useEffect(() => {
    if (!tokenStore.get()) return;
    api
      .me()
      .then((u) => {
        setUser(u);
        setStatus("authenticated");
      })
      .catch(() => clearSession());
  }, [clearSession]);

  const login = useCallback(async (email, password) => {
    const res = await api.login({ email, password });
    tokenStore.set(res.access_token);
    setUser(res.user);
    setNotice("");
    setStatus("authenticated");
  }, []);

  const logout = useCallback(async () => {
    try {
      await api.logout();
    } catch {
      /* the local session is cleared regardless */
    }
    clearSession();
  }, [clearSession]);

  const value = useMemo(
    () => ({ user, status, notice, login, logout, register: api.register, clearNotice: () => setNotice("") }),
    [user, status, notice, login, logout]
  );
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside AuthProvider");
  return ctx;
}
