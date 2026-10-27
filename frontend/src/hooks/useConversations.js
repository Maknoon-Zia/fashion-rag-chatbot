import { useCallback, useEffect, useState } from "react";
import { api } from "../api/client.js";

const PAGE = 50;

/** Sidebar data: list, create, rename, delete. The server is the source of truth. */
export function useConversations() {
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const res = await api.listConversations(PAGE, 0);
      setItems(res.items);
      setTotal(res.total);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const loadMore = useCallback(async () => {
    try {
      const res = await api.listConversations(PAGE, items.length);
      setItems((prev) => [...prev, ...res.items.filter((n) => !prev.some((p) => p.id === n.id))]);
      setTotal(res.total);
    } catch (e) {
      setError(e.message);
    }
  }, [items.length]);

  const create = useCallback(async () => {
    const conv = await api.createConversation();
    setItems((prev) => [conv, ...prev]);
    setTotal((t) => t + 1);
    return conv;
  }, []);

  const rename = useCallback(async (id, title) => {
    const updated = await api.renameConversation(id, title);
    setItems((prev) => prev.map((c) => (c.id === id ? updated : c)));
  }, []);

  const remove = useCallback(async (id) => {
    await api.deleteConversation(id);
    setItems((prev) => prev.filter((c) => c.id !== id));
    setTotal((t) => Math.max(0, t - 1));
  }, []);

  /** Called after a chat turn: moves the conversation to the top with its new title/time. */
  const applyUpdate = useCallback((conv) => {
    setItems((prev) => [conv, ...prev.filter((c) => c.id !== conv.id)]);
  }, []);

  return { items, total, loading, error, reload: load, loadMore, create, rename, remove, applyUpdate };
}
