# Operations Triage Agent

**Triagem operacional determinística com revisão humana obrigatória, persistência transacional, idempotência e auditoria.**

Guilherme Schulz · Portfólio técnico independente · Python 3.10+ · Licença MIT

> Todos os dados e políticas são sintéticos. Não há vínculo com o iFood, implantação empresarial ou impacto comercial medido. Projeto desenvolvido com assistência de IA; implementação, testes e limitações estão disponíveis para revisão.

## Problema e objetivo

Uma equipe de atendimento precisa classificar solicitações e encaminhar casos urgentes sem gerar ações financeiras indevidas ou processar duas vezes a mesma mensagem. O laboratório demonstra esse fluxo com templates sintéticos.

## O que está implementado

- Cinco rotas: atraso, item ausente, segurança alimentar, cobrança e atendimento humano.
- Prioridade de segurança; ambiguidades e negações simples seguem para humano.
- Máquina de estados com aprovação/rejeição para tratamento manual.
- SQLite com WAL, transação `BEGIN IMMEDIATE`, chave única e hash do conteúdo.
- Auditoria de triagem e revisão na mesma transação.
- Teste com 12 solicitações concorrentes e cenários explícitos de tempo.

## Executar localmente

Este repositório é independente: não exige o monorepositório original nem os outros dois projetos. Não requer chave de API, serviço pago ou dependências Python de execução. Extraia o ZIP e abra um terminal na raiz de `operations-triage-agent`.

macOS / Linux:

```bash
export PYTHONPATH=src
python3 -m ops_triage.cli run
python3 -m unittest discover -s tests -v
python3 -m ops_triage.cli serve
```

Windows PowerShell:

```powershell
$env:PYTHONPATH = "src"
python -m ops_triage.cli run
python -m unittest discover -s tests -v
python -m ops_triage.cli serve
```

