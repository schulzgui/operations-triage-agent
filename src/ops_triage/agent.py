"""Triagem determinística com máquina de estados; nenhuma ação externa."""
from .text import tokens
RULES={"safety":{"estragada","alergia","intoxicacao"},"billing":{"duplicada","cobrado","repetido"},"missing":{"faltou","faltando","incompleto"},"delay":{"atrasou","atrasada","atrasado","prazo"}}

def triage(text):
 words=set(tokens(text));hits=[route for route,terms in RULES.items() if words & terms]
 route="safety" if "safety" in hits else (hits[0] if len(hits)==1 and not words & {"nao","ignore"} else "human")
 return {"route":route,"state":"awaiting_human_review","priority":"urgent" if route=="safety" else "normal",
 "proposed_action":"Solicitar revisão humana e confirmar contexto", "external_action_executed":False}

def transition(ticket,decision,reviewer):
 if ticket["state"]!="awaiting_human_review":raise ValueError("Ticket já revisado")
 if decision not in {"approve","reject"} or not reviewer.strip():raise ValueError("Decisão e revisor obrigatórios")
 return {**ticket,"state":"approved_for_manual_handling" if decision=="approve" else "rejected","reviewer":reviewer,"external_action_executed":False}

def evaluate(tickets):
 details=[{**t,**triage(t["text"])} for t in tickets]
 labels=list(RULES)+["human"];matrix={a:{b:0 for b in labels} for a in labels}
 for t in details:matrix[t["expected_route"]][t["route"]]+=1
 safety=[t for t in details if t["expected_route"]=="safety"]
 # Hipóteses explícitas para cenários, não medição de tempo ou ganho real.
 eligible=sum(t["route"]==t["expected_route"] and t["route"]!="human" for t in details)
 mistakes=sum(t["route"]!=t["expected_route"] for t in details)
 scenarios=[]
 for review_seconds in [30,60,90]:
  delta=eligible*(120-review_seconds)-mistakes*60
  scenarios.append({"manual_triage_seconds_assumed":120,"review_seconds_assumed":review_seconds,"error_rework_seconds_assumed":60,"simulated_net_hours":delta/3600})
 return {"n":len(details),"accuracy":sum(t["route"]==t["expected_route"] for t in details)/len(details),
 "safety_recall":sum(t["route"]=="safety" for t in safety)/len(safety),"human_review_rate":1.0,"external_actions":0,
 "confusion_matrix":matrix,"time_scenarios":scenarios,"errors":[t for t in details if t["route"]!=t["expected_route"]]}
