import { useCallback, useEffect, useState } from "react";
import { useAuth } from "../../context/AuthContext.jsx";
import { useChat } from "../../hooks/useChat.js";
import { useConversations } from "../../hooks/useConversations.js";
import ChatWindow from "../chat/ChatWindow.jsx";
import Sidebar from "./Sidebar.jsx";

export default function AppShell() {
  const { user, logout } = useAuth();
  const convs = useConversations();
  const [activeId, setActiveId] = useState(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [creating, setCreating] = useState(false);
  const [pendingSend, setPendingSend] = useState(null);
  const [topError, setTopError] = useState("");

  const chat = useChat(activeId, { onConversationUpdated: convs.applyUpdate });
  const activeConversation = convs.items.find((c) => c.id === activeId) || null;

  async function handleDelete(id) {
    await convs.remove(id); // throws on failure so the dialog can show the error
    if (id === activeId) setActiveId(null);
  }

  // A first message typed with no open conversation: create one, then send once its history is ready.
  useEffect(() => {
    if (activeId && pendingSend && chat.ready) {
      chat.send(pendingSend);
      setPendingSend(null);
    }
  }, [activeId, pendingSend, chat.ready]); // eslint-disable-line react-hooks/exhaustive-deps

  const createAndOpen = useCallback(async () => {
    setCreating(true);
    setTopError("");
    try {
      const conv = await convs.create();
      setActiveId(conv.id);
      return conv;
    } catch (e) {
      setTopError(e.message);
      return null;
    } finally {
      setCreating(false);
    }
  }, [convs.create]); // eslint-disable-line react-hooks/exhaustive-deps

  async function handleNew() {
    setDrawerOpen(false);
    await createAndOpen();
  }

  async function handleSend(text) {
    setTopError("");
    if (activeId) return chat.send(text);
    const conv = await createAndOpen();
    if (conv) setPendingSend(text);
  }

  return (
    <div className="flex h-dvh overflow-hidden bg-stone-50">
      <Sidebar
        convs={convs}
        activeId={activeId}
        user={user}
        creating={creating}
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        onNew={handleNew}
        onSelect={(id) => { setActiveId(id); setDrawerOpen(false); setTopError(""); }}
        onDelete={handleDelete}
        onLogout={logout}
      />
      <ChatWindow
        conversation={activeConversation}
        chat={chat}
        busyCreating={creating}
        topError={topError}
        onMenu={() => setDrawerOpen(true)}
        onSend={handleSend}
        onReloadHistory={chat.reload}
      />
    </div>
  );
}
