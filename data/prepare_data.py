"""
Converte o dataset UniTools World Recipes (JSON) num corpus de texto
estruturado, pronto para o tokenizer e o modelo.

Fonte: https://github.com/farcrak/unitools-recipes (CC BY-SA 4.0)

Uso:
    python data/prepare_data.py
Requer:
    data/receitas.json  (baixe com o comando no README)
Gera:
    data/corpus_real.txt
"""

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(HERE, "receitas.json")
OUT_PATH = os.path.join(HERE, "corpus_real.txt")


def formata_receita(receita):
    texto = f"Title: {receita['name']['en']}\n"
    texto += f"Summary: {receita['summary']['en']}\n"
    texto += "Ingredients:\n"
    for ingrediente in receita["ingredients"]:
        qty = ingrediente.get("quantity")
        unit = ingrediente.get("unit", "")
        if qty is None or unit == "toTaste":
            qty_txt = "to taste"
        else:
            qty_txt = f"{qty} {unit}".strip()
        texto += f" - {qty_txt} {ingrediente['name']['en']}\n"
    texto += "Steps:\n"
    for i, step in enumerate(receita["steps"], start=1):
        texto += f"{i}. {step['text']['en']}\n"
    nut = receita["nutritionPerServing"]
    texto += "Nutrition per serving:\n"
    texto += f"Calories: {nut['calories']} kcal\n"
    texto += f"Protein: {nut['protein']} g\n"
    texto += f"Fat: {nut['fat']} g\n"
    texto += f"Carbs: {nut['carbs']} g\n"
    return texto


def main():
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    recipes = data["recipes"]
    blocks = [
        "<|recipe|>\n" + formata_receita(r) + "<|endofrecipe|>\n" for r in recipes
    ]
    corpus = "\n".join(blocks)

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(corpus)

    print(f"{len(recipes)} receitas processadas.")
    print(f"Corpus salvo em {OUT_PATH} ({len(corpus):,} caracteres)")


if __name__ == "__main__":
    main()
