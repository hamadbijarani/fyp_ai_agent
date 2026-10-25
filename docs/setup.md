# Environment Setup Guide

1. Create venv: `python -m venv fyp_env && source fyp_env/bin/activate`
2. Install deps: `pip install -r requirements.txt`
3. Configure folders: copy `config/authorized_folders.example.yaml` to `config/authorized_folders.yaml` and edit.
4. (Optional) Install Ollama and pull a model: `ollama pull qwen2.5:3b-instruct-q4_K_M`.
5. Set env (see `.env.example`) or edit `config/settings.yaml`.
6. Run tests: `pytest -q`.
