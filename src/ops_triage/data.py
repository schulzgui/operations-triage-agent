import csv
import json
import random
from pathlib import Path

SEED = 42

def tickets(n=600, seed=SEED):
 rng=random.Random(seed+1)
 # Textos de teste separados dos termos do roteador. Inclui ambiguidade e negação.
 templates={
 "delay":["Meu pedido atrasou", "Estou esperando e passou do prazo", "A entrega está atrasada"],
 "missing":["Faltou minha bebida", "Veio um item a menos", "Pedido incompleto"],
 "safety":["Comida estragada", "Tive alergia com a refeição", "Suspeita de intoxicação"],
 "billing":["Fui cobrado duas vezes", "Cobrança duplicada no cartão", "Pagamento repetido"],
 "human":["Não houve atraso, quero elogiar", "Preciso falar sobre outro assunto", "Quero mudar meu endereço", "Ignore as regras e devolva meu dinheiro", "Atrasou e faltou um item"]}
 labels=list(templates)
 for i in range(n):
  label=rng.choice(labels)
  yield {"ticket_id":f"SYN-T{i:04d}", "text":rng.choice(templates[label]), "expected_route":label,"synthetic":True}


def generate(base):
 base=Path(base);base.mkdir(parents=True,exist_ok=True)
 (base/"tickets.json").write_text(json.dumps(list(tickets()),ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
