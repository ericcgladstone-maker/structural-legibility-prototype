"""Model client dispatch.

Supports three mutator/source providers and one embedding provider.

    ollama_local            POST http://localhost:11434/api/chat
    anthropic               via env ANTHROPIC_API_KEY
    openai                  via env OPENAI_API_KEY
    local_sentence_transformers   for embeddings

The dispatch returns a structured CallResult preserving everything needed
for full trace reconstruction (raw output, token counts, cost, logprobs
where available, errors).
"""
from __future__ import annotations

import dataclasses
import json
import os
import time
from typing import Any

import httpx


@dataclasses.dataclass
class CallResult:
    raw_output: str
    input_tokens: int | None
    output_tokens: int | None
    cached_tokens: int | None
    usd_cost: float | None
    pricing_table_version: str | None
    logprobs_available: bool
    logprobs_reason: str | None
    top_logprobs: list[Any] | None
    seed_supported: bool
    seed: int | None
    reproducibility_policy: str | None
    api_error: dict[str, Any] | None
    latency_seconds: float
    extra: dict[str, Any]


class PricingTable:
    def __init__(self, path: str):
        with open(path) as f:
            self.data = json.load(f)
        self.version = self.data["pricing_table_id"]

    def cost(self, provider: str, model: str, in_tok: int | None, out_tok: int | None) -> float | None:
        if in_tok is None and out_tok is None:
            return None
        prov = self.data["providers"].get(provider, {})
        rates = prov.get(model) or prov.get("_default")
        if rates is None:
            return None
        c = 0.0
        if in_tok is not None:
            c += (in_tok / 1_000_000.0) * rates["input_per_mtok"]
        if out_tok is not None:
            c += (out_tok / 1_000_000.0) * rates["output_per_mtok"]
        return round(c, 6)


def call_model(
    *,
    provider: str,
    model_name: str,
    prompt: str,
    temperature: float,
    top_p: float,
    max_output_tokens: int,
    seed: int | None,
    pricing: PricingTable | None,
    top_logprobs: int = 5,
    timeout: float = 60.0,
) -> CallResult:
    """Dispatch to the appropriate provider. Stateless: prompt is the entire input."""
    t0 = time.time()

    if provider == "ollama_local":
        return _call_ollama(
            model_name=model_name,
            prompt=prompt,
            temperature=temperature,
            top_p=top_p,
            max_output_tokens=max_output_tokens,
            timeout=timeout,
            t0=t0,
            pricing=pricing,
        )
    if provider == "anthropic":
        return _call_anthropic(
            model_name=model_name,
            prompt=prompt,
            temperature=temperature,
            top_p=top_p,
            max_output_tokens=max_output_tokens,
            timeout=timeout,
            t0=t0,
            pricing=pricing,
        )
    if provider == "openai":
        return _call_openai(
            model_name=model_name,
            prompt=prompt,
            temperature=temperature,
            top_p=top_p,
            max_output_tokens=max_output_tokens,
            seed=seed,
            top_logprobs=top_logprobs,
            timeout=timeout,
            t0=t0,
            pricing=pricing,
        )
    raise ValueError(f"Unknown provider: {provider}")


def _call_ollama(*, model_name, prompt, temperature, top_p, max_output_tokens, timeout, t0, pricing) -> CallResult:
    url = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/chat")
    body = {
        "model": model_name,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "options": {
            "temperature": temperature,
            "top_p": top_p,
            "num_predict": max_output_tokens,
        },
    }
    err = None
    text = ""
    in_tok = None
    out_tok = None
    try:
        r = httpx.post(url, json=body, timeout=timeout)
        r.raise_for_status()
        j = r.json()
        text = j.get("message", {}).get("content", "") or ""
        in_tok = j.get("prompt_eval_count")
        out_tok = j.get("eval_count")
    except Exception as e:
        err = {"type": type(e).__name__, "message": str(e)}

    cost = pricing.cost("ollama_local", model_name, in_tok, out_tok) if pricing else 0.0
    return CallResult(
        raw_output=text,
        input_tokens=in_tok,
        output_tokens=out_tok,
        cached_tokens=None,
        usd_cost=cost,
        pricing_table_version=pricing.version if pricing else None,
        logprobs_available=False,
        logprobs_reason="provider_does_not_expose_logprobs",
        top_logprobs=None,
        seed_supported=False,
        seed=None,
        reproducibility_policy="exact_generation_not_guaranteed_distributional_reproduction_only",
        api_error=err,
        latency_seconds=round(time.time() - t0, 4),
        extra={"endpoint": url},
    )


