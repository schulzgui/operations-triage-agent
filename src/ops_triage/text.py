import re
import unicodedata
STOP={"a","o","e","de","da","do","na","no","um","uma","meu","minha","com","para","quero","qual","foi","esta","as","os","em"}

def tokens(text):
 text=unicodedata.normalize("NFKD",text.lower()).encode("ascii","ignore").decode()
 return [t for t in re.findall(r"[a-z0-9]+",text) if t not in STOP]
