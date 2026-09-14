# RecipeGPT

Um GPT (Transformer decoder-only) construído do zero em PyTorch — sem usar
nenhuma biblioteca de alto nível pronta (`transformers`, `tiktoken`, etc) —
treinado para escrever receitas de culinária completas, incluindo
ingredientes, modo de preparo e informação nutricional (calorias, proteína,
gordura, carboidratos).

Este projeto foi construído após terminar o curso **[Neural Networks: Zero
to Hero](https://karpathy.ai/zero-to-hero.html)**, de Andrej Karpathy, como
forma de aplicar na prática o que foi aprendido. Tudo — o tokenizer BPE, o
mecanismo de self-attention, o Transformer inteiro — foi implementado
manualmente, seguindo os princípios ensinados no curso.

> ⚠️ **Aviso importante: isso não é um livro de receitas.**
> Este é um projeto educacional para aprender como um GPT funciona por
> dentro — **não use as receitas geradas para cozinhar de verdade.** O
> modelo é pequeno e frequentemente gera texto sem sentido, combinações de
> ingredientes estranhas ou incoerentes, e valores nutricionais **inventados**
> (não calculados). Mais grave ainda: ele não tem nenhuma noção de
> **segurança alimentar** — pode "sugerir" tempos/temperaturas de cozimento
> perigosos (por exemplo, para carne, frango ou ovos mal cozidos), porque
> ele só reproduz *padrões de texto*, sem entender o que está escrevendo.
> Trate toda saída deste modelo como curiosidade técnica, nunca como
> instrução culinária real.

## O que este projeto tem por dentro

- **Tokenizer BPE (Byte Pair Encoding)** implementado do zero (`tokenizer.py`)
- **GPT com self-attention** implementado do zero: multi-head attention,
  conexões residuais, layer normalization, dropout (`model.py`)
- **Gerador de dados sintéticos** que combina ingredientes reais com dados
  nutricionais calculados matematicamente, para ampliar o dataset sem
  problemas de direitos autorais (`data/generate_recipes.py`)
- Treino com **checkpointing automático** (sempre salva a melhor versão do
  modelo pela loss de validação, evitando overfitting)

## Resultado

O modelo aprende a estrutura de uma receita (título, resumo, lista de
ingredientes, passos numerados, informação nutricional) e gera texto em
inglês fluente em nível de palavra, ainda com limitações de coerência
gramatical em frases mais longas — esperado dado o tamanho do modelo (~1-2M
parâmetros) e do dataset (~1-1.5M caracteres), muito menor que os de LLMs de
produção. **Veja o aviso no topo deste README antes de usar qualquer saída
gerada.**

## Estrutura do projeto

```
recipe-gpt/
├── data/
│   ├── prepare_data.py       # processa o dataset de 501 receitas reais
│   ├── generate_recipes.py   # gera receitas sintéticas adicionais
│   └── receitas.json         # (baixar - ver instruções abaixo)
├── tokenizer.py               # tokenizer BPE
├── model.py                    # arquitetura do GPT
├── train.py                     # treino com checkpointing
├── generate.py                   # gera uma receita com o modelo treinado
├── checkpoints/                   # modelo e tokenizer treinados (gerado)
└── requirements.txt
```

## Como rodar

### 1. Preparar o ambiente

Requer **Python 3.11 ou 3.12** (builds de PyTorch com suporte a CUDA ainda
não cobrem Python 3.14 no momento em que este projeto foi feito).

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

pip install -r requirements.txt
```

Se você tem uma GPU NVIDIA, instale a versão do PyTorch com suporte a CUDA
(bem mais rápida para treinar):

```bash
pip install torch --index-url https://download.pytorch.org/whl/cu121
```

### 2. Baixar e preparar os dados

```bash
curl -o data/receitas.json https://raw.githubusercontent.com/farcrak/unitools-recipes/main/unitools-recipes-v1.json
python data/prepare_data.py
```

Opcionalmente, gere mais receitas sintéticas para ampliar o dataset:

```bash
python data/generate_recipes.py --n 1000 --seed 42 --out data/minhas_receitas_geradas.txt
```

### 3. Treinar

```bash
python train.py
```

Isso treina o tokenizer BPE, treina o modelo, e salva o melhor checkpoint em
`checkpoints/best_model.pt` e `checkpoints/tokenizer.json`. Os
hiperparâmetros (tamanho do modelo, número de iterações, etc) podem ser
ajustados editando as constantes no topo de `train.py`.

### 4. Gerar uma receita

```bash
python generate.py
python generate.py --prompt "Title: Chocolate" --max_tokens 300
```

## O que eu aprendi construindo isso

- Como tokenização BPE transforma texto em números de forma eficiente,
  reconhecendo tokens especiais sem quebrá-los
- Como self-attention permite que cada posição de uma sequência "preste
  atenção" nas posições anteriores relevantes, sem depender de uma janela
  fixa de contexto
- Como diagnosticar overfitting comparando loss de treino e validação, e
  como checkpointing resolve isso automaticamente
- Que `model.eval()` é essencial antes de gerar texto — sem isso, o Dropout
  continua ativo e degrada a qualidade da geração
- Que modelos de linguagem pura não têm noção de correção numérica/factual:
  o modelo reproduz o *formato* de onde números aparecem, mas não verifica
  se um valor nutricional gerado faz sentido — essa é uma limitação
  estrutural, não um bug, e é o tipo de problema que técnicas como *function
  calling* resolvem em aplicações reais

## Fontes de dados e licenças

- **501 receitas reais**: [UniTools World Recipes](https://github.com/farcrak/unitools-recipes),
  licenciado sob [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).
  Crédito: *"Recipe data: UniTools, CC BY-SA 4.0"*.
- **Receitas sintéticas adicionais**: geradas programaticamente por
  `data/generate_recipes.py`, combinando uma base de dados nutricionais
  genérica com um algoritmo de composição — conteúdo original, sem
  restrições de direitos autorais.
- **Todo o código** deste repositório está sob licença MIT (veja `LICENSE`).

## Créditos

Baseado no curso [Neural Networks: Zero to Hero](https://karpathy.ai/zero-to-hero.html)
de Andrej Karpathy, especialmente as aulas *"Let's build GPT"* e *"Let's
build the GPT Tokenizer"*.
