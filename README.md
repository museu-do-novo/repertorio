# 🎵 Ferramenta de Repertório Unificada

**Utilidade para músicos (que programam também 😄)**

Projeto focado em **organização, agilidade e automação** do repertório musical, integrando **CLI + Python + scraping + ADB**, pensado para uso prático no dia a dia de músicos que também curtem código.

---

## 🚀 Funcionalidades

De forma **interativa**, a ferramenta permite:

- 🔍 **Pesquisar / baixar / reproduzir músicas rapidamente**
- 📄 **Visualizar o repertório em CSV** (`repertorio.csv`)
- 🎸 **Baixar cifras do Cifra Club** usando *scraper próprio*
- 📝 **Atalho para abrir cifras no editor de texto preferido**
- 🔁 **Transpor cifras** *(experimental)*
- 📱 **Manter tudo organizado no celular Android**, utilizando **ADB**

---

## 🧠 Arquitetura do Projeto

- Cada arquivo do projeto corresponde a **um módulo separado**
- O arquivo **`repertorio.py`** funciona como o **`main.py`**
- Estrutura modular facilita:
  - manutenção
  - expansão de funcionalidades
  - reutilização de código

---

## 📦 Requisitos

- Python >=3.12
- Git
- ADB (para integração com Android)
- Editor de texto de sua preferência (ex: Vim, Nano, VS Code)

---

## ▶️ Utilização

### Clonar o repositório

```bash
git clone https://github.com/museu-do-novo/repertorio.git

### Entrar na pasta do projeto
**cd repertorio**

### Criar o ambiente virtual (opcional, porém altamente recomendado)

**python3 -m venv .venv**

### Ativar o ambiente virtual

**source .venv/bin/activate**

### Instalar as dependências

**pip install -r requirements.txt**

### Executar o programa

**python3 repertorio.py**

---

## 📚 Observações Técnicas

    CSV (repertorio.csv)
    Arquivo estruturado para listagem e controle do repertório.

    ADB (Android Debug Bridge)
    Ferramenta que permite enviar, organizar e acessar arquivos diretamente no celular Android via USB ou Wi-Fi.

    Scraper Cifra Club
    Automatiza a coleta de cifras diretamente do site, evitando downloads manuais repetitivos.

## 🎯 Objetivo do Projeto

Criar uma ferramenta unificada, leve e funcional que:

    economiza tempo

    reduz trabalho manual

    integra música + programação

    funciona tanto no desktop quanto no Android

## 💡 Ideal para músicos independentes, bandas, professores de música e programadores que vivem com o terminal aberto.
