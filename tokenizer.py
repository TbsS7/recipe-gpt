"""
Tokenizer BPE (Byte Pair Encoding) construido do zero, seguindo os
principios da Aula 8 do curso Neural Networks: Zero to Hero (Karpathy).
"""

import json
import re


def get_stats(ids):
    """Conta quantas vezes cada par de tokens consecutivos aparece na lista."""
    counts = {}
    for pair in zip(ids, ids[1:]):
        counts[pair] = counts.get(pair, 0) + 1
    return counts


def merge(ids, pair, idx):
    """Substitui todas as ocorrencias consecutivas de 'pair' pelo novo token 'idx'."""
    newids = []
    i = 0
    while i < len(ids):
        if i < len(ids) - 1 and ids[i] == pair[0] and ids[i + 1] == pair[1]:
            newids.append(idx)
            i += 2
        else:
            newids.append(ids[i])
            i += 1
    return newids


class BPETokenizer:
    def __init__(self):
        self.merges = {}          # (int, int) -> int
        self.vocab = {}           # int -> bytes
        self.special_tokens = {}  # str -> int

    def train(self, text, vocab_size, verbose=False):
        assert vocab_size >= 256
        num_merges = vocab_size - 256

        ids = list(text.encode("utf-8"))
        vocab = {idx: bytes([idx]) for idx in range(256)}
        merges = {}

        for i in range(num_merges):
            stats = get_stats(ids)
            if not stats:
                break
            pair = max(stats, key=stats.get)
            idx = 256 + i
            ids = merge(ids, pair, idx)
            merges[pair] = idx
            vocab[idx] = vocab[pair[0]] + vocab[pair[1]]
            if verbose and (i + 1) % 500 == 0:
                print(f"merge {i + 1}/{num_merges}")

        self.merges = merges
        self.vocab = vocab

    def register_special_tokens(self, tokens):
        next_id = 256 + len(self.merges)
        for tok in tokens:
            if tok not in self.special_tokens:
                self.special_tokens[tok] = next_id
                next_id += 1

    def _encode_chunk(self, ids):
        ids = list(ids)
        while len(ids) >= 2:
            stats = get_stats(ids)
            pair = min(stats, key=lambda p: self.merges.get(p, float("inf")))
            if pair not in self.merges:
                break
            idx = self.merges[pair]
            ids = merge(ids, pair, idx)
        return ids

    def encode(self, text):
        if not self.special_tokens:
            return self._encode_chunk(list(text.encode("utf-8")))

        pattern = "(" + "|".join(re.escape(t) for t in self.special_tokens) + ")"
        chunks = re.split(pattern, text)
        ids = []
        for chunk in chunks:
            if chunk in self.special_tokens:
                ids.append(self.special_tokens[chunk])
            elif chunk:
                ids.extend(self._encode_chunk(list(chunk.encode("utf-8"))))
        return ids

    def decode(self, ids):
        inverse_special = {v: k for k, v in self.special_tokens.items()}
        parts, buffer = [], b""
        for idx in ids:
            if idx in inverse_special:
                if buffer:
                    parts.append(buffer.decode("utf-8", errors="replace"))
                    buffer = b""
                parts.append(inverse_special[idx])
            else:
                buffer += self.vocab[idx]
        if buffer:
            parts.append(buffer.decode("utf-8", errors="replace"))
        return "".join(parts)

    @property
    def vocab_size(self):
        return 256 + len(self.merges) + len(self.special_tokens)

    def save(self, path):
        payload = {
            "merges": [[list(k), v] for k, v in self.merges.items()],
            "special_tokens": self.special_tokens,
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f)

    def load(self, path):
        with open(path, "r", encoding="utf-8") as f:
            payload = json.load(f)
        self.merges = {tuple(k): v for k, v in payload["merges"]}
        self.special_tokens = payload["special_tokens"]
        vocab = {idx: bytes([idx]) for idx in range(256)}
        for (p0, p1), idx in sorted(self.merges.items(), key=lambda kv: kv[1]):
            vocab[idx] = vocab[p0] + vocab[p1]
        self.vocab = vocab
