"""Fixtures for bw_aggregation"""

import pytest
from bw2data import Database, Method
from bw2data.tests import bw2test


@pytest.fixture
@bw2test
def background():
    bio_data = {
        ("bio", "alpha"): {"exchanges": [], "type": "biosphere"},
        ("bio", "beta"): {"exchanges": [], "type": "biosphere"},
    }
    Database("bio").write(bio_data)

    cfs = [
        (("bio", "alpha"), 4),
        (("bio", "beta"), -2),
    ]

    Method(("m",)).register()
    Method(("m",)).write(cfs)

    a_data = {
        ("a", "1"): {
            "exchanges": [
                {
                    "amount": 1,
                    "type": "production",
                    "input": ("a", "1"),
                },
                {
                    "amount": 0.1,
                    "type": "technosphere",
                    "input": ("a", "3"),
                },
                {
                    "amount": 7,
                    "type": "biosphere",
                    "input": ("bio", "beta"),
                },
            ],
        },
        ("a", "2"): {
            "exchanges": [
                {
                    "amount": 0.5,
                    "type": "production",
                    "input": ("a", "2"),
                },
                {
                    "amount": -2,
                    "type": "technosphere",
                    "input": ("a", "1"),
                },
                {
                    "amount": 1,
                    "type": "biosphere",
                    "input": ("bio", "alpha"),
                },
            ],
        },
        ("a", "3"): {
            "exchanges": [
                {
                    "amount": 1,
                    "type": "production",
                    "input": ("a", "3"),
                },
                {
                    "amount": 3,
                    "type": "technosphere",
                    "input": ("a", "1"),
                },
                {
                    "amount": 2,
                    "type": "technosphere",
                    "input": ("a", "2"),
                },
                {
                    "amount": 2,
                    "type": "biosphere",
                    "input": ("bio", "alpha"),
                },
                {
                    "amount": 5,
                    "type": "biosphere",
                    "input": ("bio", "beta"),
                },
            ],
        },
    }
    Database("a").write(a_data)

    b_data = {
        ("b", "1"): {
            "exchanges": [
                {
                    "amount": 1,
                    "type": "production",
                    "input": ("b", "1"),
                },
                {
                    "amount": 0.1,
                    "type": "technosphere",
                    "input": ("b", "2"),
                },
                {
                    "amount": 0.25,
                    "type": "technosphere",
                    "input": ("a", "3"),
                },
                {
                    "amount": 7,
                    "type": "biosphere",
                    "input": ("bio", "beta"),
                },
            ],
        },
        ("b", "2"): {
            "exchanges": [
                {
                    "amount": 0.5,
                    "type": "production",
                    "input": ("b", "2"),
                },
                {
                    "amount": -2,
                    "type": "technosphere",
                    "input": ("a", "1"),
                },
                {
                    "amount": 5,
                    "type": "biosphere",
                    "input": ("bio", "beta"),
                },
            ],
        },
    }
    Database("b").write(b_data)

    c_data = {
        ("c", "1"): {
            "exchanges": [
                {
                    "amount": 1,
                    "type": "production",
                    "input": ("c", "1"),
                },
                {
                    "amount": 0.1,
                    "type": "technosphere",
                    "input": ("a", "3"),
                },
                {
                    "amount": 0.2,
                    "type": "technosphere",
                    "input": ("b", "2"),
                },
                {
                    "amount": 0.3,
                    "type": "technosphere",
                    "input": ("c", "2"),
                },
                {
                    "amount": 1,
                    "type": "biosphere",
                    "input": ("bio", "beta"),
                },
            ],
        },
        ("c", "2"): {
            "exchanges": [
                {
                    "amount": 0.5,
                    "type": "production",
                    "input": ("c", "2"),
                },
                {
                    "amount": -0.2,
                    "type": "technosphere",
                    "input": ("b", "1"),
                },
                {
                    "amount": 2,
                    "type": "biosphere",
                    "input": ("bio", "alpha"),
                },
            ],
        },
    }
    Database("c").write(c_data)
