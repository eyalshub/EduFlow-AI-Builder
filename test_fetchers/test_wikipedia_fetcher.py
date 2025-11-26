from app.stage_1.fetchers.wikipedia_fetcher import fetch_wikipedia_summary


def test_fetch_wikipedia_summary_hebrew():
    topic = "המהפכה הצרפתית"
    summary = fetch_wikipedia_summary(topic, lang="he")
    print("Hebrew summary:\n", summary)
    assert summary is not None, "Expected a summary, got None"
    assert isinstance(summary, str), "Summary should be a string"
    assert len(summary) > 30, "Summary is too short to be meaningful"


def test_fetch_wikipedia_summary_english():
    topic = "French Revolution"
    summary = fetch_wikipedia_summary(topic, lang="en")
    print("English summary:\n", summary)
    assert summary is not None, "Expected a summary, got None"
    assert "France" in summary or "revolution" in summary.lower(), "Summary doesn't relate to topic"


if __name__ == "__main__":
    test_fetch_wikipedia_summary_hebrew()
    test_fetch_wikipedia_summary_english()
    print("✅ All tests passed!")
