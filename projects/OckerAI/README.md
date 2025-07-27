# OckerAI

**OckerAI** is a local, terminal-based AI model designed for real-time learning, interaction, and transparency. It runs entirely on macOS (M1/M2/M3 chip compatible), stores memory and weights locally, and is engineered for autonomy, extensibility, and ethical visibility.

## Architecture Overview

```
OckerAI/
├── model.safetensors       # Brain: model weights
├── tokenizer.json          # Language tokenizer rules
├── train.py                # Training script
├── chat.py                 # Terminal chat interface
├── memory.jsonl            # Ongoing conversation memory
├── config.yaml             # Settings: size, learning rate, paths
├── data/                   # Training data (txt, json, corpora, etc.)
└── logs/                   # Training logs, debug output
```

### Rationale for File Types

* **`.safetensors`**: Chosen for speed, safety, and compatibility with large model weights.
* **`.jsonl`**: Ideal for logging or memory (line-separated, easily parseable, appendable).
* **`.yaml`**: Readable and flexible for configuration.
* **`.py`**: Plain Python for full transparency and terminal-native execution.
* **`data/`**: Centralized for modular retraining or live tuning.

---

## Step-by-Step Build Plan

### 1. **Base Environment Setup**

* Target Platform: macOS with M chips
* Install core libraries:

  ```bash
  pip install torch transformers datasets safetensors
  ```
* Confirm Python 3.9+ (ideally 3.11+)
* No venv unless required (global pip install with `--break-system-packages` if SIP disabled)

---

### 2. **Data Collection**

#### A. *Conversational Seed Training*

* Use internal conversation archives:

  * **Flavel R.E.M. team chat logs**
  * **Angus Flavel / V archive sessions**
  * Export from Slack, Google Drive, and internal docs
  * Format into structured `jsonl`:

    ```json
    {"prompt": "How do I build this thing?", "response": "Here’s what you do..."}
    ```

#### B. *Australian Language Data*

* Access public sources:

  * **ABC News transcripts**
  * **Aussie movie scripts**
  * **Parliament Hansard records**
  * **OpenSubtitles (Australian)**
  * **Aussie podcasts (transcribed)**

#### C. *Profanity / Real Talk*

* **OpenAssistant profanity datasets**
* **Filtered 4chan / Reddit AU** (heavily processed)
* Custom hand-curated files by Angus

#### D. *Creative / Conceptual Thinking*

* V conversations
* Marcus Aurelius reflections
* Sue/Dish Pig screenplay structure
* Inner monologue datasets

---

### 3. **Tokenizer Setup**

* Start from `GPT2TokenizerFast` or `SentencePiece`
* Or build custom with:

  ```bash
  tokenizers-train --files data/ --vocab-size 50000 --output tokenizer.json
  ```

---

### 4. **Model Architecture**

* Start from distilled transformer (TinyGPT, DistilGPT2, etc.)
* OR manually define layers in `train.py`

  * Choose: 4 layers, 8 heads, 256 embedding dim (adjustable in `config.yaml`)

---

### 5. **Training Workflow**

* Organize training material in `data/` (tagged by topic: `aussie_lingo.txt`, `v_logs.jsonl`, `screenplay.txt`)
* Edit `config.yaml` to set epochs, LR, batch size, paths
* Run:

  ```bash
  python train.py
  ```
* Logs output to `logs/`
* Resulting model: `model.safetensors`

---

### 6. **Interaction Loop**

* Run `chat.py` to interact live

  * Input -> Tokenizer -> Model -> Response
  * Response logged with timestamp in `memory.jsonl`
* Future features:

  * Memory embedding
  * Contextual thread loading
  * File summary + ingestion hooks

---

### 7. **Scaling + Extensibility**

* Modular design allows:

  * Fine-tuning new data into `data/new_topic.jsonl`
  * Swapping `model.safetensors` for larger versions
  * Testing different tokenizers
* Future conversions to GGUF possible (optional for LLM chaining or LLM orchestration)

---

### 8. **Transparency + Control**

* All code is visible
* All memory is inspectable
* All weights can be swapped
* Users can delete, modify, or reset the brain
* Folder is portable, can be zipped and moved
* Model doesn’t auto-update, doesn’t sync remotely

---