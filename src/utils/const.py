EXTRACTOR = "extractor"
FILTER = "filter"
GENERATOR = "generator"
REVISER = "reviser"
MANAGER = "manager"

MAX_ITERATIONS = 8

DO_SAMPLE = False
TEMPERATURE = 0.05
TOP_K = 5
TOP_P = 0.05
MAX_LENGTH = 8192

N_RESULTS_KEY = 3

E_HINT_THRESHOLD = 0.30
E_COL_THRESHOLD = 0.30
E_VAL_THRESHOLD = 0.30
E_COL_STRONG_THRESHOLD = 0.48
E_VAL_STRONG_THRESHOLD = 0.48

F_HINT_THRESHOLD = 0.80
F_LSH_THRESHOLD = 0.40
F_COL_THRESHOLD = 0.60
F_VAL_THRESHOLD = 0.60
F_COL_STRONG_THRESHOLD = 0.85
F_VAL_STRONG_THRESHOLD = 0.85

G_HINT_THRESHOLD = 0.30

LLM_HOST = 'localhost'
LLM_PORT = 6006