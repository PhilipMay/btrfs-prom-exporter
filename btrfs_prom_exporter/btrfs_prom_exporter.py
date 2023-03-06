# Copyright (c) 2023 Philip May
# This software is distributed under the terms of the MIT license
# which is available at https://opensource.org/licenses/MIT

"""btrfs_prom_exporter main module."""

import json
import os
import re
import sys
import time
from subprocess import PIPE, Popen
from typing import Dict, List, Set, Tuple

from prometheus_client import Counter, start_http_server

from btrfs_prom_exporter.metric_wrapper import GaugeWrapper


_STAT_TYPES = (
    "write_io_errs",
    "read_io_errs",
    "flush_io_errs",
    "corruption_errs",
    "generation_errs",
)

# Counter how often the SMART values were scraped.
_SCRAPE_ITERATIONS_COUNTER: Counter = Counter(
    "smart_prom_scrape_iterations_total", "Total number of SMART scrape iterations."
)

_FILESYSTEM_USED_RE = re.compile(r"^[ \t]+Used:[ \t]+(\d+)", re.MULTILINE)
_FILESYSTEM_FREE_RE = re.compile(r"^[ \t]+Free \(estimated\):[ \t]+(\d+)", re.MULTILINE)

first_scrape_interval: bool = True
init_metrics_done: bool = False


# TODO: remove if not needed
def normalize_str(the_str: str) -> str:
    """Normalize a string.

    If anything other than a ``str`` is passed, then the same value is returned unchanged.
    This is useful to prepare and clean Prometheus labels.
    """
    result = the_str
    if isinstance(the_str, str):
        result = the_str.strip().lower()
        replace_cars = ["-", " ", ".", "/", ":", "#", "*", "+", "~"]
        for replace_car in replace_cars:
            result = result.replace(replace_car, "_")
    return result


def call_btrfs(options: List[str]) -> Tuple[str, int]:
    """Execute a child program in a new process."""
    args = ["btrfs"]
    args.extend(options)
    if first_scrape_interval:
        print(f"DEBUG: Output of the first scraping iteration: call: {args}")
    try:
        with Popen(args, stdout=PIPE, stderr=PIPE) as popen:
            stdout, stderr = popen.communicate()

            returncode = popen.returncode
            result = None
            if stdout is not None:
                result = stdout.decode("utf-8")

            if returncode != 0:
                stderr_text = (
                    stderr.decode("utf-8")
                    if (stderr is not None and stderr.decode("utf-8") != "")
                    else "not set"
                )
                print(
                    f"WARNING: Calling {args} returned non zero returncode! "
                    f"returncode: {popen.returncode} stderr: '{stderr_text}'"
                )

            if isinstance(result, str) and len(result) > 0:  # we have a result
                if first_scrape_interval:
                    print(f"DEBUG: Output of the first scraping iteration: result: {result}")
                return result, returncode
            else:
                raise RuntimeError(
                    f"Calling {args} returned no result! "
                    f"returncode: {popen.returncode} stderr: '{stderr_text}'"
                )

    except FileNotFoundError:
        print(
            "ERROR: The btrfs program cannot be found. "
            "Maybe btrfs still needs to be installed.",
            file=sys.stderr,
        )
        raise


def scrape_device_stat(device_stat: Dict[str, str], monitor_path):
    """TODO: add doc."""
    device = device_stat.get("device", "unknown")
    devid = device_stat.get("devid", "unknown")
    for stat_type in _STAT_TYPES:
        stat_type_value = device_stat.get(stat_type, None)
        if isinstance(stat_type_value, str):
            try:
                stat_type_value = float(stat_type_value)
            except ValueError:
                # nothing we can do here
                pass
            if isinstance(stat_type_value, float):
                _BTRFS_DEVICE_STAT_GAUGE.set(  # type: ignore
                    value=stat_type_value,
                    device=device,
                    devid=devid,
                    stat_type=stat_type,
                    path=monitor_path,
                )