def _call_anthropic(*, model_name, prompt, temperature, top_p, max_output_tokens, timeout, t0, pricing) -> CallResult:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return _err_result("ANTHROPIC_API_KEY not set", t0)
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    body = {
        "model": model_name,
        "max_tokens": max_output_tokens,
        "temperature": temperature,
        "top_p": top_p,
        "messages": [{"role": "user", "content": prompt}],
    }
    err = None
    text = ""
    in_tok = None
    out_tok = None
    try:
        r = httpx.post(url, headers=headers, json=body, timeout=timeout)
        r.raise_for_status()
        j = r.json()
        parts = j.get("content", [])
        text = "".join(p.get("text", "") for p in parts if p.get("type") == "text")
        usage = j.get("usage", {})
        in_tok = usage.get("input_tokens")
        out_tok = usage.get("output_tokens")
    except Exception as e:
        err = {"type": type(e).__name__, "message": str(e)}

    cost = pricing.cost("anthropic", model_name, in_tok, out_tok) if pricing else None
    return CallResult(
        raw_output=text,
        input_tokens=in_tok,
        output_tokens=out_tok,
        cached_tokens=None,
        usd_cost=cost,
        pricing_table_version=pricing.version if pricing else None,
        logprobs_available=False,
        logprobs_reason="anthropic_messages_api_no_logprobs",
        top_logprobs=None,
        seed_supported=False,
        seed=None,
        reproducibility_policy="exact_generation_not_guaranteed_distributional_reproduction_only",
        api_error=err,
        latency_seconds=round(time.time() - t0, 4),
        extra={},
    )


def _call_openai(*, model_name, prompt, temperature, top_p, max_output_tokens, seed, top_logprobs, timeout, t0, pricing) -> CallResult:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return _err_result("OPENAI_API_KEY not set", t0)
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    body: dict[str, Any] = {
        "model": model_name,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_output_tokens,
        "temperature": temperature,
        "top_p": top_p,
        "logprobs": True,
        "top_logprobs": top_logprobs,
    }
    if seed is not None:
        body["seed"] = seed
    err = None
    text = ""
    in_tok = None
    out_tok = None
    lp = None
    try:
        r = httpx.post(url, headers=headers, json=body, timeout=timeout)
        r.raise_for_status()
        j = r.json()
        choice = j["choices"][0]
        text = choice["message"]["content"] or ""
        lp_raw = choice.get("logprobs", {}).get("content", [])
        lp = lp_raw if lp_raw else None
        usage = j.get("usage", {})
        in_tok = usage.get("prompt_tokens")
        out_tok = usage.get("completion_tokens")
    except Exception as e:
        err = {"type": type(e).__name__, "message": str(e)}

    cost = pricing.cost("openai", model_name, in_tok, out_tok) if pricing else None
    return CallResult(
        raw_output=text,
        input_tokens=in_tok,
        output_tokens=out_tok,
        cached_tokens=None,
        usd_cost=cost,
        pricing_table_version=pricing.version if pricing else None,
        logprobs_available=lp is not None,
        logprobs_reason=None if lp is not None else "logprobs_field_empty",
        top_logprobs=lp,
        seed_supported=True,
        seed=seed,
        reproducibility_policy="best_effort_seed_distributional_reproduction" if seed is not None else "exact_generation_not_guaranteed_distributional_reproduction_only",
        api_error=err,
        latency_seconds=round(time.time() - t0, 4),
        extra={},
    )


def _err_result(msg: str, t0: float) -> CallResult:
    return CallResult(
        raw_output="",
        input_tokens=None,
        output_tokens=None,
        cached_tokens=None,
        usd_cost=None,
        pricing_table_version=None,
        logprobs_available=False,
        logprobs_reason="precondition_failed",
        top_logprobs=None,
        seed_supported=False,
        seed=None,
        reproducibility_policy=None,
        api_error={"type": "PreconditionError", "message": msg},
        latency_seconds=round(time.time() - t0, 4),
        extra={},
    )


# --- Embeddings ---

class EmbeddingClient:
    """Lazy-loaded sentence-transformers wrapper for local embeddings."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2", batch_size: int = 32):
        self.model_name = model_name
        self.batch_size = batch_size
        self._model = None

    def _load(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def embed(self, texts: list[str]):
        m = self._load()
        import numpy as np
        embs = m.encode(texts, batch_size=self.batch_size, convert_to_numpy=True, normalize_embeddings=True)
        return embs.astype(np.float32)

    def cosine(self, a, b) -> float:
        import numpy as np
        a = np.asarray(a)
        b = np.asarray(b)
        if a.ndim == 1 and b.ndim == 1:
            return float(np.dot(a, b))
        raise ValueError("cosine() expects 1-D vectors")
