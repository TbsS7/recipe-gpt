"""
Gerador de receitas sinteticas - combina ingredientes, pratos e estilos de
cozinha de forma programatica para criar centenas de receitas UNICAS e
ORIGINAIS (sem copiar de nenhuma fonte), com nutricao calculada de verdade
a partir dos ingredientes usados (nao inventada).

Uso:
    python generate_recipes.py --n 500 --seed 42 --out minhas_receitas_geradas.txt
"""

import argparse
import random

# ---------------------------------------------------------------------------
# Base de ingredientes: valores por 100g (fonte: medias de tabelas nutricionais
# publicas, arredondadas). calories, protein(g), fat(g), carbs(g)
# ---------------------------------------------------------------------------
INGREDIENTS = {
    "chicken breast":   (165, 31, 3.6, 0),
    "ground beef":      (250, 26, 15, 0),
    "pork loin":        (242, 27, 14, 0),
    "salmon":           (208, 20, 13, 0),
    "shrimp":           (99, 24, 0.3, 0.2),
    "tofu":             (76, 8, 4.8, 1.9),
    "chickpeas":        (164, 8.9, 2.6, 27),
    "black beans":      (132, 8.9, 0.5, 24),
    "lentils":          (116, 9, 0.4, 20),
    "eggs":             (155, 13, 11, 1.1),
    "rice":             (130, 2.7, 0.3, 28),
    "pasta":            (131, 5, 1.1, 25),
    "potato":           (77, 2, 0.1, 17),
    "sweet potato":     (86, 1.6, 0.1, 20),
    "bread":            (265, 9, 3.2, 49),
    "quinoa":           (120, 4.4, 1.9, 21),
    "onion":            (40, 1.1, 0.1, 9),
    "garlic":           (149, 6.4, 0.5, 33),
    "tomato":           (18, 0.9, 0.2, 3.9),
    "bell pepper":      (31, 1, 0.3, 6),
    "carrot":           (41, 0.9, 0.2, 10),
    "spinach":          (23, 2.9, 0.4, 3.6),
    "broccoli":         (34, 2.8, 0.4, 7),
    "zucchini":         (17, 1.2, 0.3, 3.1),
    "mushroom":         (22, 3.1, 0.3, 3.3),
    "cabbage":          (25, 1.3, 0.1, 6),
    "cheese":           (402, 25, 33, 1.3),
    "mozzarella":       (280, 28, 17, 3.1),
    "butter":           (717, 0.9, 81, 0.1),
    "olive oil":        (884, 0, 100, 0),
    "coconut milk":     (230, 2.3, 24, 6),
    "cream":            (340, 2.1, 36, 2.8),
    "yogurt":           (61, 3.5, 3.3, 4.7),
    "milk":             (42, 3.4, 1, 5),
    "flour":            (364, 10, 1, 76),
    "sugar":            (387, 0, 0, 100),
    "honey":            (304, 0.3, 0, 82),
    "almonds":          (579, 21, 50, 22),
    "peanuts":          (567, 26, 49, 16),
    "coconut flakes":   (660, 6.9, 65, 24),
    "soy sauce":        (53, 8, 0.1, 4.9),
    "coconut sugar":    (375, 0, 0, 100),
    "chili peppers":    (40, 1.9, 0.4, 9),
    "ginger":           (80, 1.8, 0.8, 18),
    "lime":             (30, 0.7, 0.2, 11),
    "avocado":          (160, 2, 15, 9),
    "corn":             (86, 3.3, 1.4, 19),
}

