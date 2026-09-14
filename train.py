"""
Treina o RecipeGPT do zero: le o corpus, treina o tokenizer BPE, treina o
modelo com checkpointing (salva sempre a melhor versao pela loss de
validacao), e salva tudo em checkpoints/.

Uso:
    python train.py
"""

import copy
import glob
import os

import torch

from tokenizer import BPETokenizer
from model import RecipeGPT

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, "data")
CKPT_DIR = os.path.join(HERE, "checkpoints")

# --------------------------------------------------------------------------
# Hiperparametros
# --------------------------------------------------------------------------
VOCAB_SIZE = 3000
BLOCK_SIZE = 256
BATCH_SIZE = 32
N_EMBD = 192
N_HEAD = 6
N_LAYER = 5
DROPOUT = 0.1
MAX_ITERS = 10000
EVAL_INTERVAL = 300
EVAL_ITERS = 50
LEARNING_RATE = 3e-4
WEIGHT_DECAY = 0.1
SEED = 1337


def load_corpus():
    """Junta o corpus real com todos os arquivos de receitas geradas
    encontrados em data/ (qualquer arquivo minhas_receitas*.txt)."""
    parts = []

    real_path = os.path.join(DATA_DIR, "corpus_real.txt")
    if os.path.exists(real_path):
        with open(real_path, "r", encoding="utf-8") as f:
            parts.append(f.read())
    else:
        raise FileNotFoundError(
            "data/corpus_real.txt nao encontrado. Rode antes: python data/prepare_data.py"
        )

    for path in sorted(glob.glob(os.path.join(DATA_DIR, "minhas_receitas*.txt"))):
        with open(path, "r", encoding="utf-8") as f:
            parts.append(f.read())
        print(f"Incluido: {os.path.basename(path)}")

    return "\n".join(parts)


def main():
    os.makedirs(CKPT_DIR, exist_ok=True)
    torch.manual_seed(SEED)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("Usando dispositivo:", device)

    corpus = load_corpus()
    print(f"Corpus total: {len(corpus):,} caracteres, "
          f"{corpus.count('<|recipe|>')} receitas")

    tok = BPETokenizer()
    print("Treinando tokenizer BPE...")
    tok.train(corpus, vocab_size=VOCAB_SIZE, verbose=True)
    tok.register_special_tokens(["<|recipe|>", "<|endofrecipe|>"])
    tok.save(os.path.join(CKPT_DIR, "tokenizer.json"))
    print("vocab_size final:", tok.vocab_size)

    data_tensor = torch.tensor(tok.encode(corpus), dtype=torch.long)
    n = int(0.9 * len(data_tensor))
    train_data = data_tensor[:n]
    val_data = data_tensor[n:]
    print(f"Tokens: {len(data_tensor):,} | treino: {len(train_data):,} "
          f"| validacao: {len(val_data):,}")

    def get_batch(split):
        data = train_data if split == "train" else val_data
        ix = torch.randint(len(data) - BLOCK_SIZE, (BATCH_SIZE,))
        x = torch.stack([data[i:i + BLOCK_SIZE] for i in ix])
        y = torch.stack([data[i + 1:i + BLOCK_SIZE + 1] for i in ix])
        return x.to(device), y.to(device)

    model = RecipeGPT(
        vocab_size=tok.vocab_size,
        n_embd=N_EMBD,
        n_head=N_HEAD,
        n_layer=N_LAYER,
        block_size=BLOCK_SIZE,
        dropout=DROPOUT,
    ).to(device)
    n_params = sum(p.numel() for p in model.parameters())
    print(f"Modelo: {n_params:,} parametros")

    @torch.no_grad()
    def estimate_loss():
        out = {}
        model.eval()
        for split in ["train", "val"]:
            losses = torch.zeros(EVAL_ITERS)
            for k in range(EVAL_ITERS):
                X, Y = get_batch(split)
                _, loss = model(X, Y)
                losses[k] = loss.item()
            out[split] = losses.mean().item()
        model.train()
        return out

    optimizer = torch.optim.AdamW(
        model.parameters(), lr=LEARNING_RATE, weight_decay=WEIGHT_DECAY
    )

    best_val_loss = float("inf")
    best_state = None

    for it in range(MAX_ITERS):
        if it % EVAL_INTERVAL == 0 or it == MAX_ITERS - 1:
            losses = estimate_loss()
            print(f"step {it}: train loss {losses['train']:.4f}, "
                  f"val loss {losses['val']:.4f}")
            if losses["val"] < best_val_loss:
                best_val_loss = losses["val"]
                best_state = copy.deepcopy(model.state_dict())
                torch.save(
                    {
                        "model_state": best_state,
                        "val_loss": best_val_loss,
                        "config": {
                            "vocab_size": tok.vocab_size,
                            "n_embd": N_EMBD,
                            "n_head": N_HEAD,
                            "n_layer": N_LAYER,
                            "block_size": BLOCK_SIZE,
                            "dropout": DROPOUT,
                        },
                    },
                    os.path.join(CKPT_DIR, "best_model.pt"),
                )
                print(f"  -> novo melhor modelo salvo (val loss {best_val_loss:.4f})")

        xb, yb = get_batch("train")
        _, loss = model(xb, yb)
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        optimizer.step()

    model.load_state_dict(best_state)
    print(f"\nTreino concluido. Melhor val loss: {best_val_loss:.4f}")
    print(f"Checkpoint salvo em: {os.path.join(CKPT_DIR, 'best_model.pt')}")


if __name__ == "__main__":
    main()
