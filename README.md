# MVP Marceneiro Pro

Aplicação web full stack para pequenos marceneiros criarem orçamentos avançados de móveis planejados, com:

- geração automática de peças;
- plano de corte 2D simplificado;
- cálculo de fita de borda e ferragens;
- sugestão de uso de retalhos;
- cálculo financeiro (custo, margem, lucro e preço sugerido);
- alertas de risco e nota de confiança;
- lista de compra e ordem de produção;
- geração de PDF para cliente e PDF técnico interno.

## Stack

- Backend: Django + Django REST Framework
- Frontend: React + TypeScript (Vite)
- Banco principal: PostgreSQL
- PDFs: ReportLab

## Estrutura

```text
backend/
  manage.py
  requirements.txt
  marcenaria/
  orcamentos/
frontend/
  src/
README.md
docker-compose.yml
```

## Subir o PostgreSQL (local)

```bash
docker compose up -d
```

## Rodar backend

1. Entrar na pasta:

```bash
cd backend
```

2. Instalar dependências:

```bash
python -m pip install -r requirements.txt
```

3. Configurar ambiente:

- Copie `backend/.env.example` para `.env` (opcional, já existem defaults de desenvolvimento).

4. Aplicar migrations:

```bash
python manage.py migrate
```

5. Carregar seed inicial:

```bash
python manage.py seed_dados
```

6. Rodar servidor:

```bash
python manage.py runserver
```

Backend em: `http://127.0.0.1:8000`

## Rodar frontend

1. Entrar na pasta:

```bash
cd frontend
```

2. Instalar dependências:

```bash
npm install
```

3. Opcional: configurar URL da API em `.env`:

```env
VITE_API_URL=http://127.0.0.1:8000/api
```

4. Rodar:

```bash
npm run dev
```

Frontend em: `http://127.0.0.1:5173`

## Endpoints principais da API

- `GET/POST /api/clientes/`
- `GET/PUT/DELETE /api/clientes/{id}/`
- `GET/POST /api/materiais/`
- `GET/PUT/DELETE /api/materiais/{id}/`
- `GET/POST /api/retalhos/`
- `GET/PUT/DELETE /api/retalhos/{id}/`
- `GET/POST /api/orcamentos/`
- `GET/PUT/DELETE /api/orcamentos/{id}/`
- `POST /api/orcamentos/{id}/calcular/`
- `POST /api/orcamentos/{id}/gerar_pecas/`
- `GET /api/orcamentos/{id}/plano_corte/`
- `GET /api/orcamentos/{id}/pdf_cliente/`
- `GET /api/orcamentos/{id}/pdf_tecnico/`
- `POST /api/orcamentos/{id}/duplicar/`
- `POST /api/orcamentos/{id}/aprovar/`
- `POST /api/orcamentos/{id}/recusar/`
- `GET /api/dashboard/`

## Fluxo de cálculo (`POST /api/orcamentos/{id}/calcular/`)

O endpoint executa o pipeline:

1. gera peças automáticas por tipo de móvel;
2. calcula plano de corte por material;
3. calcula fita de borda;
4. calcula ferragens;
5. sugere uso de retalhos;
6. monta custos (chapas, ferragens, fita, mão de obra, instalação, frete, extras);
7. calcula preço sugerido, margem real e lucro;
8. gera alertas de risco e nota de confiança;
9. gera lista de compra e ordem de produção;
10. salva resultado completo em `orcamento.resultado_calculo`.

## Testes unitários (backend)

Foram implementados testes para:

- cálculo de margem real/preço sugerido;
- cálculo de fita de borda;
- geração de peças de guarda-roupa;
- regra de dobradiças por altura;
- plano de corte simples;
- cálculo de aproveitamento.

Rodar:

```bash
cd backend
set DJANGO_USE_SQLITE=1 && python manage.py test
```

Observação: para testes rápidos, `DJANGO_USE_SQLITE=1` evita depender de PostgreSQL.

## Dados de seed incluídos

- Materiais (MDF, fita, ferragens, insumos) conforme lista solicitada.
- Clientes: João Carlos, Maria Souza, Ana Paula.
- Retalhos: 3 exemplos.
- 3 orçamentos de exemplo (guarda-roupa, painel de TV, armário aéreo), já calculados.

## PDFs

- **Cliente**: sem custos internos sensíveis por padrão.
- **Técnico**: inclui custos detalhados, lista de compra, alertas, margem e ordem de produção.
- Campo `mostrar_detalhamento_pdf_cliente` habilita resumo técnico adicional no PDF do cliente.

## O que foi simplificado neste MVP

- Otimizador de corte: estratégia shelf/bin packing simples, focada em clareza e evolução futura.
- Sugestão de retalhos: heurística simplificada para viabilidade e economia estimada.
- Layout frontend: interface funcional e responsiva, com foco em operação local e validação do fluxo.

## Próximos passos recomendados

- autenticação de usuários e perfis;
- catálogo configurável de regras de móveis/ferragens sem alterar código;
- versionamento de orçamento e histórico de cálculo;
- exportação técnica com visual mais detalhado de corte e etiquetas de peças.
