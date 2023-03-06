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


BTRFS_FILESYSTEM_USAGE = """
Overall:
    Device size:		    22000898670592
    Device allocated:		     3633559109632
    Device unallocated:		    18367339560960
    Device missing:		                 0
    Device slack:		                 0
    Used:			     3612965650432
    Free (estimated):		     9192925765632	(min: 9192925765632)
    Free (statfs, df):		     8193271078912
    Data ratio:			              2.00
    Metadata ratio:		              2.00
    Global reserve:		         536870912	(used: 0)
    Multiple profiles:		                no

Data,RAID1: Size:1813549940736, Used:1804293955584 (99.49%)
   /dev/sdb1	1813549940736
   /dev/sdc1	1813549940736

Metadata,RAID1: Size:3221225472, Used:2188607488 (67.94%)
   /dev/sdb1	3221225472
   /dev/sdc1	3221225472

System,RAID1: Size:8388608, Used:262144 (3.12%)
   /dev/sdb1	   8388608
   /dev/sdc1	   8388608

Unallocated:
   /dev/sdb1	8184016142336
   /dev/sdc1	10183323418624
"""