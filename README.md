# ProgridAI Tools API

API genérica e modular desenvolvida em FastAPI para ferramentas reutilizáveis da ProgridAI.

## Módulos Disponíveis

### `/privacy`
Responsável por detectar, substituir (sanitizar), validar e restaurar dados sensíveis (PII) em textos livres antes do envio para modelos de inteligência artificial (LLMs). Todo processamento ocorre localmente.

Tecnologias utilizadas:
- **FastAPI**: Framework web.
- **Microsoft Presidio**: Ferramenta open-source para detecção e anonimização de entidades sensíveis.
- **spaCy**: Utilizado com o modelo `pt_core_news_lg` para melhorar a detecção de nomes e entidades em português.
- **Validações Customizadas**: Expressões regulares e algoritmos de dígito verificador para CPF e CNPJ.

## Executando Localmente

### Pré-requisitos
- Python 3.11+
- pip

### Passos
1. Clone o repositório.
2. Crie um ambiente virtual: `python -m venv venv`
3. Ative o ambiente virtual (`venv\Scripts\activate` no Windows, `source venv/bin/activate` no Linux/Mac).
4. Instale as dependências: `pip install -r requirements.txt`
5. Baixe o modelo do spaCy: `python -m spacy download pt_core_news_lg`
6. Copie o `.env.example` para `.env` e configure sua `API_KEY`.
7. Execute o servidor: `uvicorn app.main:app --reload`
8. Acesse a documentação em `http://127.0.0.1:8000/docs`.

## Executando com Docker

O projeto já contém um `Dockerfile` pronto para build, inclusive para plataformas como o EasyPanel.

1. Faça o build da imagem:
   ```bash
   docker build -t progridai-tools-api .
   ```
2. Execute o contêiner:
   ```bash
   docker run -d -p 8000:8000 --env-file .env progridai-tools-api
   ```

## Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto com base no `.env.example`:

```env
API_KEY=
```

A `API_KEY` é exigida no header `X-API-Key` para todos os endpoints `/privacy/*`.

## Endpoints Principais

- `GET /health`: Verifica o status da API (Público).
- `GET /version`: Retorna a versão (Público).
- `POST /privacy/sanitize`: Substitui dados sensíveis por tokens.
- `POST /privacy/restore`: Restaura dados originais a partir de tokens (válido por 24h em memória).
- `POST /privacy/detect`: Apenas lista as entidades encontradas.
- `POST /privacy/validate`: Verifica se o texto é seguro (sem PII) para enviar à LLM.
- `DELETE /privacy/maps/{mapId}`: Apaga um mapa de restauração manualmente.

*Para exemplos completos de requisição e resposta, verifique o Swagger UI em `/docs` após subir a API.*
