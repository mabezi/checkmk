#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

import pytest

from tests.testlib import SpecialAgent

pytestmark = pytest.mark.checks


@pytest.mark.parametrize(
    "params,expected_args",
    [
        ({}, ["address"]),
        ({"timeout": 20}, ["--timeout", "20", "address"]),
    ],
)
def test_allnet_ip_sensoric_argument_parsing(  # type:ignore[no-untyped-def]
    params, expected_args
) -> None:
    """Tests if all required arguments are present."""
    agent = SpecialAgent("agent_allnet_ip_sensoric")
    arguments = agent.argument_func(params, "host", "address")
    assert arguments == expected_args
