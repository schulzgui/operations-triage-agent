# Decisões para discutir

600 sorteios de 17 templates, em cinco classes. A avaliação mede acurácia, matriz de confusão e recall de segurança, e lista os erros. Os 600 registros não são 600 formulações independentes.

Idempotência: mesma chave e mesmo texto retornam o resultado já gravado; mesma chave com outro texto falha. Revisão só ocorre em `awaiting_human_review`, exige decisão válida e identificador do revisor. Aprovação **não executa reembolso ou qualquer ação externa**. Trata-se de um agente especializado determinístico; não usa LLM nem planejamento autônomo.

## Demonstração

1. Envie “Faltou minha bebida” com chave `demo-001`.
2. Repita o mesmo conteúdo/chave e veja o resultado preservado.
3. Altere o texto mantendo a chave e observe a rejeição.
4. Com nova chave, envie “Comida estragada”: prioridade urgente e revisão obrigatória.
5. Execute a revisão pela API Python e veja que não há efeito externo.

## Limitações

- Regras lexicais limitadas; “Veio um item a menos” não é reconhecido e segue para humano.
- Identificador do revisor não é autenticação.
- Auditoria é append-only na aplicação, mas pode ser alterada por quem controla o banco.
- Não há integração externa, outbox, fila distribuída ou garantia de exactly-once entre serviços.
- Cenários de tempo não são ganhos reais e não incluem custos de implantação, supervisão ou consequências dos erros.

## Próximo experimento

Adicionar outbox com retries e dead-letter queue, autenticação/RBAC, classificação semântica avaliada em dados independentes e estudo de tempo com usuários.

Explique o código com suas próprias palavras e informe o uso de assistência de IA. Este repositório não representa trabalho realizado no iFood.
