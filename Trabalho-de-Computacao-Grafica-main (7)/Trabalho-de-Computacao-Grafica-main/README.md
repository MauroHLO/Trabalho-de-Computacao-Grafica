# Zelda 3D – Projeto de Computação Gráfica

Este projeto consiste no desenvolvimento de um jogo 3D inspirado na franquia Zelda,
implementado integralmente em Python, como trabalho acadêmico da disciplina de
Computação Gráfica.

O objetivo do projeto é aplicar, de forma prática, os conceitos fundamentais de
computação gráfica, utilizando OpenGL em baixo nível, sem o uso de engines prontas,
permitindo a compreensão completa do pipeline de renderização 3D.


## Descrição Geral

O sistema simula um ambiente tridimensional no estilo Zelda, permitindo ao jogador
controlar um personagem em um cenário 3D composto por plataformas, rampas e inimigos.

O projeto foi desenvolvido de forma modular, separando claramente a lógica do jogo,
a engine gráfica e o sistema de renderização, facilitando a compreensão, manutenção
e evolução do código.


## Conceitos de Computação Gráfica Aplicados

- Pipeline de renderização 3D
- Sistemas de coordenadas (mundo, câmera e tela)
- Transformações geométricas:
  - Translação
  - Escala
  - Rotação
- Projeção perspectiva
- Câmera 3D (LookAt)
- Shaders programáveis (GLSL)
- Renderização de objetos 3D
- Organização da cena
- Detecção básica de colisão
- Movimentação e animação em tempo real


## Tecnologias Utilizadas

- Python 3
- PyOpenGL
- GLFW
- NumPy
- OpenGL (GLSL)


## Principais Imports do Projeto

import glfw
from OpenGL.GL import *
import numpy as np
import math
import ctypes
import time

from engine.transformacoes import perspectiva, translacao, escala, rotacaoX, look_at
from engine.geometrias import criarCubo, criarPlataforma, criarVAO
from engine.colisao import colisaoINI

from game.jogador import Player
from game.inimigo import Inimigo
from game.plataforma import Plataforma
from game.rampa import Rampa

from core.renderizador import desenhar
from core.shaders import criarPrograma


## Execução do Projeto

Pré-requisitos:
- Python 3.9 ou superior
- Pip

Instalação das dependências:
pip install glfw PyOpenGL numpy

Execução:
python src/main.py


## Arquitetura do Sistema

O projeto segue uma arquitetura dividida em três camadas principais:

Engine:
Responsável por transformações geométricas, criação de geometrias e colisão.

Core:
Responsável pela comunicação com a GPU, shaders e renderização.

Game:
Responsável pela lógica do jogo, entidades e regras de interação.

Essa separação facilita o entendimento do fluxo gráfico e a organização do código.


## Estado Atual do Projeto

- Renderização 3D funcional
- Sistema de câmera implementado
- Movimentação do jogador
- Detecção de colisão básica
- Cenário com plataformas e rampas
- Estrutura inicial de inimigos

## Autor

Projeto desenvolvido como trabalho acadêmico para a disciplina de Computação Gráfica.

Arthur Lemes

Mauro Henrique

Rian Lucas

## Observações Finais

Este projeto possui finalidade exclusivamente educacional. A inspiração na franquia
Zelda é utilizada apenas como referência conceitual e estética, sem qualquer finalidade
comercial.

## Estrutura de Pastas

```text
src/
├── assets/
│   └── shaders/
│       ├── basic.vert
│       └── basic.frag
│
├── core/
│   ├── renderizador.py
│   └── shaders.py
│
├── engine/
│   ├── colisao.py
│   ├── geometrias.py
│   └── transformacoes.py
│
├── game/
│   ├── fase.py
│   ├── inimigo.py
│   ├── jogador.py
│   ├── modelo_blocos.py
│   ├── modelo_inimigos.py
│   ├── plataforma.py
│   ├── rampa.py
│   └── render_utils.py
│
└── main.py

