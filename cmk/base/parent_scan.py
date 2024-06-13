#!/usr/bin/env python3
# Copyright (C) 2024 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
import os
import socket
import subprocess
import sys
from collections.abc import Iterable, Sequence

import cmk.utils.debug
import cmk.utils.paths
import cmk.utils.tty as tty
from cmk.utils.caching import cache_manager, DictCache
from cmk.utils.exceptions import MKGeneralException
from cmk.utils.hostaddress import HostAddress, HostName, Hosts
from cmk.utils.log import console

from cmk.automations.results import Gateway, GatewayResult

import cmk.base.config as config
import cmk.base.obsolete_output as out
from cmk.base.config import ConfigCache


def traceroute_available() -> str | None:
    for path in os.environ["PATH"].split(os.pathsep):
        f = path + "/traceroute"
        if os.path.exists(f) and os.access(f, os.X_OK):
            return f
    return None


def scan_parents_of(
    config_cache: ConfigCache,
    hosts_config: Hosts,
    monitoring_host: HostName | None,
    hosts: Iterable[HostName],
    silent: bool = False,
    settings: dict[str, int] | None = None,
) -> Sequence[GatewayResult]:
    # pylint: disable=too-many-branches
    if settings is None:
        settings = {}

    if monitoring_host:
        nagios_ip = config.lookup_ip_address(config_cache, monitoring_host, family=socket.AF_INET)
    else:
        nagios_ip = None

    os.putenv("LANG", "")
    os.putenv("LC_ALL", "")

    # Start processes in parallel
    procs: list[tuple[HostName, HostAddress | None, str | subprocess.Popen]] = []
    for host in hosts:
        console.verbose("%s " % host)
        try:
            ip = config.lookup_ip_address(config_cache, host, family=socket.AF_INET)
            if ip is None:
                raise RuntimeError()
            command = [
                "traceroute",
                "-w",
                "%d" % settings.get("timeout", 8),
                "-q",
                "%d" % settings.get("probes", 2),
                "-m",
                "%d" % settings.get("max_ttl", 10),
                "-n",
                ip,
            ]
            console.vverbose("Running '%s'\n" % subprocess.list2cmdline(command))

            procs.append(
                (
                    host,
                    ip,
                    subprocess.Popen(  # pylint: disable=consider-using-with
                        command,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        close_fds=True,
                        encoding="utf-8",
                    ),
                )
            )
        except Exception as e:
            if cmk.utils.debug.enabled():
                raise
            procs.append((host, None, "ERROR: %s" % e))

    # Output marks with status of each single scan
    def dot(color: str, dot: str = "o") -> None:
        if not silent:
            out.output(tty.bold + color + dot + tty.normal)

    # Now all run and we begin to read the answers. For each host
    # we add a triple to gateways: the gateway, a scan state  and a diagnostic output
    gateways: list[GatewayResult] = []
    for host, ip, proc_or_error in procs:
        if isinstance(proc_or_error, str):
            lines = [proc_or_error]
            exitstatus = 1
        else:
            exitstatus = proc_or_error.wait()
            if proc_or_error.stdout is None:
                raise RuntimeError()
            lines = [l.strip() for l in proc_or_error.stdout.readlines()]

        if exitstatus:
            dot(tty.red, "*")
            gateways.append(
                GatewayResult(
                    None, "failed", 0, "Traceroute failed with exit code %d" % (exitstatus & 255)
                )
            )
            continue

        if len(lines) == 1 and lines[0].startswith("ERROR:"):
            message = lines[0][6:].strip()
            console.verbose("%s: %s\n", host, message, stream=sys.stderr)
            dot(tty.red, "D")
            gateways.append(GatewayResult(None, "dnserror", 0, message))
            continue

        if len(lines) == 0:
            if cmk.utils.debug.enabled():
                raise MKGeneralException(
                    "Cannot execute %s. Is traceroute installed? Are you root?" % command
                )
            dot(tty.red, "!")
            continue

        if len(lines) < 2:
            if not silent:
                console.error("{}: {}\n".format(host, " ".join(lines)))
            gateways.append(
                GatewayResult(
                    None,
                    "garbled",
                    0,
                    "The output of traceroute seem truncated:\n%s" % ("".join(lines)),
                )
            )
            dot(tty.blue)
            continue

        # Parse output of traceroute:
        # traceroute to 8.8.8.8 (8.8.8.8), 30 hops max, 40 byte packets
        #  1  * * *
        #  2  10.0.0.254  0.417 ms  0.459 ms  0.670 ms
        #  3  172.16.0.254  0.967 ms  1.031 ms  1.544 ms
        #  4  217.0.116.201  23.118 ms  25.153 ms  26.959 ms
        #  5  217.0.76.134  32.103 ms  32.491 ms  32.337 ms
        #  6  217.239.41.106  32.856 ms  35.279 ms  36.170 ms
        #  7  74.125.50.149  45.068 ms  44.991 ms *
        #  8  * 66.249.94.86  41.052 ms 66.249.94.88  40.795 ms
        #  9  209.85.248.59  43.739 ms  41.106 ms 216.239.46.240  43.208 ms
        # 10  216.239.48.53  45.608 ms  47.121 ms 64.233.174.29  43.126 ms
        # 11  209.85.255.245  49.265 ms  40.470 ms  39.870 ms
        # 12  8.8.8.8  28.339 ms  28.566 ms  28.791 ms
        routes: list[HostAddress | None] = []
        for line in lines[1:]:
            parts = line.split()
            route = parts[1]
            if route.count(".") == 3:
                routes.append(HostAddress(route))
            elif route == "*":
                routes.append(None)  # No answer from this router
            else:
                if not silent:
                    console.error(f"{host}: invalid output line from traceroute: '{line}'\n")

        if len(routes) == 0:
            error = "incomplete output from traceroute. No routes found."
            console.error(f"{host}: {error}\n")
            gateways.append(GatewayResult(None, "garbled", 0, error))
            dot(tty.red)
            continue

        # Only one entry -> host is directly reachable and gets nagios as parent -
        # if nagios is not the parent itself. Problem here: How can we determine
        # if the host in question is the monitoring host? The user must configure
        # this in monitoring_host.
        if len(routes) == 1:
            if ip == nagios_ip:
                gateways.append(
                    GatewayResult(None, "root", 0, "")
                )  # We are the root-monitoring host
                dot(tty.white, "N")
            elif monitoring_host and nagios_ip:
                gateways.append(
                    GatewayResult(Gateway(monitoring_host, nagios_ip, None), "direct", 0, "")
                )
                dot(tty.cyan, "L")
            else:
                gateways.append(GatewayResult(None, "direct", 0, ""))
            continue

        # Try far most route which is not identical with host itself
        ping_probes = settings.get("ping_probes", 5)
        skipped_gateways = 0
        this_route: HostAddress | None = None
        for r in routes[::-1]:
            if not r or (r == ip):
                continue
            # Do (optional) PING check in order to determine if that
            # gateway can be monitored via the standard host check
            if ping_probes:
                if not gateway_reachable_via_ping(r, ping_probes):
                    console.verbose("(not using %s, not reachable)\n", r, stream=sys.stderr)
                    skipped_gateways += 1
                    continue
            this_route = r
            break
        if not this_route:
            error = "No usable routing information"
            if not silent:
                console.error(f"{host}: {error}\n")
            gateways.append(GatewayResult(None, "notfound", 0, error))
            dot(tty.blue)
            continue

        # TTLs already have been filtered out)
        gateway_ip = this_route
        gateway = _ip_to_hostname(config_cache, hosts_config, this_route)
        if gateway:
            console.verbose("%s(%s) ", gateway, gateway_ip)
        else:
            console.verbose("%s ", gateway_ip)

        # Try to find DNS name of host via reverse DNS lookup
        dns_name = _ip_to_dnsname(gateway_ip)
        gateways.append(
            GatewayResult(Gateway(gateway, gateway_ip, dns_name), "gateway", skipped_gateways, "")
        )
        dot(tty.green, "G")
    return gateways