# ---------------------------------------------------------------------------
# Cuisines: pais, estilo de tempero (usado nos passos), ingredientes "assinatura"
# ---------------------------------------------------------------------------
CUISINES = [
    ("BR", "Brazilian", ["garlic", "onion", "tomato", "black beans", "rice", "lime"]),
    ("IT", "Italian", ["garlic", "olive oil", "tomato", "pasta", "mozzarella", "cheese"]),
    ("IN", "Indian", ["ginger", "garlic", "chili peppers", "coconut milk", "chickpeas", "rice"]),
    ("MX", "Mexican", ["chili peppers", "lime", "corn", "black beans", "avocado", "tomato"]),
    ("JP", "Japanese", ["soy sauce", "ginger", "rice", "mushroom", "tofu"]),
    ("FR", "French", ["butter", "cream", "garlic", "onion", "mushroom"]),
    ("TH", "Thai", ["coconut milk", "chili peppers", "lime", "ginger", "peanuts"]),
    ("GR", "Greek", ["olive oil", "garlic", "yogurt", "spinach", "cheese"]),
    ("MA", "Moroccan", ["chickpeas", "chili peppers", "ginger", "honey", "almonds"]),
    ("US", "American", ["cheese", "ground beef", "bread", "potato", "corn"]),
    ("KR", "Korean", ["soy sauce", "garlic", "ginger", "cabbage", "chili peppers"]),
    ("PE", "Peruvian", ["lime", "chili peppers", "corn", "sweet potato", "onion"]),
]

DISH_TYPES = [
    ("soup", "main", ["broth-friendly simmering"]),
    ("stew", "main", ["slow simmering"]),
    ("stir-fry", "main", ["quick high-heat stir-frying"]),
    ("curry", "main", ["simmering in a spiced sauce"]),
    ("pasta dish", "main", ["boiling and tossing"]),
    ("grain bowl", "main", ["assembling cooked components"]),
    ("salad", "salad", ["tossing fresh ingredients"]),
    ("roast", "main", ["oven roasting"]),
    ("casserole", "main", ["baking layered ingredients"]),
    ("taco filling", "main", ["pan-frying and seasoning"]),
    ("dumpling filling", "main", ["mixing and steaming"]),
    ("pancake", "breakfast", ["griddle cooking"]),
    ("flatbread", "snack", ["griddle cooking"]),
    ("dessert bar", "dessert", ["baking and cooling"]),
    ("pudding", "dessert", ["slow stovetop stirring"]),
    ("smoothie bowl", "breakfast", ["blending"]),
]

PROTEINS = ["chicken breast", "ground beef", "pork loin", "salmon", "shrimp", "tofu",
            "chickpeas", "black beans", "lentils", "eggs"]
STARCHES = ["rice", "pasta", "potato", "sweet potato", "bread", "quinoa", "corn"]
VEGGIES = ["onion", "tomato", "bell pepper", "carrot", "spinach", "broccoli",
           "zucchini", "mushroom", "cabbage"]
FATS = ["olive oil", "butter", "coconut milk", "cream"]

DIFFICULTIES = ["easy", "medium", "hard"]

STEP_VERBS = {
    "broth-friendly simmering": [
        "Bring a pot of water or broth to a boil and add the {ing}.",
        "Simmer everything together until the {ing} is tender.",
    ],
    "slow simmering": [
        "Brown the {ing} in a heavy pot over medium heat.",
        "Cover and let it simmer slowly until everything is tender.",
    ],
    "quick high-heat stir-frying": [
        "Heat oil in a wok or large pan until very hot, then add the {ing}.",
        "Stir constantly for a few minutes until everything is cooked through.",
    ],
    "simmering in a spiced sauce": [
        "Toast the spices briefly, then add the {ing} and stir to coat.",
        "Pour in the sauce and simmer until thickened and fragrant.",
    ],
    "boiling and tossing": [
        "Cook the {ing} in salted boiling water until al dente.",
        "Toss with the sauce and remaining ingredients off the heat.",
    ],
    "assembling cooked components": [
        "Cook the {ing} separately according to package instructions.",
        "Arrange everything in a bowl and drizzle with dressing.",
    ],
    "tossing fresh ingredients": [
        "Wash and chop the {ing} into bite-sized pieces.",
        "Toss everything together with the dressing just before serving.",
    ],
    "oven roasting": [
        "Preheat the oven and toss the {ing} with oil and seasoning.",
        "Roast until golden and cooked through, turning once halfway.",
    ],
    "baking layered ingredients": [
        "Layer the {ing} in a baking dish.",
        "Bake until bubbling and golden on top.",
    ],
    "pan-frying and seasoning": [
        "Cook the {ing} in a hot pan, breaking it up as it browns.",
        "Season well and remove from the heat.",
    ],
    "mixing and steaming": [
        "Mix the {ing} together into a filling.",
        "Wrap and steam until cooked through.",
    ],
    "griddle cooking": [
        "Mix the {ing} into a batter or dough.",
        "Cook on a hot griddle until golden on both sides.",
    ],
    "baking and cooling": [
        "Combine the {ing} and pour into a lined baking pan.",
        "Bake, then let cool completely before slicing.",
    ],
    "slow stovetop stirring": [
        "Combine the {ing} in a saucepan over low heat.",
        "Stir constantly until thickened.",
    ],
    "blending": [
        "Add the {ing} to a blender.",
        "Blend until smooth and pour into a bowl.",
    ],
}

