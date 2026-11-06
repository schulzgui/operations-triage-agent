# Data card — Operations Triage Agent

**100% sintético; licença MIT.**

`tickets.json` contém 600 tickets sintéticos com prefixo SYN-T, texto, classe esperada e `synthetic=true`. Semente base 42; gerador usa 43. Templates incluem ambiguidades, negação e pedido de ignorar regras. Sem dados pessoais ou tickets de clientes reais.

Gerador: `src/ops_triage/data.py`. Semente base 42, sem dados externos, scraping, nomes de clientes ou operação real.

- Regras lexicais limitadas; “Veio um item a menos” não é reconhecido e segue para humano.
- Identificador do revisor não é autenticação.
- Auditoria é append-only na aplicação, mas pode ser alterada por quem controla o banco.
- Não há integração externa, outbox, fila distribuída ou garantia de exactly-once entre serviços.
- Cenários de tempo não são ganhos reais e não incluem custos de implantação, supervisão ou consequências dos erros.
