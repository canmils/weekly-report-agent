# Preserve drafts when model generation is incomplete

Assessed 2026-11-12 against main `1086699d78185d0d25b8c03a0c02a1e375b1f647`.

## Problem and decision

`src/ai_writer.py::_chat` returned any nonempty response text, including a report cut off at the token limit or a refusal. Both UI generation paths then replaced the reviewed draft. Add a deterministic completion gate before returning text: require a choice, no refusal, `finish_reason == stop`, and nonempty string content. Existing UI error handling preserves the previous draft and source state.

Set a 60-second network timeout per attempt and at most one SDK retry. Do not add an application retry/repair loop or evaluator LLM. A timeout setting is not an overall wall-clock deadline. No new dependencies, model selection, token limit or paid calls are introduced by this change.

This borrows the idea of an objective pipeline gate before human review, not a claim that an autonomous supervisor or evaluator verifies facts. A complete response can still omit, misinterpret or invent information. The producer must review before saving or sharing.

## Sources

- [LangGraph workflow guidance](https://github.com/langchain-ai/docs/blob/main/src/oss/langgraph/workflows-agents.mdx), reviewed blob `4b9fceb641a50dd2eb5354be65819d4a8af427bb`: conceptual pipeline gates; no code copied or dependency adopted.
- Existing OpenAI Python dependency: installed official SDK `2.54.0`, `openai/types/chat/chat_completion.py` and `chat_completion_message.py` confirm completion reasons and refusal fields. The existing requirements already allow this SDK version.
- The supplied Reflexion link (https://lnkd.in/eQ5nabJz -> https://arxiv.org/abs/2303.11366) concerns verbal feedback, not a drop-in transport retry implementation. Do not describe this change as implementing Reflexion.

## Validation and rollback

- Baseline: 4 tests passed.
- Completion/refusal/empty-choice/token-limit/filter/tool-call fixtures exercise the real writer with mocked provider transport boundary.
- A Streamlit regression verifies truncated responses preserve both game and clan drafts and create no additional report files.
- No paid live model evaluation. These checks establish response handling, not factual quality or general output improvement.
- Revert the PR to restore previous handling. A valid completion still replaces an unsaved draft as before; this change only blocks unusable responses.
