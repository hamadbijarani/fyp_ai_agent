"""Optional CPU-first backend using llama-cpp-python.

GPU acceleration uses a general backend (Vulkan/Metal/ROCm) selected at build time,
never NVIDIA CUDA/cuDNN. Build example:
  CMAKE_ARGS="-DLLAMA_VULKAN=on" pip install llama-cpp-python --no-cache-dir
"""

from __future__ import annotations

import os

from src.config import load_settings
from src.llm.base import LLMClient


class LlamaCppClient(LLMClient):
    def __init__(self, model_path: str | None = None, n_gpu_layers: int = 0, temperature: float = 0.2, max_tokens: int = 512):
        cfg = load_settings()
        inf = cfg.get("inference", {})
        self.model_path = model_path or os.getenv("LLAMA_MODEL_PATH")
        # CPU-first default
        self.n_gpu_layers = n_gpu_layers if n_gpu_layers else int(inf.get("n_gpu_layers", 0) or 0)
        self.temperature = temperature
        self.max_tokens = max_tokens
        try:
            from llama_cpp import Llama
        except Exception as e:
            raise RuntimeError("llama-cpp-python not installed") from e
        self._llm = Llama(model_path=self.model_path, n_gpu_layers=self.n_gpu_layers, verbose=False)

    def generate(self, prompt: str, system: str | None = None, format_json: bool = False) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        out = self._llm.create_chat_completion(messages=messages, temperature=self.temperature, max_tokens=self.max_tokens)
        return out["choices"][0]["message"]["content"]

    def generate_json(self, prompt: str, system: str | None = None) -> dict:
        import json
        raw = self.generate(prompt, system=system, format_json=True)
        try:
            return json.loads(raw)
        except Exception:
            start, end = raw.find("{"), raw.rfind("}")
            if start != -1 and end != -1:
                return json.loads(raw[start : end + 1])
            raise
