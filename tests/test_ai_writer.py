"""Provider response fixtures, not live AI quality evaluations."""
import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from src.ai_writer import _chat


def response(reason="stop", content=" Complete draft ", refusal=None):
    return SimpleNamespace(choices=[SimpleNamespace(
        finish_reason=reason,
        message=SimpleNamespace(content=content, refusal=refusal),
    )])


class CompletionGateTest(unittest.TestCase):
    def call(self, result):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "fixture-key"}), patch("src.ai_writer.OpenAI") as provider:
            provider.return_value.chat.completions.create.return_value = result
            return _chat("System", "Fictional notes")

    def test_complete_text_is_returned(self):
        self.assertEqual(self.call(response()), "Complete draft")

    def test_partial_filtered_and_tool_responses_are_not_reports(self):
        for reason in ("length", "content_filter", "tool_calls", "function_call", None):
            with self.subTest(reason=reason), self.assertRaises(ValueError):
                self.call(response(reason=reason))

    def test_refusal_is_not_saved_as_a_report(self):
        with self.assertRaises(ValueError):
            self.call(response(refusal="Fixture refusal"))

    def test_no_choice_or_empty_text_is_not_a_report(self):
        for result in (SimpleNamespace(choices=[]), response(content=" "), response(content=None)):
            with self.subTest(result=result), self.assertRaises(ValueError):
                self.call(result)

    def test_provider_requests_have_bounded_timeout_and_retry_count(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "fixture-key"}), patch("src.ai_writer.OpenAI") as provider:
            provider.return_value.chat.completions.create.return_value = response()
            _chat("System", "Fictional notes")
            provider.assert_called_once_with(timeout=60.0, max_retries=1)
            provider.return_value.chat.completions.create.assert_called_once()