UNITS_FOR = {
    "eggs": "piece", "garlic": "clove", "onion": "piece", "tomato": "piece",
    "bell pepper": "piece", "carrot": "piece", "avocado": "piece", "lime": "piece",
}

# peso medio (em gramas) de UMA unidade "piece"/"clove", usado so para estimar
# a nutricao corretamente (a quantidade exibida na receita continua em unidades)
PIECE_WEIGHT_G = {
    "eggs": 50, "garlic": 5, "onion": 110, "tomato": 120,
    "bell pepper": 120, "carrot": 60, "avocado": 200, "lime": 70,
}

COUNT_MAX = {
    "eggs": 6, "garlic": 6, "onion": 3, "tomato": 4,
    "bell pepper": 3, "carrot": 3, "avocado": 2, "lime": 3,
}


def pick_unit(ingredient):
    return UNITS_FOR.get(ingredient, "g")


def is_count_based(ingredient):
    return ingredient in UNITS_FOR


def nutrition_for(ingredient, grams):
    cal, prot, fat, carb = INGREDIENTS[ingredient]
    factor = grams / 100.0
    return cal * factor, prot * factor, fat * factor, carb * factor


SWEET_INGREDIENTS = ["flour", "sugar", "honey", "milk", "eggs", "butter", "cream",
                      "almonds", "peanuts", "coconut flakes", "coconut sugar",
                      "yogurt", "avocado"]


def gen_ingredient_list(rng, cuisine_ings, dish_category):
    chosen = []

    if dish_category in ("dessert", "breakfast"):
        pool = list(SWEET_INGREDIENTS)
        rng.shuffle(pool)
        n_items = rng.randint(3, 5)
        chosen = [p for p in pool if p in INGREDIENTS][:n_items]
        if "sugar" not in chosen and rng.random() < 0.6:
            chosen.append("sugar")
        return list(dict.fromkeys(chosen))

    n_protein = 1
    if n_protein and rng.random() < 0.8:
        chosen.append(rng.choice(PROTEINS))

    chosen.append(rng.choice(STARCHES))

    n_veggies = rng.randint(2, 4)
    veg_pool = list(set(VEGGIES) | set(cuisine_ings))
    rng.shuffle(veg_pool)
    for v in veg_pool:
        if v in INGREDIENTS and v not in chosen:
            chosen.append(v)
        if len([c for c in chosen if c in VEGGIES or c in cuisine_ings]) >= n_veggies:
            break

    if rng.random() < 0.7:
        chosen.append(rng.choice(FATS))

    # adiciona 1-2 itens de assinatura da cuisine que ainda nao estao la
    extra = [c for c in cuisine_ings if c not in chosen and c in INGREDIENTS]
    rng.shuffle(extra)
    chosen.extend(extra[:2])

    # remove duplicados mantendo ordem
    seen = set()
    result = []
    for c in chosen:
        if c not in seen:
            seen.add(c)
            result.append(c)
    return result


