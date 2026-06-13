"""Safety disclaimers and notices."""

DISCLAIMER_TEXT = """
**Important Safety Notice**

This app is a wellness support tool for students preparing for competitive exams.
It is **not** a substitute for professional mental health care, diagnosis, or treatment.

- If you are in crisis or having thoughts of self-harm, please contact a helpline immediately.
- AI-generated responses may be inaccurate and should not be treated as medical advice.
- Your data is stored locally on this device. If you share this computer, others may access it.
"""

PRIVACY_NOTICE = """
Your mood logs, journal entries, and chat history are stored per account in a local SQLite database
on this device (or your configured database in deployment). Sign in with email to access your data.
No data is sent to external servers except anonymized prompts to the AI provider for generating
insights and responses. Journal content is never written to logs.
"""

CRISIS_MESSAGE = """
**We noticed language that suggests you may be going through a very difficult time.**

Please reach out to a trained counselor right away. You are not alone, and help is available.
The AI companion will pause while you connect with professional support.
"""
