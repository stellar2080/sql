RECEIVER = "receiver"

FILTER = "filter"

DECOMPOSER = "decomposer"

REVISER = "reviser"

MANAGER = "manager"

AGENT_LIST = [FILTER, DECOMPOSER, REVISER, MANAGER]

MAX_ITERATIONS = 6

TEMPERATURE = 0.2

MAX_TOKENS = 1000

N_RESULTS_DOC = 6

N_RESULTS_KEY = 6

N_RESULTS_SC = 6

N_RESULTS_MEMORY = 3

N_LAST_MEMORY = 1

TOOLS = [
    {
        'type': 'function',
        'function': {
            'name': 'query_database',
            'description': 'No arguments needed, query the financial databases.'
        }
    }
]

FUNC_NAMES = ['query_database']