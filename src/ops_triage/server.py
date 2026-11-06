from .store import Store
"""Demo somente em loopback, sem arquivos arbitrários ou chamadas externas."""
import json
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from urllib.parse import urlparse

HTML = """<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Operations Triage Agent</title>
<style>body{font:16px system-ui;background:#101724;color:#eef3ff;max-width:1080px;margin:40px auto;padding:20px}h1{font-size:42px}small{color:#b4c7df}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(290px,1fr));gap:18px}section{background:#1c293c;padding:22px;border-radius:14px}input,button,textarea{box-sizing:border-box;padding:12px;margin:6px 0;width:100%;border-radius:7px;border:1px solid #7290b5}button{background:#b8f874;font-weight:bold;cursor:pointer}pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:13px}label{display:block}details{margin:24px 0}</style>
<h1>Operations Triage Agent</h1><p>Laboratório independente · <b>100% dados sintéticos</b> · sem vínculo com o iFood</p><small>ML, recuperação de informação e automação auditável. Nenhuma ação financeira é executada.</small>
<div class="grid"><section><h2>03 / Triagem auditável</h2><form id="triage"><label>Chave única<input name="key" value="demo-001"></label><label>Mensagem<textarea name="text">Faltou minha bebida</textarea></label><button>Registrar e propor encaminhamento</button></form><pre id="triage-out"></pre><small>Repetir a chave preserva o resultado. Alterar conteúdo exige outra chave.</small></section></div>
<details><summary>Métricas completas e hipóteses</summary><pre id="metrics"></pre></details>
<script>
for(const name of ['triage'])document.getElementById(name).onsubmit=async e=>{e.preventDefault();const out=document.getElementById(name+'-out');try{const payload=Object.fromEntries(new FormData(e.target));const r=await fetch('/api/'+name,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});out.textContent=JSON.stringify(await r.json(),null,2)}catch(e){out.textContent='Falha de conexão'}};
fetch('/api/metrics').then(r=>r.json()).then(x=>document.getElementById('metrics').textContent=JSON.stringify(x,null,2));
</script></html>"""

def handler(base):
 class Handler(BaseHTTPRequestHandler):
  def send(self,status,payload,kind="application/json"):
   body=(json.dumps(payload,ensure_ascii=False) if kind=="application/json" else payload).encode()
   self.send_response(status);self.send_header("Content-Type",kind+"; charset=utf-8");self.send_header("Content-Length",str(len(body)));self.send_header("X-Content-Type-Options","nosniff");self.end_headers();self.wfile.write(body)
  def do_GET(self):
   path=urlparse(self.path).path
   if path=="/":self.send(200,HTML,"text/html")
   elif path=="/api/metrics":self.send(200,json.loads((base/"artifacts/metrics.json").read_text(encoding="utf-8")))
   elif path=="/health":self.send(200,{"status":"ok","synthetic":True})
   else:self.send(404,{"error":"Rota inexistente"})
  def do_POST(self):
   # JSON estrito + sem CORS; evita formulários cross-origin alterando o SQLite local.
   if self.headers.get("Content-Type","").split(";")[0]!="application/json":return self.send(415,{"error":"Use application/json"})
   origin=self.headers.get("Origin")
   if origin and origin!=f"http://127.0.0.1:{self.server.server_port}":return self.send(403,{"error":"Origem não permitida"})
   try:
    length=int(self.headers.get("Content-Length","0"))
    if not 0<length<=8192:raise ValueError("Corpo deve ter entre 1 e 8192 bytes")
    obj=json.loads(self.rfile.read(length))
    if not isinstance(obj,dict):raise ValueError("Objeto JSON obrigatório")
    path=urlparse(self.path).path
    if path=="/api/triage":
     store=Store(base/"artifacts/demo.sqlite")
     try:result=store.process(str(obj["key"]),str(obj["text"]))
     finally:store.close()
    else:return self.send(404,{"error":"Rota inexistente"})
    self.send(200,result)
   except (ValueError,KeyError,TypeError):self.send(400,{"error":"Entrada inválida ou chave já usada com outro conteúdo"})
  def log_message(self,*args):pass
 return Handler

def serve(base,port):
 if not (base/"artifacts/metrics.json").exists():raise SystemExit("Execute primeiro: python -m ops_triage.cli run")
 server=ThreadingHTTPServer(("127.0.0.1",port),handler(base))
 print(f"Demo sintética: http://127.0.0.1:{server.server_port}",flush=True)
 try:server.serve_forever()
 except KeyboardInterrupt:pass
 finally:server.server_close()
