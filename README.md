# Neori

É um jogo que mistura *infecção* com as mecânicas
do [Conway's Game of Life](https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life)
e [Snake Game](https://en.wikipedia.org/wiki/Snake_(video_game_genre)).

## Motivação

Este projeto foi resultado de uma atividade acadêmica
do curso de **Engenharia da Computação**, da disciplina
de **Desenvolvimento Rápido de Aplicações em Python**,
que tinha como objetivo projetar uma aplicação gráfica
usando a linguagem de programação Python, com os
conceitos discutidos durante a disciplina.

## Design

A aplicação usa a biblioteca `pygame`, que contém a lógica
para lidar com a criação da janela e processamento de
eventos de usuário, além de permitir renderizar formas
simples/complexas. A biblioteca `pygame_gui` é utilizada
para a criação da interface de usuário. A biblioteca `numpy`
é usado para operações matemáticas com vetores/matrizes.

### Estrutura

```
neori/                  -> Biblioteca principal
    resources/          -> Recursos utilizados (imagens, fontes e etc)
    __init__.py         -> Define a função para rodar a aplicação
    utils.py            -> Define algumas funções/classes úteis
    colors.py           -> Define as cores utilizadas
    food.py             -> Define os tipos de frutas
    snake.py            -> Define a lógica para a cobra
    world.py            -> Define o comportamento das células
    interface.py        -> Define a interface de usuário
    game.py             -> Arquivo principal, contém a lógica da aplicação
```

## Executando

Antes de tentar executar o jogo, veja se possui as
[depêdencias](#depêndencias) necessárias instaladas.

---

Execute o arquivo `application.py` com python:

```
python application.py
```

Ou se tiver no Windows, encontre o arquivo e o execute
pelo Explorador de Arquivos.

## Depêndencias

- [numpy](https://numpy.org/)
- [pygame_gui](https://github.com/MyreMylar/pygame_gui)

Com o python instalado, instale as depêndencias
usando o comando:

```
pip install numpy pygame_gui
```

ou

```
python -m pip install numpy pygame_gui
```
