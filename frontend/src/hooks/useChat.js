import { useCallback, useEffect, useRef, useState } from "react";
import { api } from "../api/client.js";

let tempCounter = 0;

/**
 * Messages of the active conversation plus sending/retrying.
 * A user message that could not be answered stays visible with status "failed" and a Retry action.
 */
export function useChat(conversationId, { onConversationUpdated }) {
  const [messages, setMessages] = useState([]);
  const [ready, setReady] = useState(false); // history for the active conversation has loaded
  const [loadingHistory, setLoadingHistory] = useState(false);
  const [historyError, setHistoryError] = useState("");
  const [hasMore, setHasMore] = useState(false);
  const [nextBefore, setNextBefore] = useState(null);
  const [sending, setSending] = useState(false);
  const [sendError, setSendError] = useState("");
  const activeRef = useRef(conversationId);
  const sendingRef = useRef(false);

  const loadHistory = useCallback(async (id) => {
    setLoadingHistory(true);
    setHistoryError("");
    setReady(false);
    try {
      const res = await api.getConversation(id);
      if (activeRef.current !== id) return; // user switched conversations meanwhile
      setMessages(res.messages);
      setHasMore(res.has_more);
      setNextBefore(res.next_before);
      setReady(true);
    } catch (e) {
      if (activeRef.current === id) setHistoryError(e.message);
    } finally {
      if (activeRef.current === id) setLoadingHistory(false);
    }
  }, []);

  useEffect(() => {
    activeRef.current = conversationId;
    setMessages([]);
    setSendError("");
    setHasMore(false);
    setNextBefore(null);
    setReady(false);
    if (conversationId) loadHistory(conversationId);
  }, [conversationId, loadHistory]);

  const loadOlder = useCallback(async () => {
    if (!conversationId || !nextBefore) return;
    try {
      const res = await api.getConversation(conversationId, { before: nextBefore });
      if (activeRef.current !== conversationId) return;
      setMessages((prev) => [...res.messages, ...prev]);
      setHasMore(res.has_more);
      setNextBefore(res.next_before);
    } catch (e) {
      setHistoryError(e.message);
    }
  }, [conversationId, nextBefore]);

  /** bubbleId: reuse an existing (failed) bubble when retrying. */
  const perform = useCallback(
    async (content, { retryMessageId = null, bubbleId = null } = {}) => {
      if (!conversationId || sendingRef.current) return;
      sendingRef.current = true;
      setSending(true);
      setSendError("");
      const id = conversationId;
      const tempId = bubbleId || `tmp-${++tempCounter}`;

      setMessages((prev) =>
        bubbleId
          ? prev.map((m) => (m.id === bubbleId ? { ...m, status: "pending" } : m))
          : [...prev, { id: tempId, role: "user", content, status: "pending", created_at: new Date().toISOString() }]
      );
      try {
        const res = await api.sendMessage(id, content, retryMessageId);
        onConversationUpdated?.(res.conversation);
        if (activeRef.current === id) {
          setMessages((prev) => [
            ...prev.filter((m) => m.id !== tempId && m.id !== res.user_message.id),
            res.user_message,
            res.assistant_message,
          ]);
        }
      } catch (e) {
        if (activeRef.current === id) {
          // userMessageId => the server saved the message but could not answer; otherwise it was not saved.
          setMessages((prev) =>
            prev.map((m) =>
              m.id === tempId ? { ...m, id: e.userMessageId || m.id, status: "failed", saved: Boolean(e.userMessageId) } : m
            )
          );
          setSendError(e.message);
        }
      } finally {
        sendingRef.current = false;
        setSending(false);
      }
    },
    [conversationId, onConversationUpdated]
  );

  const send = useCallback((content) => perform(content), [perform]);

  const retry = useCallback(
    (message) => perform(message.content, { retryMessageId: message.saved ? message.id : null, bubbleId: message.id }),
    [perform]
  );

  const reload = useCallback(() => conversationId && loadHistory(conversationId), [conversationId, loadHistory]);

  return { reload, messages, ready, loadingHistory, historyError, hasMore, loadOlder, sending, sendError, send, retry };
}