def gen_quantities(rng, ingredient_list, servings):
    quantities = {}
    for ing in ingredient_list:
        if is_count_based(ing):
            base = rng.randint(1, max(1, COUNT_MAX[ing] // 2))
            scale = max(1, round(servings / 2))
            qty = min(COUNT_MAX[ing], base * scale)
        elif ing in FATS:
            qty = rng.choice([15, 20, 30, 50]) * max(1, servings // 2)
        elif ing in PROTEINS:
            qty = rng.choice([100, 120, 150, 200]) * max(1, servings // 2)
        elif ing in STARCHES:
            qty = rng.choice([80, 100, 150, 200]) * max(1, servings // 2)
        else:
            qty = rng.choice([30, 50, 80, 100]) * max(1, servings // 2)
        quantities[ing] = qty
    return quantities


def format_recipe(rng, idx):
    country_code, country_name, cuisine_ings = rng.choice(CUISINES)
    dish_name, dish_category, techniques = rng.choice(DISH_TYPES)
    difficulty = rng.choice(DIFFICULTIES)
    servings = rng.choice([2, 2, 4, 4, 6])
    prep = rng.choice([10, 15, 20, 25, 30])
    cook = rng.choice([10, 15, 20, 30, 40, 60])

    ingredient_list = gen_ingredient_list(rng, cuisine_ings, dish_category)
    quantities = gen_quantities(rng, ingredient_list, servings)

    main_ing = ingredient_list[0] if ingredient_list else "vegetables"
    title = f"{country_name} {main_ing.title()} {dish_name.title()}"

    lines = []
    lines.append("<|recipe|>")
    lines.append(f"Title: {title}")
    lines.append(f"Country: {country_code}")
    lines.append(f"Category: {dish_category}")
    lines.append(f"Difficulty: {difficulty}")
    lines.append(f"Servings: {servings}")
    lines.append(f"Prep time: {prep} min")
    lines.append(f"Cook time: {cook} min")
    article = "An" if difficulty[0] in "aeiou" else "A"
    lines.append(f"Summary: {article} {difficulty} {country_name.lower()}-style {dish_name} "
                 f"built around {main_ing}, finished with a simple homemade touch.")
    lines.append("")
    lines.append("Ingredients:")

    total_cal = total_prot = total_fat = total_carb = 0.0
    for ing in ingredient_list:
        qty = quantities[ing]
        unit = pick_unit(ing)
        if is_count_based(ing):
            grams_equiv = qty * PIECE_WEIGHT_G[ing]
        else:
            grams_equiv = qty
        c, p, f, cb = nutrition_for(ing, grams_equiv)
        total_cal += c; total_prot += p; total_fat += f; total_carb += cb
        lines.append(f"- {qty} {unit} {ing.title()}")

    lines.append("")
    lines.append("Steps:")
    step_num = 1
    for tech in techniques:
        verbs = STEP_VERBS[tech]
        for v in verbs:
            text = v.format(ing=main_ing)
            minutes = rng.choice([5, 8, 10, 15])
            lines.append(f"{step_num}. {text} ({minutes} min)")
            step_num += 1
    lines.append(f"{step_num}. Season to taste, plate, and serve while hot.")

    lines.append("")
    lines.append("Nutrition per serving:")
    lines.append(f"Calories: {round(total_cal / servings)} kcal")
    lines.append(f"Protein: {round(total_prot / servings)} g")
    lines.append(f"Fat: {round(total_fat / servings)} g")
    lines.append(f"Carbs: {round(total_carb / servings)} g")
    lines.append("<|endofrecipe|>")
    lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=500)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--out", type=str, default="minhas_receitas_geradas.txt")
    args = parser.parse_args()

    rng = random.Random(args.seed)
    seen_titles = set()
    blocks = []
    attempts = 0
    while len(blocks) < args.n and attempts < args.n * 20:
        attempts += 1
        block = format_recipe(rng, len(blocks))
        title_line = block.split("\n")[1]
        if title_line in seen_titles:
            continue
        seen_titles.add(title_line)
        blocks.append(block)

    with open(args.out, "w", encoding="utf-8") as f:
        f.write("\n".join(blocks))

    print(f"Geradas {len(blocks)} receitas unicas em '{args.out}'")
    print(f"Tamanho do arquivo: {sum(len(b) for b in blocks):,} caracteres")
    print("\n--- Exemplo ---\n")
    print(blocks[0])


if __name__ == "__main__":
    main()
