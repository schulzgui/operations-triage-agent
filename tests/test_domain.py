import concurrent.futures
import tempfile
import math
import unittest
from pathlib import Path
from ops_triage.agent import triage
from ops_triage.store import Store

class AgentTests(unittest.TestCase):
 def test_safety_priority(self):self.assertEqual(triage('Atrasou e comida estragada')['route'],'safety')
 def test_negation_and_ambiguity(self):
  for text in ['Não houve atraso','Atrasou e faltou um item']:
   self.assertEqual(triage(text)['route'],'human')
 def test_transaction_and_review(self):
  with tempfile.TemporaryDirectory() as d:
   s=Store(Path(d)/'db');first=s.process('x','Faltou bebida')
   self.assertEqual(first,s.process('x','Faltou bebida'))
   with self.assertRaises(ValueError):s.process('x','Outra mensagem')
   self.assertEqual(s.db.execute('SELECT count(*) FROM events').fetchone()[0],1)
   with self.assertRaises(ValueError):s.review('x','approve','')
   result=s.review('x','approve','revisor-demo');self.assertFalse(result['external_action_executed'])
   with self.assertRaises(ValueError):s.review('x','approve','revisor-demo')
   s.close()
 def test_concurrent_idempotency(self):
  with tempfile.TemporaryDirectory() as d:
   path=Path(d)/'db';s=Store(path);s.close()
   def work(_):
    s=Store(path)
    try:return s.process('same','Comida estragada')
    finally:s.close()
   with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:results=list(pool.map(work,range(12)))
   self.assertTrue(all(r==results[0] for r in results))
   s=Store(path);self.assertEqual(s.db.execute('SELECT count(*) FROM events').fetchone()[0],1);s.close()
