import { groupConversations } from "../../utils/dateGroups.js";
import { LogoutIcon, PlusIcon, XIcon } from "../common/icons.jsx";
import Spinner from "../common/Spinner.jsx";
import ConversationItem from "./ConversationItem.jsx";

export default function Sidebar({ convs, activeId, user, creating, open, onClose, onNew, onSelect, onDelete, onLogout }) {
  const groups = groupConversations(convs.items);

  return (
    <>
      {open && <div className="fixed inset-0 z-30 bg-black/40 md:hidden" onClick={onClose} aria-hidden="true" />}
      <aside
        aria-label="Conversations"
        className={`fixed inset-y-0 left-0 z-40 flex w-72 flex-col border-r border-stone-200 bg-stone-100 transition-transform duration-200 md:static md:translate-x-0 ${open ? "translate-x-0" : "-translate-x-full"}`}
      >
        <div className="flex items-center justify-between px-4 pb-2 pt-4">
          <span className="font-display text-lg font-semibold text-brand-800">Styling Assistant</span>
          <button onClick={onClose} aria-label="Close conversations" className="rounded-lg p-1.5 text-stone-500 hover:bg-stone-200 md:hidden"><XIcon /></button>
        </div>

        <div className="px-3 pb-2">
          <button
            onClick={onNew}
            disabled={creating}
            className="flex w-full items-center justify-center gap-2 rounded-lg bg-brand-600 px-3 py-2 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-60"
          >
            {creating ? <Spinner className="h-4 w-4 !text-white" /> : <PlusIcon size={16} />} New chat
          </button>
        </div>

        <nav className="flex-1 overflow-y-auto px-2 pb-2">
          {convs.loading && <div className="flex justify-center py-6"><Spinner /></div>}
          {convs.error && (
            <p className="m-2 rounded-lg bg-red-50 p-2 text-xs text-red-700" role="alert">
              {convs.error}{" "}
              <button onClick={convs.reload} className="font-medium underline">Retry</button>
            </p>
          )}
          {!convs.loading && !convs.error && groups.length === 0 && (
            <p className="px-3 py-6 text-center text-sm text-stone-500">No conversations yet. Start a new chat!</p>
          )}
          {groups.map((g) => (
            <section key={g.label} className="mb-3">
              <h2 className="px-3 pb-1 pt-2 text-xs font-semibold uppercase tracking-wide text-stone-400">{g.label}</h2>
              {g.items.map((c) => (
                <ConversationItem
                  key={c.id}
                  conversation={c}
                  active={c.id === activeId}
                  onSelect={onSelect}
                  onRename={convs.rename}
                  onDelete={onDelete}
                />
              ))}
            </section>
          ))}
          {convs.items.length < convs.total && (
            <button onClick={convs.loadMore} className="mx-auto mb-2 block rounded-full border border-stone-300 px-4 py-1 text-xs text-stone-600 hover:bg-stone-200">
              Load more
            </button>
          )}
        </nav>

        <div className="flex items-center gap-2 border-t border-stone-200 px-3 py-3">
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-brand-200 text-sm font-semibold text-brand-800">
            {user.name.slice(0, 1).toUpperCase()}
          </div>
          <div className="min-w-0 flex-1">
            <p className="truncate text-sm font-medium text-stone-800">{user.name}</p>
            <p className="truncate text-xs text-stone-500">{user.email}</p>
          </div>
          <button onClick={onLogout} aria-label="Sign out" title="Sign out" className="rounded-lg p-2 text-stone-500 hover:bg-stone-200 hover:text-stone-800"><LogoutIcon size={18} /></button>
        </div>
      </aside>
    </>
  );
}
