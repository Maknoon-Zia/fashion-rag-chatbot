from app.core.errors import UpstreamError
from app.db.mongo import get_db
from app.services import prompts, retrieval_service
from tests.conftest import make_user


def start(client, headers):
    return client.post("/api/conversations", headers=headers).json()["id"]


def ask(client, headers, cid, text, **extra):
    return client.post(f"/api/conversations/{cid}/messages", json={"content": text, **extra}, headers=headers)


def test_rag_answer_is_grounded_saved_and_returned_with_sources(client, alice, llm, indexed_kb):
    cid = start(client, alice)
    r = ask(client, alice, cid, "I wear a black abaya. Which hijab color works for university?")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["assistant_message"]["content"] == llm.reply
    assert body["user_message"]["status"] == "answered"
    info = body["assistant_message"]["retrieval"]
    assert info["grounded"] is True and info["sources"], "sources must be returned"
    assert any("abaya" in s["section"].lower() or "hijab" in s["section"].lower() for s in info["sources"])
    # retrieved text really reached the LLM, inside the data block
    sent = llm.calls[0]
    assert sent[0]["role"] == "system" and "<knowledge_base>" in sent[-1]["content"]
    assert "[1]" in sent[-1]["content"]
    # title derived from first message; conversation activity updated
    assert body["conversation"]["title"].startswith("I wear a black abaya")


def test_history_persists_in_order_after_reload(client, alice, llm, indexed_kb):
    cid = start(client, alice)
    ask(client, alice, cid, "Suggest colors for a tan complexion")
    ask(client, alice, cid, "What tie goes with a charcoal suit and white shirt?")
    detail = client.get(f"/api/conversations/{cid}", headers=alice).json()
    assert [m["role"] for m in detail["messages"]] == ["user", "assistant", "user", "assistant"]
    # second LLM call included the first turn as history
    roles = [m["role"] for m in llm.calls[1]]
    assert roles == ["system", "user", "assistant", "user"]


def test_conversations_do_not_mix_messages(client, alice, llm, indexed_kb):
    c1, c2 = start(client, alice), start(client, alice)
    ask(client, alice, c1, "black abaya hijab colour")
    assert client.get(f"/api/conversations/{c2}", headers=alice).json()["messages"] == []


def test_no_relevant_context_says_so_and_skips_llm(client, alice, llm, indexed_kb):
    cid = start(client, alice)
    r = ask(client, alice, cid, "zxqv plorbat gnarfle wuzzle quixotic")
    assert r.status_code == 200
    msg = r.json()["assistant_message"]
    assert msg["content"] == prompts.NO_ANSWER_MESSAGE
    assert msg["retrieval"]["grounded"] is False and msg["retrieval"]["sources"] == []
    assert llm.calls == []


def test_small_talk_gets_greeting_without_retrieval(client, alice, llm):  # note: KB not even indexed
    cid = start(client, alice)
    r = ask(client, alice, cid, "hello!")
    assert r.status_code == 200 and r.json()["assistant_message"]["content"] == prompts.GREETING_MESSAGE
    assert llm.calls == []


def test_llm_failure_keeps_user_message_saves_no_fake_answer_and_retry_works(client, alice, llm, indexed_kb):
    cid = start(client, alice)
    llm.error = UpstreamError("llm_unavailable", "The answer service is unavailable. Please try again.")
    r = ask(client, alice, cid, "What scarf colors work with a black abaya?")
    assert r.status_code == 503 and r.json()["code"] == "llm_unavailable"
    failed_id = r.json()["user_message_id"]

    msgs = client.get(f"/api/conversations/{cid}", headers=alice).json()["messages"]
    assert [(m["role"], m["status"]) for m in msgs] == [("user", "failed")]  # preserved, no assistant row

    llm.error = None
    retry = ask(client, alice, cid, "ignored", retry_message_id=failed_id)
    assert retry.status_code == 200
    msgs = client.get(f"/api/conversations/{cid}", headers=alice).json()["messages"]
    assert [(m["role"], m["status"]) for m in msgs] == [("user", "answered"), ("assistant", "ok")]
    assert msgs[0]["content"].startswith("What scarf colors")  # stored text used, not request text
    # an answered message cannot be retried again
    assert ask(client, alice, cid, "x", retry_message_id=failed_id).status_code == 409


def test_retry_of_someone_elses_message_is_404(client, alice, bob, llm, indexed_kb):
    cid = start(client, alice)
    llm.error = UpstreamError("llm_unavailable", "down")
    mid = ask(client, alice, cid, "black abaya hijab").json()["user_message_id"]
    bob_cid = start(client, bob)
    assert ask(client, bob, bob_cid, "x", retry_message_id=mid).status_code == 404


def test_vector_store_not_indexed_gives_helpful_error_and_keeps_message(client, alice, llm):
    cid = start(client, alice)
    r = ask(client, alice, cid, "What goes with a navy blazer?")
    assert r.status_code == 503 and r.json()["code"] == "knowledge_base_not_indexed"
    assert get_db().messages.count_documents({"role": "user", "status": "failed"}) == 1
    assert get_db().messages.count_documents({"role": "assistant"}) == 0


def test_message_validation(client, alice):
    cid = start(client, alice)
    assert ask(client, alice, cid, "   ").status_code == 422
    assert ask(client, alice, cid, "x" * 2001).status_code == 422
    assert get_db().messages.count_documents({}) == 0


def test_build_query_adds_previous_question_for_short_follow_ups():
    assert retrieval_service.build_query("what about shoes?", "black abaya for university") == (
        "black abaya for university\nwhat about shoes?"
    )
    long_q = "please suggest a complete outfit for a winter wedding evening"
    assert retrieval_service.build_query(long_q, "earlier") == long_q
    assert retrieval_service.build_query("hi", None) == "hi"
