import os
import sys
from pathlib import Path

os.environ["ROTALIVRE_BACKEND"] = "stub"   # testes não usam LLM; resultados vão para a pasta temporária
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
