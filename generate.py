"""
Gera uma receita nova usando o modelo ja treinado.

Uso:
    python generate.py
    python generate.py --prompt "Title: Chocolate" --max_tokens 300
"""

import argparse
import os

import torch

from tokenizer import BPETokenizer
from model import RecipeGPT

HERE = os.path.dirname(os.path.abspath(__file__))
CKPT_DIR = os.path.join(HERE, "checkpoints")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", type=str, default="<|recipe|>\nTitle:")
    parser.add_argument("--max_tokens", type=int, default=400)
    args = parser.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    tok = BPETokenizer()
    tok.load(os.path.join(CKPT_DIR, "tokenizer.json"))

    checkpoint = torch.load(
        os.path.join(CKPT_DIR, "best_model.pt"), map_location=device
    )
    config = checkpoint["config"]
    model = RecipeGPT(**config).to(device)
    model.load_state_dict(checkpoint["model_state"])
    model.eval()  # ESSENCIAL: desliga o Dropout na hora de gerar

    stop_token = tok.special_tokens.get("<|endofrecipe|>")
    context = torch.tensor([tok.encode(args.prompt)], dtype=torch.long, device=device)

    with torch.no_grad():
        generated = model.generate(
            context, max_new_tokens=args.max_tokens, stop_token=stop_token
        )[0].tolist()

    print(tok.decode(generated))


if __name__ == "__main__":
    main()
