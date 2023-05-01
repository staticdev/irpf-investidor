# IRPF Investidor

[![PyPI](https://img.shields.io/pypi/v/irpf-investidor.svg)][pypi status]
[![Status](https://img.shields.io/pypi/status/irpf-investidor.svg)][pypi status]
[![Python Version](https://img.shields.io/pypi/pyversions/irpf-investidor)][pypi status]
[![License](https://img.shields.io/pypi/l/irpf-investidor)][license]

[![Read the documentation at https://irpf-investidor.readthedocs.io/](https://img.shields.io/readthedocs/irpf-investidor/latest.svg?label=Read%20the%20Docs)][read the docs]
[![Tests](https://github.com/staticdev/irpf-investidor/workflows/Tests/badge.svg)][tests]
[![Codecov](https://codecov.io/gh/staticdev/irpf-investidor/branch/main/graph/badge.svg)][codecov]

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)][black]

[pypi status]: https://pypi.org/project/irpf-investidor/
[read the docs]: https://irpf-investidor.readthedocs.io/
[tests]: https://github.com/staticdev/irpf-investidor/actions?workflow=Tests
[codecov]: https://app.codecov.io/gh/staticdev/irpf-investidor
[pre-commit]: https://github.com/pre-commit/pre-commit
[black]: https://github.com/psf/black

Programa auxiliar para calcular custos de ações, ETFs e FIIs. Este programa foi feito para calcular emolumentos, taxa de liquidação e custo total para a declaração de Bens e Direitos do Imposto de Renda Pessoa Física.

**Essa aplicação foi testada e configurada para calcular tarifas referentes aos anos de 2019 a 2022 (IRPF 2020/2023) e não faz cálculos para compra e venda no mesmo dia (Day Trade), contratos futuros e Índice Brasil 50.**

## Requisitos

1. Python

Instale na sua máquina o Python 3.10.0 ou superior (versão 3.10 recomendada) para o seu sistema operacional em [python.org].

Usuários do Windows devem baixar a versão `Windows x86-64 executable installer` e na tela de instalação marcar a opção `Add Python 3.10 to PATH`:

```{image} docs/images/winpath.png
:alt: "Checkbox PATH na instala\xE7\xE3o Windows"
:width: 400
```

2. Suporte a língua Português (Brasil) no seu sistema operacional.

Pode ser instalado no Linux (Debian/Ubuntu) pelo comando:

```sh
$ apt-get install language-pack-pt-base
```

## Instalação

You can install _IRPF Investidor_ via [pip] from [PyPI]:

```sh
$ pip install irpf-investidor
```

## Uso

1. Entre na [Área do Investidor] da B3, faça login e entre no menu Extratos e Informativos → Negociação de Ativos → Escolha uma corretora e as datas 1 de Janeiro e 31 de Dezembro do ano em que deseja declarar. Em seguida clique no botão “Exportar para EXCEL”. Ele irá baixar o arquivo “InfoCEI.xls”.

**Ainda não é possível rodar o programa usando os novos arquivos XLSX, gerar no formato antigo.** Baixe e altere o [Template_InfoCEI.xls](Template_InfoCEI.xls).

Você pode combinar lançamentos de anos diferentes em um mesmo documento colando as linhas de um relatório em outro, mas mantenha a ordem cronológica.

2. Execute o programa através do comando:

```sh
$ irpf-investidor
```

O programa irá procurar o arquivo "InfoCEI.xls" na pasta atual (digite `pwd` no terminal para sabe qual é) ou na pasta downloads e exibirá na tela os resultados.

Ao executar, o programa pede para selecionar operações realizadas em leilão. Essa informação não pode ser obtida nos relatórios da `Área do Investidor` da B3 e precisam ser buscadas diretamente com a sua corretora de valores. Isso afeta o cálculo dos emolumentos e do custo médio.

## Aviso legal (disclaimer)

Esta é uma ferramenta com código aberto e gratuita, com licença MIT. Você pode alterar o código e distribuir, usar comercialmente como bem entender. Contribuições são muito bem vindas. Toda a responsabilidade de conferência dos valores e do envio dessas informações à Receita Federal é do usuário. Os desenvolvedores e colaboradores desse programa não se responsabilizam por quaisquer incorreções nos cálculos e lançamentos gerados.

## Créditos

Esse projeto foi gerado pelo template [@cjolowicz]'s [Hypermodern Python Cookiecutter].

<!-- github-only -->

[license]: https://github.com/staticdev/irpf-investidor/blob/main/LICENSE
[@cjolowicz]: https://github.com/cjolowicz
[hypermodern python cookiecutter]: https://github.com/cjolowicz/cookiecutter-hypermodern-python
[pip]: https://pip.pypa.io/
[pypi]: https://pypi.org/
[python.org]: https://www.python.org/downloads/
[uso]: https://irpf-investidor.readthedocs.io/en/latest/usage.html
[área do investidor]: https://www.investidor.b3.com.br/