Abra [a demo local](http://127.0.0.1:8003). Encerre com Ctrl+C. Para outra porta, use `serve --port 9000`. Execute na raiz do repositório; `--base CAMINHO` permite escolher outro diretório de dados/artefatos.

Opcional: `python3 -m pip install -e .` instala o comando `operations-triage-agent`. Após a instalação, use `operations-triage-agent run` ou `operations-triage-agent serve`. A instalação requer obter o build backend se ele não estiver instalado; a execução por `PYTHONPATH` funciona sem esse passo.

## Arquitetura

```text
Mensagem + chave → verificação de idempotência → classificação → awaiting_human_review
Revisão humana → approved_for_manual_handling OU rejected
Transação SQLite → ticket + evento de auditoria (sem efeito externo)
```

`agent.py`: roteamento e estados; `store.py`: transações e auditoria; `text.py`: normalização; `data.py`: templates.

## Método e avaliação

600 sorteios de 17 templates, em cinco classes. A avaliação mede acurácia, matriz de confusão e recall de segurança, e lista os erros. Os 600 registros não são 600 formulações independentes.

Idempotência: mesma chave e mesmo texto retornam o resultado já gravado; mesma chave com outro texto falha. Revisão só ocorre em `awaiting_human_review`, exige decisão válida e identificador do revisor. Aprovação **não executa reembolso ou qualquer ação externa**. Trata-se de um agente especializado determinístico; não usa LLM nem planejamento autônomo.

Resultados observados e contagens de testes: [relatório reproduzido](docs/RESULTADOS.md). Dados detalhados: [metrics.json](artifacts/metrics.json). Procedência: [manifest.json](artifacts/manifest.json).

O manifesto registra semente, Python e hashes SHA256 de dados e implementação. Não é uma assinatura criptográfica de autoria. O comando `run` sobrescreve os dados sintéticos e artefatos gerados no diretório escolhido.

## Dados e origem

`tickets.json` contém 600 tickets sintéticos com prefixo SYN-T, texto, classe esperada e `synthetic=true`. Semente base 42; gerador usa 43. Templates incluem ambiguidades, negação e pedido de ignorar regras. Sem dados pessoais ou tickets de clientes reais.

Leia o [data card](data/README.md). Os dados são distribuídos sob MIT, junto com o código.

## API local

| Método e rota | Função |
|---|---|
| `GET /` | Formulário de demonstração |
| `GET /health` | Verificação de disponibilidade |
| `GET /api/metrics` | Resultados da última execução |
| `POST /api/triage` | Executar a operação do projeto |

Com o servidor iniciado:

```bash
curl -X POST http://127.0.0.1:8003/api/triage \
  -H 'Content-Type: application/json' \
  -d '{"key": "demo-001", "text": "Faltou minha bebida"}'
```

A resposta é JSON. Entradas inválidas retornam HTTP 400, formato de conteúdo inadequado 415, origem incompatível 403 e rota desconhecida 404. Há limite de 8 KiB por corpo de requisição. A demo escuta apenas em `127.0.0.1`; não deve ser exposta à internet sem autenticação, TLS, servidor de produção e revisão de segurança.

## Testes e reprodução

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 scripts/verify_reproduction.py
```

O segundo comando compara dados gerados byte a byte e métricas/modelos JSON com tolerância numérica de `1e-10`, para acomodar arredondamento entre versões Python. A versão Python no manifesto pode variar. Os testes de integração iniciam a API em porta temporária e usam diretórios descartáveis. A CI está configurada para Python 3.10, 3.12 e 3.13; apenas os testes locais efetivamente executados são declarados no relatório.

## Estrutura

```text
src/ops_triage/      algoritmos, gerador, CLI e servidor
scripts/                 verificação dos artefatos versionados
tests/                   testes de domínio e integração HTTP
data/                    dados sintéticos e data card
artifacts/               métricas e manifesto de procedência
docs/                    resultados e roteiro técnico
.github/workflows/       CI por versão Python
```

## Demonstração para entrevista

1. Envie “Faltou minha bebida” com chave `demo-001`.
2. Repita o mesmo conteúdo/chave e veja o resultado preservado.
3. Altere o texto mantendo a chave e observe a rejeição.
4. Com nova chave, envie “Comida estragada”: prioridade urgente e revisão obrigatória.
5. Execute a revisão pela API Python e veja que não há efeito externo.

Leia [o guia técnico](docs/ENTREVISTA.md) e reproduza o experimento antes de apresentá-lo. Declare claramente a contribuição da assistência de IA e as modificações que você revisou ou realizou.

## Limitações e decisões

- Regras lexicais limitadas; “Veio um item a menos” não é reconhecido e segue para humano.
- Identificador do revisor não é autenticação.
- Auditoria é append-only na aplicação, mas pode ser alterada por quem controla o banco.
- Não há integração externa, outbox, fila distribuída ou garantia de exactly-once entre serviços.
- Cenários de tempo não são ganhos reais e não incluem custos de implantação, supervisão ou consequências dos erros.

A inspeção visual da demo ainda não foi concluída; os endpoints são cobertos por testes HTTP. Nenhum resultado deste laboratório comprova experiência profissional no iFood.

## Próximos experimentos — ainda não implementados

Adicionar outbox com retries e dead-letter queue, autenticação/RBAC, classificação semântica avaliada em dados independentes e estudo de tempo com usuários.

## Publicar como repositório separado

Crie um repositório vazio chamado `operations-triage-agent` na sua conta. Envie **o conteúdo da raiz deste projeto**, incluindo arquivos ocultos, sem a pasta externa e sem o ZIP. Alternativamente:

```bash
git init -b main
git add .
git commit -m "Add standalone reproducible project"
git remote add origin https://github.com/SEU_USUARIO/operations-triage-agent.git
git push -u origin main
```

Substitua `SEU_USUARIO` pelo seu login. Autenticação Git precisa estar configurada. Confirme a execução da aba Actions após o envio. Esses comandos não foram executados contra um novo repositório remoto nesta reorganização.

## Licença e contribuição

[MIT](LICENSE). Para propor alterações: descreva o problema, preserve a identificação sintética, execute os testes e regenere artefatos quando modificar dados ou algoritmos. Não atualize métricas manualmente para fazê-las parecer melhores.

## Revisão humana pela API Python

O formulário registra a triagem. A revisão está disponível pela API Python:

```python
from ops_triage.store import Store

store = Store("artifacts/demo.sqlite")
try:
    ticket = store.process("review-demo-001", "Comida estragada")
    result = store.review("review-demo-001", "approve", "revisor-demo")
    print(result)
finally:
    store.close()
```

Uma segunda revisão falha. Use outra chave em nova demonstração. O banco local e seus arquivos WAL/SHM estão no `.gitignore`; não publique interações pessoais. Aprovação significa apenas encaminhamento para tratamento manual.
