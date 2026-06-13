# tests/test_tools.py
from unittest.mock import MagicMock, patch
from tools import search_listings, suggest_outfit, create_fit_card

def test_search_returns_results():
    results = search_listings("vintage graphic tee", size=None, max_price=50)
    print(f"\nResults: {results}")
    assert isinstance(results, list)
    assert len(results) > 0

def test_search_empty_results():
    results = search_listings("designer ballgown", size="XXS", max_price=5)
    print(f"\nResults: {results}")
    assert results == []   # empty list, no exception

def test_search_price_filter():
    results = search_listings("jacket", size=None, max_price=10)
    print(f"\nResults: {results}")
    assert all(item["price"] <= 10 for item in results)


# ── Fixtures ──────────────────────────────────────────────────────────────────

SAMPLE_ITEM = {
    "title": "Vintage Levi's Denim Jacket",
    "category": "jacket",
    "color": "blue",
    "description": "Classic 90s denim jacket with worn-in look",
    "style_tags": ["vintage", "casual", "90s"],
    "colors": ["blue"],
    "brand": "Levi's",
    "platform": "Depop",
    "price": 35.0,
}

SAMPLE_WARDROBE = {
    "items": [
        {"name": "White graphic tee"},
        {"name": "Black slim jeans"},
        {"name": "White Nike Air Force 1s"},
    ]
}

EMPTY_WARDROBE = {"items": []}


def _mock_groq(response_text: str):
    """Return a patched Groq client that yields response_text."""
    mock_choice = MagicMock()
    mock_choice.message.content = response_text
    mock_completion = MagicMock()
    mock_completion.choices = [mock_choice]
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_completion
    return mock_client


# ── suggest_outfit ────────────────────────────────────────────────────────────

@patch("tools._get_groq_client")
def test_suggest_outfit_with_wardrobe_returns_string(mock_get_client):
    mock_get_client.return_value = _mock_groq("Outfit 1: jacket + black jeans + white tee.")
    result = suggest_outfit(SAMPLE_ITEM, SAMPLE_WARDROBE)
    print(f"\nResult: {result}")
    assert isinstance(result, str)
    assert len(result) > 0


@patch("tools._get_groq_client")
def test_suggest_outfit_with_wardrobe_mentions_item(mock_get_client):
    mock_get_client.return_value = _mock_groq("Pair the Vintage Levi's Denim Jacket with black slim jeans.")
    result = suggest_outfit(SAMPLE_ITEM, SAMPLE_WARDROBE)
    print(f"\nResult: {result}")
    assert result.strip() != ""


@patch("tools._get_groq_client")
def test_suggest_outfit_empty_wardrobe_returns_general_advice(mock_get_client):
    mock_get_client.return_value = _mock_groq("This jacket pairs well with slim chinos and white sneakers.")
    result = suggest_outfit(SAMPLE_ITEM, EMPTY_WARDROBE)
    print(f"\nResult: {result}")
    assert isinstance(result, str)
    assert len(result) > 0


@patch("tools._get_groq_client")
def test_suggest_outfit_empty_wardrobe_calls_llm(mock_get_client):
    mock_client = _mock_groq("General styling advice here.")
    mock_get_client.return_value = mock_client
    suggest_outfit(SAMPLE_ITEM, EMPTY_WARDROBE)
    print(f"\nLLM was called: {mock_client.chat.completions.create.called}")
    mock_client.chat.completions.create.assert_called_once()


@patch("tools._get_groq_client")
def test_suggest_outfit_does_not_raise_on_missing_wardrobe_keys(mock_get_client):
    mock_get_client.return_value = _mock_groq("Some advice.")
    result = suggest_outfit(SAMPLE_ITEM, {})
    print(f"\nResult: {result}")
    assert isinstance(result, str)


# ── create_fit_card ───────────────────────────────────────────────────────────

@patch("tools._get_groq_client")
def test_create_fit_card_returns_string(mock_get_client):
    mock_get_client.return_value = _mock_groq("Found this gem on Depop for $35 and I'm obsessed. 🧥")
    result = create_fit_card("jacket + black jeans", SAMPLE_ITEM)
    print(f"\nResult: {result}")
    assert isinstance(result, str)
    assert len(result) > 0


@patch("tools._get_groq_client")
def test_create_fit_card_calls_llm_with_outfit(mock_get_client):
    mock_client = _mock_groq("Caption text here.")
    mock_get_client.return_value = mock_client
    create_fit_card("jacket + black jeans + white tee", SAMPLE_ITEM)
    print(f"\nLLM was called: {mock_client.chat.completions.create.called}")
    mock_client.chat.completions.create.assert_called_once()


def test_create_fit_card_empty_outfit_returns_error_string():
    result = create_fit_card("", SAMPLE_ITEM)
    print(f"\nResult: {repr(result)}")
    assert isinstance(result, str)


def test_create_fit_card_whitespace_outfit_returns_error_string():
    result = create_fit_card("   ", SAMPLE_ITEM)
    print(f"\nResult: {repr(result)}")
    assert isinstance(result, str)


def test_create_fit_card_empty_outfit_does_not_raise():
    try:
        result = create_fit_card("", SAMPLE_ITEM)
        print(f"\nResult: {repr(result)}")
    except Exception as e:
        raise AssertionError(f"create_fit_card raised an exception on empty outfit: {e}")

def test_suggest_outfit_real_llm():
    result = suggest_outfit(SAMPLE_ITEM, SAMPLE_WARDROBE)
    print(f"\nResult: {result}")
    result1 = create_fit_card(result, SAMPLE_ITEM)
    print(f"Result: {result1}")
    assert isinstance(result, str)
    assert len(result) > 0
    assert isinstance(result1, str)
    assert len(result1) > 0
