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

TOOLS = [
[
    {
        'type': 'function',
        'function': {
            'name': 'get_schema',
            'description': 'Get the schema of financial databases'
        }
    }
],

[
    {
        'type': 'function',
        'function': {
            'name': 'query_database',
            'description': 'Convert natural language questions into SQL and query the database'
        }
    }
]
]

FUNC_NAMES = ['get_schema','query_database']