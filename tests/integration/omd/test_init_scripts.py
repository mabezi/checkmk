#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from tests.testlib.site import Site


def test_init_scripts(site: Site) -> None:
    scripts = {
        "agent-receiver",
        "apache",
        "background-jobs",
        "core",
        "crontab",
        "jaeger",
        "mkeventd",
        "nagios",
        "npcd",
        "piggyback-hub",
        "pnp_gearman_worker",
        "redis",
        "rrdcached",
        "stunnel",
        "xinetd",
    }

    if not site.version.is_raw_edition():
        scripts |= {
            "cmc",
            "dcd",
            "liveproxyd",
            "mknotifyd",
        }

    installed_scripts = set(site.listdir("etc/init.d"))

    assert scripts == installed_scripts
