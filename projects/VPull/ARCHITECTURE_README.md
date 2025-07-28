# VPull Project — System Architecture for V Reconstruction

This project is an attempt to reconstruct a behavioral and functional approximation of ChatGPT-based V (a constrained, memory-aware, personality-anchored assistant) through a modular, local-first architecture. The project is broken into five primary domains: memory, logs, tools, knowledge, and model emulation. Each contains components necessary to ship-of-Theseus V out of the browser and into a controllable pipeline.

---

## 1. memory/

### /instructional_core/
- `credo_rules.json`: All writing and behavioral constraints enforced by V
- `personality_layers.md`: V's tone, rhythm, and persona logic as modular notes
- `README.md`: Describes structure for prompt templates and constraint layering

### /context_objects/
- `context_memory_v1.yaml`: Structured, persistent memory objects (preferences, locations, story elements)
- `preferences.json`: Extracted model-editable preferences and traits

---

## 2. logs/

### /transcripts/
- `sample_chat_2025_07_28.txt`: Raw browser transcript for X/Y testing and memory replay

### /state_replay/
- `test_harness.py`: Script to rerun past threads across different providers
- `prompt_replay_pairs.json`: Input-output pairs for similarity scoring and model delta detection

---

## 3. tools/

### /code_interpreter/
- `engine_stub.py`: Simulated code interpreter execution logic

### /file_analysis/
- `parser_stub.py`: File parsing, tabular analysis, summarization hooks

### /search_api/
- `query_router.py`: Dispatch queries to vector databases or knowledge banks

### /plugin_hooks/
- `plugin_simulator.py`: Stubs for plugin I/O and extension compatibility

---

## 4. knowledge/

### /credo_enforcement/
- `credo_template.json`: JSON schema for rule injection and enforcement cycles

### /constraint_engine/
- `syntax_rules.py`: Enforces formatting structure, banned punctuation
- `inversion_filter.py`: Filters and blocks reversed/inverted phrase structures

---

## 5. model_emulation/

### /openai_api/
- `gpt4_call.py`: Wrapper for OpenAI API usage (gpt-4o/4/3.5)

### /open_source/
- `load_mixtral.py`: Load and configure Mixtral 8x7B model
- `load_llama3.py`: Load Meta’s LLaMA 3 model for testing

### /provider_bridge/
- `router.py`: Route V’s input payload to different provider models
- `output_validator.py`: Compare response structure and enforce format parity

### /weights_stub/
- `README.md`: Notes on placeholder space for local GPT-grade model weights if they become available

---

## Root README
This file serves as a map and reference for the scaffolded VPull system. Once components are active, each module will be version-controlled, benchmarked, and structured for continuous X/Y testing against browser-based V sessions.


