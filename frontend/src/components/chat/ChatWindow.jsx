import { useEffect, useRef } from "react";
import { MenuIcon } from "../common/icons.jsx";
import Spinner from "../common/Spinner.jsx";
import Composer from "./Composer.jsx";
import EmptyState from "./EmptyState.jsx";
import ErrorBanner from "./ErrorBanner.jsx";
import MessageBubble from "./MessageBubble.jsx";

function Thinking() {
  return (
    <div className="flex justify-start" aria-live="polite">
      <div className="flex items-center gap-1.5 rounded-2xl rounded-bl-md bg-white px-4 py-3 shadow-sm ring-1 ring-stone-200" role="status" aria-label="Assistant is typing">
        {[0, 150, 300].map((d) => (
          <span key={d} className="h-2 w-2 animate-bounce rounded-full bg-brand-400" style={{ animationDelay: `${d}ms` }} />
        ))}
      </div>
    </div>
  );
}

export default function ChatWindow({ conversation, chat, busyCreating, topError, onMenu, onSend, onReloadHistory }) {
  const endRef = useRef(null);
  const hasConversation = Boolean(conversation);
  const { messages, sending, loadingHistory } = chat;
  const lastFailed = [...messages].reverse().find((m) => m.status === "failed");

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages.length, sending]);

  const showEmpty = !loadingHistory && !chat.historyError && messages.length === 0;

  return (
    <main className="flex h-full min-w-0 flex-1 flex-col">
      <header className="flex items-center gap-3 border-b border-stone-200 bg-white px-3 py-3 sm:px-5">
        <button onClick={onMenu} aria-label="Open conversations" className="rounded-lg p-1.5 text-stone-600 hover:bg-stone-100 md:hidden">
          <MenuIcon />
        </button>
        <h1 className="truncate font-display text-lg font-semibold text-stone-900">
          {conversation?.title || "Fashion Styling Assistant"}
        </h1>
      </header>

      <div className="flex-1 overflow-y-auto px-3 py-4 sm:px-5" role="log" aria-label="Conversation">
        <div className="mx-auto flex max-w-3xl flex-col gap-4">
          {loadingHistory && (
            <div className="flex justify-center py-10"><Spinner className="h-6 w-6" /></div>
          )}
          {chat.historyError && <ErrorBanner message={chat.historyError} onRetry={onReloadHistory} retryLabel="Reload" />}
          {chat.hasMore && (
            <button onClick={chat.loadOlder} className="self-center rounded-full border border-stone-300 px-4 py-1 text-xs text-stone-600 hover:bg-stone-100">
              Load earlier messages
            </button>
          )}
          {showEmpty && <EmptyState onPick={onSend} disabled={sending || busyCreating} />}
          {messages.map((m) => (
            <MessageBubble key={m.id} message={m} onRetry={chat.retry} retryDisabled={sending} />
          ))}
          {sending && <Thinking />}
          <div ref={endRef} />
        </div>
      </div>

      <div className="space-y-2 px-3 sm:px-5">
        <ErrorBanner message={topError} />
        <ErrorBanner
          message={chat.sendError}
          onRetry={lastFailed && !sending ? () => chat.retry(lastFailed) : undefined}
        />
      </div>
      <Composer onSend={onSend} disabled={sending || busyCreating || (hasConversation && !chat.ready && !chat.historyError)} autoFocusKey={conversation?.id} />
    </main>
  );
}
