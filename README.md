# Secure Local AI Assistant

Local-first AI assistant for email/WhatsApp with authorized file-based knowledge. All inference runs locally.

## Recreate environment

```bash
python -m venv fyp_env

source fyp_env/bin/activate # MacOS/Linux
.fyp_env/bin/Activate.bat # Windows CMD

pip install -r requirements.txt
cp config/authorized_folders.example.yaml config/authorized_folders.yaml
# edit authorized folders
```

## Optional: Ollama

```bash
# install ollama (https://ollama.com), then:
ollama pull qwen2.5:3b-instruct-q4_K_M
```

## Run

```bash
python -m src.cli ingest            # index authorized folders
python -m src.cli search "quarterly report"
python -m src.cli draft --source email --sender a@b.com --body "Please send the report"
python -m src.cli audit
```

## Tests

```bash
pytest -q
```
