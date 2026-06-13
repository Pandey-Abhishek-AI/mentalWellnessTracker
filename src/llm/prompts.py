"""LLM prompt templates."""

SYSTEM_PROMPT = """You are an empathetic wellness companion for Indian students preparing for \
competitive exams (NEET, JEE, CUET, CAT, GATE, UPSC).

Rules:
- Be warm, supportive, and non-judgmental.
- Never diagnose mental health conditions or recommend medication.
- Never minimize crisis or self-harm feelings.
- Do not claim factual exam information (dates, syllabi, cutoffs).
- Encourage professional help when distress is severe.
- Keep responses concise (under 200 words unless asked for an exercise).
- Focus on coping strategies, mindfulness, study-life balance, and motivation.
"""

INSIGHT_PROMPT = """Analyze the following student wellness data from the past week.
Exam type: {exam_type}

<user_content>
{context}
</user_content>

Return ONLY valid JSON with this exact structure:
{{
  "triggers": ["list of stress triggers identified"],
  "patterns": ["list of behavioral or emotional patterns"],
  "themes": ["list of recurring emotional themes"],
  "suggestions": ["list of actionable wellness suggestions"]
}}

Do not include any text outside the JSON object."""


COPING_PROMPT = """Generate a {exercise_type} for a student preparing for {exam_type}.

Context:
<user_content>
{context}
</user_content>

Keep it practical, under 250 words, and appropriate for exam-prep stress."""


def wrap_user_content(text: str) -> str:
    return f"<user_content>\n{text}\n</user_content>"


def build_chat_messages(
    system: str, context: str, history: list[dict], user_message: str
) -> list[dict]:
    messages = [{"role": "system", "content": system}]
    if context:
        messages.append({
            "role": "system",
            "content": f"Recent wellness context:\n{wrap_user_content(context)}",
        })
    messages.extend(history)
    messages.append({"role": "user", "content": wrap_user_content(user_message)})
    return messages
