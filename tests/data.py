# -*- coding: utf-8 -*-
UNIQUE_SCORE_TEST_TABLE = {
    "title": "testing",
    "hit_policy": "Unique",
    "inputs": {
        "cols": [{"id": "score"}, {"id": "sex"}],
        "rows": [
            ["[0..70]", '"boy"'],
            ["(70..80]", '"boy"'],
            ["(80..90]", '"boy"'],
            ["(90..100]", '"boy"'],
            ["[0..60]", '"girl"'],
            ["(60..70]", '"girl"'],
            ["(70..80]", '"girl"'],
            ["(80..100]", '"girl"'],
        ],
    },
    "outputs": {
        "cols": [{"id": "level"}],
        "rows": [
            ['"bad"'],
            ['"good"'],
            ['"good+"'],
            ['"good++"'],
            ['"bad"'],
            ['"good"'],
            ['"good+"'],
            ['"good++"'],
        ],
    },
}

UNIQUE_TEST_DATA = [
    (UNIQUE_SCORE_TEST_TABLE, {"score": 10, "sex": "boy"}, [{"level": "bad"}]),
    (UNIQUE_SCORE_TEST_TABLE, {"score": 80, "sex": "boy"}, [{"level": "good"}]),
    (UNIQUE_SCORE_TEST_TABLE, {"score": 95, "sex": "boy"}, [{"level": "good++"}]),
    (UNIQUE_SCORE_TEST_TABLE, {"score": 65, "sex": "girl"}, [{"level": "good"}]),
    (UNIQUE_SCORE_TEST_TABLE, {"score": 75, "sex": "girl"}, [{"level": "good+"}]),
    (UNIQUE_SCORE_TEST_TABLE, {"score": 84, "sex": "girl"}, [{"level": "good++"}]),
]


ANY_SCORE_TEST_TABLE = {
    "title": "testing",
    "hit_policy": "Any",
    "inputs": {
        "cols": [{"id": "score"}, {"id": "sex"}],
        "rows": [
            ["[0..70]", '"boy"'],
            ["(70..80]", '"boy"'],
            ["(80..90]", '"boy"'],
            ["(90..100]", '"boy"'],
            ["[0..60]", '"girl"'],
            ["(60..70]", '"girl"'],
            ["(70..80]", '"girl"'],
            ["(80..100]", '"girl"'],
            ["(90..100]", ""],
        ],
    },
    "outputs": {
        "cols": [{"id": "level"}],
        "rows": [
            ['"bad"'],
            ['"good"'],
            ['"good+"'],
            ['"good++"'],
            ['"bad"'],
            ['"good"'],
            ['"good+"'],
            ['"good++"'],
            ['"good++"'],
        ],
    },
}

ANY_TEST_DATA = [
    (ANY_SCORE_TEST_TABLE, {"score": 95, "sex": "girl"}, [{"level": "good++"}]),
    (ANY_SCORE_TEST_TABLE, {"score": 75, "sex": "girl"}, [{"level": "good+"}]),
]

FIRST_SCORE_TEST_TABLE = {
    "title": "testing",
    "hit_policy": "First",
    "inputs": {
        "cols": [{"id": "score"}, {"id": "sex"}],
        "rows": [
            ["(90..100]", ""],
            ["(80..100]", '"boy"'],
        ],
    },
    "outputs": {
        "cols": [{"id": "level"}],
        "rows": [
            ['"good++"'],
            ['"good+"'],
        ],
    },
}

FIRST_TEST_DATA = [
    (FIRST_SCORE_TEST_TABLE, {"score": 95, "sex": "girl"}, [{"level": "good++"}]),
    (FIRST_SCORE_TEST_TABLE, {"score": 91, "sex": "boy"}, [{"level": "good++"}]),
    (FIRST_SCORE_TEST_TABLE, {"score": 85, "sex": "boy"}, [{"level": "good+"}]),
]


PRIORITY_SCORE_TEST_TABLE = {
    "title": "testing",
    "hit_policy": "Priority",
    "inputs": {
        "cols": [{"id": "score"}, {"id": "sex"}],
        "rows": [
            ["(90..100]", ""],
            ["(80..100]", '"boy"'],
        ],
    },
    "outputs": {
        "cols": [{"id": "priority"}, {"id": "level"}],
        "rows": [
            ["1", '"good++"'],
            ["2", '"good+"'],
        ],
    },
}