def gateway_reachable_via_ping(ip: HostAddress, probes: int) -> bool:
    return (
        subprocess.call(
            ["ping", "-q", "-i", "0.2", "-l", "3", "-c", "%d" % probes, "-W", "5", ip],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
            close_fds=True,
        )
        == 0
    )


def _ip_to_hostname(
    config_cache: ConfigCache, hosts_config: Hosts, ip: HostAddress | None
) -> HostName | None:
    """Find hostname belonging to an ip address."""
    absent = "ip_to_hostname" not in cache_manager
    cache = cache_manager.obtain_cache("ip_to_hostname")
    if absent:
        _fill_ip_to_hostname_cache(cache, config_cache, hosts_config)

    return cache.get(ip)


def _fill_ip_to_hostname_cache(
    cache: DictCache, config_cache: ConfigCache, hosts_config: Hosts
) -> None:
    """We must not use reverse DNS but the Checkmk mechanisms, since we do not
    want to find the DNS name but the name of a matching host from all_hosts"""
    for host in {
        # inconsistent with do_scan_parents where a list of hosts could be passed as an argument
        hn
        for hn in hosts_config.hosts
        if config_cache.is_active(hn) and config_cache.is_online(hn)
    }:
        try:
            cache[config.lookup_ip_address(config_cache, host, family=socket.AF_INET)] = host
        except Exception:
            pass


def _ip_to_dnsname(ip: HostAddress) -> HostName | None:
    try:
        return HostName(socket.gethostbyaddr(ip)[0])
    except Exception:
        return None
