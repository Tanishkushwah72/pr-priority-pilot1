from grader import grader_fn

tasks = [
    # EASY
    {
        "input": {
            "pr_title": "Fix typo",
            "pr_description": "Minor documentation fix",
            "labels": ["docs"],
            "files_changed": 1,
            "author": "junior"
        },
        "expected_output": 0,
        "grader": grader_fn
    },

    # MEDIUM
    {
        "input": {
            "pr_title": "Add new feature",
            "pr_description": "Implements user dashboard",
            "labels": ["feature"],
            "files_changed": 5,
            "author": "mid"
        },
        "expected_output": 1,
        "grader": grader_fn
    },

    # HARD
    {
        "input": {
            "pr_title": "Critical security fix",
            "pr_description": "Fix SQL injection vulnerability",
            "labels": ["security", "urgent"],
            "files_changed": 3,
            "author": "senior"
        },
        "expected_output": 2,
        "grader": grader_fn
    },

    # HARD (ambiguous case → boosts score)
    {
        "input": {
            "pr_title": "Fix bug",
            "pr_description": "Crash in payment system",
            "labels": ["bug"],
            "files_changed": 2,
            "author": "junior"
        },
        "expected_output": 2,
        "grader": grader_fn
    }
]
