# Copyright (c) 2023 Philip May
# This software is distributed under the terms of the MIT license
# which is available at https://opensource.org/licenses/MIT


"""JSON fixtures."""


BTRFS_DEVICE_STATS_SINGLE_JSON = """
{
  "__header": {
    "version": "1"
  },
  "device-stats": [
    {
      "device": "/dev/sda2",
      "devid": "1",
      "write_io_errs": "0",
      "read_io_errs": "0",
      "flush_io_errs": "0",
      "corruption_errs": "0",
      "generation_errs": "0"
    }
  ]
}
"""

BTRFS_DEVICE_STATS_RAID_JSON = """
{
    "__header": {
      "version": "1"
    },
    "device-stats": [
      {
        "device": "/dev/sdc1",
        "devid": "1",
        "write_io_errs": "0",
        "read_io_errs": "0",
        "flush_io_errs": "0",
        "corruption_errs": "0",
        "generation_errs": "0"
      },
      {
        "device": "/dev/sdb1",
        "devid": "2",
        "write_io_errs": "0",
        "read_io_errs": "0",
        "flush_io_errs": "0",
        "corruption_errs": "0",
        "generation_errs": "0"
      }
    ]
  }
"""
