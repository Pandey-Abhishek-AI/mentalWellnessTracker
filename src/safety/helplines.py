"""India mental health helpline resources."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Helpline:
    name: str
    numbers: list[str]
    description: str


HELPLINES: list[Helpline] = [
    Helpline(
        name="Tele-MANAS",
        numbers=["14416", "1-800-891-4416"],
        description="National tele-mental health helpline (24/7)",
    ),
    Helpline(
        name="iCall",
        numbers=["+91-9152987821"],
        description="Psychosocial helpline by TISS",
    ),
    Helpline(
        name="Vandrevala Foundation",
        numbers=["1860-2662-345", "1800-233-3330"],
        description="Mental health support helpline",
    ),
]


def get_helplines() -> list[Helpline]:
    return HELPLINES
