"""Inbox transacional, idempotência e trilha de auditoria SQLite."""
import hashlib
import json
import sqlite3
from .agent import triage,transition

class Store:
 def __init__(self,path):
  self.db=sqlite3.connect(path,timeout=10)
  self.db.execute("PRAGMA journal_mode=WAL")
  self.db.executescript("""
  CREATE TABLE IF NOT EXISTS tickets (id TEXT PRIMARY KEY, digest TEXT NOT NULL, payload TEXT NOT NULL);
  CREATE TABLE IF NOT EXISTS events (seq INTEGER PRIMARY KEY AUTOINCREMENT, ticket_id TEXT NOT NULL, kind TEXT NOT NULL, payload TEXT NOT NULL);
  """)
 def close(self):self.db.close()
 def process(self,key,text):
  if not key.strip() or not text.strip():raise ValueError("Chave e texto obrigatórios")
  digest=hashlib.sha256(text.encode()).hexdigest()
  with self.db:
   self.db.execute("BEGIN IMMEDIATE")
   previous=self.db.execute("SELECT digest,payload FROM tickets WHERE id=?",(key,)).fetchone()
   if previous:
    if previous[0]!=digest:raise ValueError("Chave reutilizada com conteúdo diferente")
    return json.loads(previous[1])
   result={"ticket_id":key,**triage(text)};payload=json.dumps(result)
   self.db.execute("INSERT INTO tickets VALUES (?,?,?)",(key,digest,payload))
   self.db.execute("INSERT INTO events(ticket_id,kind,payload) VALUES (?,?,?)",(key,"triaged",payload))
   return result
 def review(self,key,decision,reviewer):
  with self.db:
   self.db.execute("BEGIN IMMEDIATE")
   row=self.db.execute("SELECT payload FROM tickets WHERE id=?",(key,)).fetchone()
   if not row:raise KeyError(key)
   result=transition(json.loads(row[0]),decision,reviewer);payload=json.dumps(result)
   self.db.execute("UPDATE tickets SET payload=? WHERE id=?",(payload,key))
   self.db.execute("INSERT INTO events(ticket_id,kind,payload) VALUES (?,?,?)",(key,"reviewed",payload))
   return result