PRIORITY_TEST_DATA = [
    (PRIORITY_SCORE_TEST_TABLE, {"score": 95, "sex": "girl"}, [{"priority": 1, "level": "good++"}]),
    (PRIORITY_SCORE_TEST_TABLE, {"score": 91, "sex": "boy"}, [{"priority": 2, "level": "good+"}]),
    (PRIORITY_SCORE_TEST_TABLE, {"score": 85, "sex": "boy"}, [{"priority": 2, "level": "good+"}]),
]

RULE_ORDER_SCORE_TEST_TABLE = {
    "title": "testing",
    "hit_policy": "RuleOrder",
    "inputs": {
        "cols": [{"id": "score"}, {"id": "sex"}],
        "rows": [
            ["(90..100]", ""],
            ["(80..100]", '"boy"'],
        ],
    },
    "outputs": {
        "cols": [{"id": "level"}],
        "rows": [
            ['"good++"'],
            ['"good+"'],
        ],
    },
}

RULE_ORDER_TEST_DATA = [
    (RULE_ORDER_SCORE_TEST_TABLE, {"score": 95, "sex": "girl"}, [{"level": "good++"}]),
    (RULE_ORDER_SCORE_TEST_TABLE, {"score": 95, "sex": "boy"}, [{"level": "good++"}, {"level": "good+"}]),
    (RULE_ORDER_SCORE_TEST_TABLE, {"score": 85, "sex": "boy"}, [{"level": "good+"}]),
]


OUTPUT_ORDER_SCORE_TEST_TABLE = {
    "title": "testing",
    "hit_policy": "OutputOrder",
    "inputs": {
        "cols": [{"id": "score"}, {"id": "sex"}],
        "rows": [
            ["(80..100]", '"boy"'],
            ["(90..100]", ""],
        ],
    },
    "outputs": {
        "cols": [{"id": "level"}],
        "rows": [
            ['"good+"'],
            ['"good++"'],
        ],
    },
}

OUTPUT_ORDER_TEST_DATA = [
    (OUTPUT_ORDER_SCORE_TEST_TABLE, {"score": 95, "sex": "girl"}, [{"level": "good++"}]),
    (OUTPUT_ORDER_SCORE_TEST_TABLE, {"score": 95, "sex": "boy"}, [{"level": "good++"}, {"level": "good+"}]),
    (OUTPUT_ORDER_SCORE_TEST_TABLE, {"score": 85, "sex": "boy"}, [{"level": "good+"}]),
]


COLLECT_SCORE_TEST_TABLE = {
    "title": "testing",
    "hit_policy": "Collect",
    "inputs": {
        "cols": [{"id": "color"}],
        "rows": [
            ['"red"'],
            ['"yellow", "green"'],
            ['"green", "red"'],
            ['"yellow", "black"'],
            ['"white"'],
        ],
    },
    "outputs": {
        "cols": [{"id": "score"}],
        "rows": [
            ["1"],
            ["2"],
            ["3"],
            ["4"],
            ["5"],
        ],
    },
}


COLLECT_TEST_DATA = [
    (COLLECT_SCORE_TEST_TABLE, {"color": "green"}, [{"score": 2}, {"score": 3}]),
    ({**COLLECT_SCORE_TEST_TABLE, "hit_policy": "Collect(Sum)"}, {"color": "green"}, [{"score": 5}]),
    ({**COLLECT_SCORE_TEST_TABLE, "hit_policy": "Collect(Min)"}, {"color": "green"}, [{"score": 2}]),
    ({**COLLECT_SCORE_TEST_TABLE, "hit_policy": "Collect(Max)"}, {"color": "green"}, [{"score": 3}]),
    ({**COLLECT_SCORE_TEST_TABLE, "hit_policy": "Collect(Count)"}, {"color": "green"}, [{"score": 2}]),
]


COLLECT_100_RULES_TEST_TABLE = {
    "title": "testing",
    "hit_policy": "Collect(Sum)",
    "inputs": {
        "cols": [{"id": "color"}],
        "rows": [],
    },
    "outputs": {
        "cols": [{"id": "score"}],
        "rows": [],
    },
}

COLLECT_100_RULES_TEST_TABLE["inputs"]["rows"] = [['"red"'] for _ in range(100)]
COLLECT_100_RULES_TEST_TABLE["outputs"]["rows"] = [["1"] for _ in range(100)]

BATCH_TEST_DATA = [
    (COLLECT_100_RULES_TEST_TABLE, {"color": "red"}, [{"score": 100}]),
    (COLLECT_100_RULES_TEST_TABLE, {"color": "green"}, []),
]
