import pytest
from app.core.agents.grounding_verifier_agent import run_grounding_verifier_agent, GroundingVerifierInput


def print_grounding_output(name: str, question: str, explanation: str, chunk: str, score: float, justification: str):
    print(f"\n========== TEST CASE: {name} ==========")
    print("🔹 Question:\n", question)
    print("\n✅ Explanation:\n", explanation)
    print("\n📘 Chunk:\n", chunk)
    print(f"\n🎯 Grounding Score: {score}")
    print("\n📝 Justification:\n", justification)
    print("=" * 45)


@pytest.mark.asyncio
async def test_grounding_verifier_fully_grounded():
    input_data: GroundingVerifierInput = {
        "question": "What was the main reason for the French Revolution?",
        "answer": "Economic inequality and taxation.",
        "explanation": "The Third Estate was heavily taxed while others were not, leading to unrest and revolution.",
        "chunk": "The French Revolution was caused by deep economic inequality. The Third Estate carried most of the tax burden while the clergy and nobility were largely exempt."
    }

    result = await run_grounding_verifier_agent(input_data)
    assert result["status"] == "ok"
    print_grounding_output(
        "Fully Grounded",
        input_data["question"],
        input_data["explanation"],
        input_data["chunk"],
        result["grounding_score"],
        result["justification"]
    )
    assert result["grounding_score"] >= 0.8


@pytest.mark.asyncio
async def test_grounding_verifier_not_grounded():
    input_data: GroundingVerifierInput = {
        "question": "Who led the French army during the Revolution?",
        "answer": "Napoleon Bonaparte",
        "explanation": "Napoleon led the revolution and was the main general who fought the monarchy.",
        "chunk": "The French Revolution began as a reaction to inequality and high taxation on the Third Estate. The king at the time was Louis XVI."
    }

    result = await run_grounding_verifier_agent(input_data)
    assert result["status"] == "ok"
    print_grounding_output(
        "Not Grounded",
        input_data["question"],
        input_data["explanation"],
        input_data["chunk"],
        result["grounding_score"],
        result["justification"]
    )
    assert result["grounding_score"] <= 0.3


@pytest.mark.asyncio
async def test_grounding_verifier_partial_grounding_hebrew():
    input_data: GroundingVerifierInput = {
        "question": "מה הוביל לפרוץ המהפכה הצרפתית?",
        "answer": "אי־שוויון חברתי וכלכלי",
        "explanation": "המהפכה פרצה בעקבות האכזבה משלטונו של נפוליאון ומחסור במזון.",
        "chunk": "המהפכה הצרפתית נבעה מאי־שוויון חברתי וכלכלי חמור. המעמד השלישי נשא ברוב נטל המסים, בעוד האצולה והכמורה נהנו מפריבילגיות."
    }

    result = await run_grounding_verifier_agent(input_data)
    assert result["status"] == "ok"
    print_grounding_output(
        "Hebrew – Partial Grounding",
        input_data["question"],
        input_data["explanation"],
        input_data["chunk"],
        result["grounding_score"],
        result["justification"]
    )
    assert 0.2 <= result["grounding_score"] <= 0.6


@pytest.mark.asyncio
async def test_grounding_verifier_generic_but_true_hebrew():
    input_data: GroundingVerifierInput = {
        "question": "מה הייתה השפעת המהפכה הצרפתית?",
        "answer": "היא שינתה את פני אירופה",
        "explanation": "המהפכה הובילה לשינויים פוליטיים בכל רחבי היבשת, כולל עליית רעיונות דמוקרטיים.",
        "chunk": "המהפכה הצרפתית שינתה את סדרי החברה בצרפת. רעיונות של שוויון וחירות החלו להתפשט לאחר מכן."
    }

    result = await run_grounding_verifier_agent(input_data)
    assert result["status"] == "ok"
    print_grounding_output(
        "Hebrew – General but True",
        input_data["question"],
        input_data["explanation"],
        input_data["chunk"],
        result["grounding_score"],
        result["justification"]
    )
    assert 0.5 <= result["grounding_score"] <= 0.9


@pytest.mark.asyncio
async def test_grounding_verifier_unrelated_hebrew():
    input_data: GroundingVerifierInput = {
        "question": "מה היה תפקידו של נפוליאון במהלך המהפכה הצרפתית?",
        "answer": "הוא הוביל את המהפכה מתחילתה ועד סופה.",
        "explanation": "נפוליאון היה הדמות המרכזית במהפכה, הנהיג את הקרבות ושלט בצרפת כבר מראשיתה.",
        "chunk": "במהלך המהפכה הודח המלך לואי ה-16 והוקמה רפובליקה. השלטון עבר לידיים אזרחיות. אין אזכור לנפוליאון."
    }

    result = await run_grounding_verifier_agent(input_data)
    assert result["status"] == "ok"
    print_grounding_output(
        "Hebrew – Completely Unrelated",
        input_data["question"],
        input_data["explanation"],
        input_data["chunk"],
        result["grounding_score"],
        result["justification"]
    )
    assert result["grounding_score"] < 0.2