def scrape_device_stats(result_json, returncode, monitor_path):
    """TODO: add doc."""
    # TODO: should we do something with the returncode?
    if isinstance(result_json, str) and len(result_json) > 0:  # we have a result
        results = json.loads(result_json)
        device_stats = results.get("device-stats", None)
        if isinstance(device_stats, list):
            for device_stat in device_stats:
                scrape_device_stat(device_stat, monitor_path)
        else:
            # TODO: what do we so here?
            pass
    else:
        print(f"WARNING: No device stats for {monitor_path}")


def scrape_filesystem_usage(result, returncode, monitor_path):
    """TODO: add doc."""
    free_bytes = 0
    free_search = re.search(_FILESYSTEM_FREE_RE, result)
    if free_search is not None:
        try:
            free_bytes = float(free_search.group(1))
        except ValueError:
            # nothing we can do here
            pass
    _BTRFS_FILESYSTEM_USAGE_GAUGE.set(value=free_bytes, stat_type="free_estimated", path=monitor_path)

    used_bytes = 0
    used_search = re.search(_FILESYSTEM_USED_RE, result)
    if used_search is not None:
        try:
            used_bytes = float(used_search.group(1))
        except ValueError:
            # nothing we can do here
            pass
    _BTRFS_FILESYSTEM_USAGE_GAUGE.set(value=used_bytes, stat_type="used", path=monitor_path)


def refresh_metrics(monitor_paths: Set[str]) -> None:
    """Refresh the metrics."""
    for monitor_path in monitor_paths:
        # scrape device status
        device_stats_result_json, returncode = call_btrfs(
            ["--format", "json", "device", "stats", monitor_path]
        )
        scrape_device_stats(device_stats_result_json, returncode, monitor_path)

        # scrape filesystem usage
        filesystem_usage_result, returncode = call_btrfs(
            ["filesystem", "usage", "--raw", monitor_path]
        )
        scrape_filesystem_usage(filesystem_usage_result, returncode, monitor_path)


def init_metrics(btrfs_info_refresh_interval):
    """Init the metrics."""
    global init_metrics_done
    if not init_metrics_done:
        init_metrics_done = True

        global _BTRFS_DEVICE_STAT_GAUGE
        _BTRFS_DEVICE_STAT_GAUGE = GaugeWrapper(
            "btrfs_device_stat",
            "Btrfs device IO error statistics",
            ["device", "devid", "stat_type", "path"],
            btrfs_info_refresh_interval * 4,
        )

        global _BTRFS_FILESYSTEM_USAGE_GAUGE
        _BTRFS_FILESYSTEM_USAGE_GAUGE = GaugeWrapper(
            "btrfs_filesystem_usage_bytes",
            "Btrfs information about internal filesystem usage.",
            ["stat_type", "path"],
            btrfs_info_refresh_interval * 4,
        )


def read_monitor_paths() -> Set[str]:
    """Read all paths to monitor from environment variable."""
    monitor_paths = set()
    for path_id in range(100):
        monitor_path = os.environ.get(f"BTRFS_MONITOR_PATH_{path_id}")
        if monitor_path is not None:
            monitor_paths.add(monitor_path)
    return monitor_paths


def main() -> None:
    """Main function."""
    global first_scrape_interval
    print("INFO: Start btrfs_prom_exporter.")

    prometheus_client_port = int(os.environ.get("PROMETHEUS_METRIC_PORT", 9902))
    print(f"INFO: Start prometheus client. port: {prometheus_client_port}")
    start_http_server(prometheus_client_port)

    btrfs_info_refresh_interval = int(os.environ.get("BTRFS_INFO_READ_INTERVAL_SECONDS", 60))

    monitor_paths: Set[str] = read_monitor_paths()

    init_metrics(btrfs_info_refresh_interval)

    print(
        f"INFO: Enter metrics refresh loop. "
        f"smart_info_refresh_interval: {btrfs_info_refresh_interval}"
    )

    while True:
        refresh_metrics(monitor_paths)
        _SCRAPE_ITERATIONS_COUNTER.inc()
        first_scrape_interval = False
        _BTRFS_DEVICE_STAT_GAUGE.remove_old_metrics()  # type: ignore
        _BTRFS_FILESYSTEM_USAGE_GAUGE.remove_old_metrics()  # type: ignore
        time.sleep(btrfs_info_refresh_interval)


if __name__ == "__main__":
    main()
