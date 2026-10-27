/**
 * Group conversations for the sidebar using the browser's local timezone.
 * Input must already be sorted newest-activity-first (the API does this).
 * Buckets come from last_message_at: Today, Yesterday, Previous 7 Days, Older.
 */
export const GROUP_ORDER = ["Today", "Yesterday", "Previous 7 Days", "Older"];

const startOfDay = (d) => new Date(d.getFullYear(), d.getMonth(), d.getDate());

export function groupLabel(isoString, now = new Date()) {
  const day = startOfDay(new Date(isoString));
  const today = startOfDay(now);
  const diffDays = Math.round((today - day) / 86400000);
  if (diffDays <= 0) return "Today"; // also covers small clock skew into the future
  if (diffDays === 1) return "Yesterday";
  if (diffDays <= 7) return "Previous 7 Days";
  return "Older";
}

export function groupConversations(conversations, now = new Date()) {
  const buckets = new Map(GROUP_ORDER.map((label) => [label, []]));
  for (const c of conversations) buckets.get(groupLabel(c.last_message_at, now)).push(c);
  return GROUP_ORDER.filter((label) => buckets.get(label).length > 0).map((label) => ({
    label,
    items: buckets.get(label),
  }));
}
