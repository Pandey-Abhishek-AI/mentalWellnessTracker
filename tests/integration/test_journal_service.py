"""Integration tests for journal service."""



def test_journal_save_flags_crisis(journal_service, user_id):
    result = journal_service.save_entry(
        user_id,
        "I want to end my life because NEET prep is too much.",
    )
    assert result.crisis.is_crisis
    assert result.entry.crisis_flagged is True


def test_journal_save_normal(journal_service, user_id):
    result = journal_service.save_entry(
        user_id,
        "Today I studied organic chemistry for 4 hours and felt okay.",
    )
    assert not result.crisis.is_crisis
    assert result.entry.crisis_flagged is False
