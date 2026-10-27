import { useEffect, useRef, useState } from "react";
import { MAX_MESSAGE_CHARS } from "../../config.js";
import { SendIcon } from "../common/icons.jsx";

export default function Composer({ onSend, disabled, autoFocusKey }) {
  const [text, setText] = useState("");
  const ref = useRef(null);
  const trimmed = text.trim();
  const tooLong = trimmed.length > MAX_MESSAGE_CHARS;
  const canSend = !disabled && trimmed.length > 0 && !tooLong;

  // grow with content up to ~6 lines
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 160)}px`;
  }, [text]);

  useEffect(() => {
    ref.current?.focus();
  }, [autoFocusKey]);

  function submit() {
    if (!canSend) return;
    onSend(trimmed);
    setText("");
  }

  function onKeyDown(e) {
    // Enter sends, Shift+Enter inserts a newline (ignored while an IME is composing)
    if (e.key === "Enter" && !e.shiftKey && !e.nativeEvent.isComposing) {
      e.preventDefault();
      submit();
    }
  }

  return (
    <div className="border-t border-stone-200 bg-white/90 p-3 backdrop-blur sm:p-4">
      <div className="mx-auto flex max-w-3xl items-end gap-2">
        <textarea
          ref={ref}
          rows={1}
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={onKeyDown}
          placeholder="Ask about outfits, colors, accessories…"
          aria-label="Message"
          className="max-h-40 min-h-[44px] flex-1 resize-none rounded-xl border border-stone-300 bg-white px-3 py-2.5 text-[15px] outline-none focus:ring-2 focus:ring-brand-300"
        />
        <button
          onClick={submit}
          disabled={!canSend}
          aria-label="Send message"
          className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-brand-600 text-white transition hover:bg-brand-700 disabled:cursor-not-allowed disabled:bg-stone-300"
        >
          <SendIcon />
        </button>
      </div>
      <div className="mx-auto mt-1 flex max-w-3xl justify-between px-1 text-xs text-stone-400">
        <span>Enter to send · Shift+Enter for a new line</span>
        {trimmed.length > MAX_MESSAGE_CHARS * 0.8 && (
          <span className={tooLong ? "text-red-600" : ""}>{trimmed.length}/{MAX_MESSAGE_CHARS}</span>
        )}
      </div>
    </div>
  );
}
