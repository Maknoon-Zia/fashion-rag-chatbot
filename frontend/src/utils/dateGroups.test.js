import test from "node:test";
import assert from "node:assert/strict";
import { groupConversations, groupLabel } from "./dateGroups.js";

// "now" = Sunday 25 Oct 2026, 15:00 local time
const now = new Date(2026, 9, 25, 15, 0, 0);
const at = (y, m, d, h = 12) => new Date(y, m, d, h).toISOString();

test("labels by calendar day in local time", () => {
  assert.equal(groupLabel(at(2026, 9, 25, 0), now), "Today");
  assert.equal(groupLabel(at(2026, 9, 24, 23), now), "Yesterday");
  assert.equal(groupLabel(at(2026, 9, 23), now), "Previous 7 Days");
  assert.equal(groupLabel(at(2026, 9, 18), now), "Previous 7 Days"); // exactly 7 days ago
  assert.equal(groupLabel(at(2026, 9, 17), now), "Older");
  assert.equal(groupLabel(at(2025, 0, 1), now), "Older");
});

test("groups keep order, skip empty groups and preserve item order", () => {
  const items = [
    { id: "a", last_message_at: at(2026, 9, 25, 14) },
    { id: "b", last_message_at: at(2026, 9, 25, 9) },
    { id: "c", last_message_at: at(2026, 9, 20) },
    { id: "d", last_message_at: at(2026, 8, 1) },
  ];
  const groups = groupConversations(items, now);
  assert.deepEqual(groups.map((g) => g.label), ["Today", "Previous 7 Days", "Older"]);
  assert.deepEqual(groups[0].items.map((i) => i.id), ["a", "b"]);
});

test("empty list gives no groups", () => {
  assert.deepEqual(groupConversations([], now), []);
});
