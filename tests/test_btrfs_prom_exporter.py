# Copyright (c) 2022 - 2023 Philip May
# This software is distributed under the terms of the MIT license
# which is available at https://opensource.org/licenses/MIT

from math import isclose

from prometheus_client import REGISTRY

from btrfs_prom_exporter.btrfs_prom_exporter import (
    _STAT_TYPES,
    init_metrics,
    normalize_str,
    scrape_device_stats,
)
from tests.json_fixtures import BTRFS_DEVICE_STATS_RAID_JSON, BTRFS_DEVICE_STATS_SINGLE_JSON


def test_normalize_str__happy_case():
    string = " AB- ./:#*+~xy "
    output = normalize_str(string)
    assert output == "ab_________xy"


def test_normalize_str__non_str_type():
    string = 77
    output = normalize_str(string)
    assert string == output


def test_scrape_device_stats_single():
    init_metrics(30)
    scrape_device_stats(BTRFS_DEVICE_STATS_SINGLE_JSON, None, "/test_path")

    for stat_type in _STAT_TYPES:
        btrfs_device_stat_gauge = REGISTRY.get_sample_value(
            "btrfs_device_stat",
            labels={
                "device": "/dev/sda2",
                "devid": "1",
                "stat_type": stat_type,
                "path": "/test_path",
            },
        )
        assert btrfs_device_stat_gauge is not None
        assert isclose(btrfs_device_stat_gauge, 0.0)


def test_scrape_device_stats_raid():
    init_metrics(30)
    scrape_device_stats(BTRFS_DEVICE_STATS_RAID_JSON, None, "/test_path")

    dev_infos = [
        {"device": "/dev/sdc1", "devid": "1"},
        {"device": "/dev/sdb1", "devid": "2"},
    ]
    for dev_info in dev_infos:
        for stat_type in _STAT_TYPES:
            btrfs_device_stat_gauge = REGISTRY.get_sample_value(
                "btrfs_device_stat",
                labels={
                    "device": dev_info["device"],
                    "devid": dev_info["devid"],
                    "stat_type": stat_type,
                    "path": "/test_path",
                },
            )
            assert btrfs_device_stat_gauge is not None
            assert isclose(btrfs_device_stat_gauge, 0.0)
