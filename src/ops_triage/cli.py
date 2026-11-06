import argparse
import csv
import hashlib
import json
import platform
from pathlib import Path
from . import data
from . import agent

def dump(path,obj):
 path.write_text(json.dumps(obj,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")

def run(base):
 base=Path(base);data.generate(base/"data");out=base/"artifacts";out.mkdir(parents=True,exist_ok=True)
 tickets=json.loads((base/"data/tickets.json").read_text(encoding="utf-8"))
 report=agent.evaluate(tickets)
 report={"synthetic":True,"seed":data.SEED,**report}
 dump(out/"metrics.json",report)
 sources=list((base/"data").glob("*"))+list(Path(__file__).parent.glob("*.py"))
 dump(out/"manifest.json",{"python":platform.python_version(),"seed":data.SEED,"synthetic":True,
 "sha256":{("src/ops_triage/"+p.name if p.suffix==".py" else "data/"+p.name):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(sources)}})
 print("Avaliação sintética salva em",out/"metrics.json")
 return report

def main():
 parser=argparse.ArgumentParser(description="Operations Triage Agent")
 parser.add_argument("command",choices=["run","serve"])
 parser.add_argument("--base",default=".");parser.add_argument("--port",type=int,default=8003)
 args=parser.parse_args()
 if args.command=="run":run(args.base)
 else:
  from .server import serve
  serve(Path(args.base),args.port)
if __name__=="__main__":main()
