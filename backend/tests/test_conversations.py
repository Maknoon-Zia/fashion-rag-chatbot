from app.db.mongo import get_db
from app.services import conversation_service as cs


def new_conv(client, headers):
    r = client.post("/api/conversations", headers=headers)
    assert r.status_code == 201
    return r.json()


def test_create_list_newest_activity_first(client, alice):
    first, second = new_conv(client, alice), new_conv(client, alice)
    ids = [c["id"] for c in client.get("/api/conversations", headers=alice).json()["items"]]
    assert ids == [second["id"], first["id"]]
    assert first["title"] == "New chat"


def test_user_only_sees_own_conversations(client, alice, bob):
    mine = new_conv(client, alice)
    assert client.get("/api/conversations", headers=bob).json()["items"] == []
    assert [c["id"] for c in client.get("/api/conversations", headers=alice).json()["items"]] == [mine["id"]]


def test_ownership_other_user_gets_404_everywhere(client, alice, bob, llm):
    conv = new_conv(client, alice)
    cid = conv["id"]
    assert client.get(f"/api/conversations/{cid}", headers=bob).status_code == 404
    assert client.patch(f"/api/conversations/{cid}", json={"title": "hacked"}, headers=bob).status_code == 404
    assert client.post(f"/api/conversations/{cid}/messages", json={"content": "hi there"}, headers=bob).status_code == 404
    assert client.delete(f"/api/conversations/{cid}", headers=bob).status_code == 404
    # ... and nothing changed for the owner
    detail = client.get(f"/api/conversations/{cid}", headers=alice).json()
    assert detail["conversation"]["title"] == "New chat" and detail["messages"] == []
    assert llm.calls == []


def test_invalid_and_unknown_ids_return_404_not_500(client, alice):
    assert client.get("/api/conversations/not-an-objectid", headers=alice).status_code == 404
    assert client.get("/api/conversations/64b7f0f2f2f2f2f2f2f2f2f2", headers=alice).status_code == 404


def test_rename_and_validation(client, alice):
    cid = new_conv(client, alice)["id"]
    r = client.patch(f"/api/conversations/{cid}", json={"title": "  Eid   outfit ideas "}, headers=alice)
    assert r.status_code == 200 and r.json()["title"] == "Eid outfit ideas"
    assert client.patch(f"/api/conversations/{cid}", json={"title": "   "}, headers=alice).status_code == 422
    assert client.patch(f"/api/conversations/{cid}", json={"title": "x" * 121}, headers=alice).status_code == 422


def test_delete_removes_conversation_and_messages(client, alice):
    cid = new_conv(client, alice)["id"]
    conv = cs.get_owned_conversation(get_db().users.find_one({"email": "alice@example.com"})["_id"], cid)
    cs.insert_message(conv, "user", "hello", "answered")
    assert client.delete(f"/api/conversations/{cid}", headers=alice).status_code == 204
    assert client.get(f"/api/conversations/{cid}", headers=alice).status_code == 404
    assert client.delete(f"/api/conversations/{cid}", headers=alice).status_code == 404
    assert get_db().messages.count_documents({}) == 0


def test_message_pagination_is_bounded_and_ordered(client, alice):
    cid = new_conv(client, alice)["id"]
    uid = get_db().users.find_one({"email": "alice@example.com"})["_id"]
    conv = cs.get_owned_conversation(uid, cid)
    for i in range(5):
        cs.insert_message(conv, "user" if i % 2 == 0 else "assistant", f"m{i}", "ok")
    page1 = client.get(f"/api/conversations/{cid}?limit=2", headers=alice).json()
    assert [m["content"] for m in page1["messages"]] == ["m3", "m4"] and page1["has_more"]
    page2 = client.get(f"/api/conversations/{cid}?limit=2&before={page1['next_before']}", headers=alice).json()
    assert [m["content"] for m in page2["messages"]] == ["m1", "m2"] and page2["has_more"]
    page3 = client.get(f"/api/conversations/{cid}?limit=2&before={page2['next_before']}", headers=alice).json()
    assert [m["content"] for m in page3["messages"]] == ["m0"] and not page3["has_more"]
    assert client.get(f"/api/conversations/{cid}?limit=1000", headers=alice).status_code == 422


def test_indexes_exist(client):
    db = get_db()
    assert any(i.get("unique") for i in db.users.index_information().values())
    assert "user_last_message" in db.conversations.index_information()
    assert "conversation_created" in db.messages.index_information()
