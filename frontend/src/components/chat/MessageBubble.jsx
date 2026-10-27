import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { AlertIcon, RetryIcon } from "../common/icons.jsx";
import SourceList from "./SourceList.jsx";


const time = (iso) => new Date(iso).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

export default function MessageBubble({ message, onRetry, retryDisabled }) {
  const isUser = message.role === "user";
  const failed = message.status === "failed";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div className={`max-w-[92%] sm:max-w-[80%] ${isUser ? "items-end" : "items-start"} flex flex-col`}>
        <div
          className={`break-words rounded-2xl px-4 py-2.5 text-[15px] leading-relaxed ${isUser
              ? `rounded-br-md ${failed ? "bg-red-50 text-stone-800 ring-1 ring-red-300" : "bg-brand-600 text-white"} ${message.status === "pending" ? "opacity-70" : ""}`
              : "rounded-bl-md bg-white text-stone-800 shadow-sm ring-1 ring-stone-200"
            }`}
        >
          {isUser ? (
            <p className="whitespace-pre-wrap">{message.content}</p>
          ) : (
            <div className="prose-chat">
              <ReactMarkdown
               remarkPlugins={[remarkGfm]}
                components={{
                  a: (props) => <a {...props} target="_blank" rel="noopener noreferrer" />,
                  // wide tables scroll inside the bubble instead of breaking the layout
                  table: ({ node, ...props }) => (
                    <div className="table-wrap"><table {...props} /></div>
                  ),
                }}
                >
                {message.content}
              </ReactMarkdown>
            </div>
          )}
          {!isUser && <SourceList sources={message.retrieval?.sources} />}
        </div>

        <div className="mt-1 flex items-center gap-2 px-1 text-xs text-stone-400">
          {failed ? (
            <>
              <span className="flex items-center gap-1 text-red-600"><AlertIcon size={13} /> Not answered</span>
              <button
                onClick={() => onRetry(message)}
                disabled={retryDisabled}
                className="flex items-center gap-1 font-medium text-brand-700 hover:underline disabled:opacity-50"
              >
                <RetryIcon size={13} /> Retry
              </button>
            </>
          ) : message.status === "pending" ? (
            <span>Sending…</span>
          ) : (
            <span>{time(message.created_at)}</span>
          )}
        </div>
      </div>
    </div>
  );
}
