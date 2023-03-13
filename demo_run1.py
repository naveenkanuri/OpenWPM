from pathlib import Path
import os
import subprocess, argparse

from custom_command import LinkCountingCommand
from openwpm.command_sequence import CommandSequence
from openwpm.commands.browser_commands import GetCommand, BrowseCommand
from openwpm.config import BrowserParams, ManagerParams
from openwpm.storage.sql_provider import SQLiteStorageProvider
from openwpm.task_manager import TaskManager
from cookie_command import CookieAnalyzerCommand
from openwpm.storage.cloud_storage.gcp_storage import (
    GcsStructuredProvider,
    GcsUnstructuredProvider,
)


# The list of sites that we wish to crawl
NUM_BROWSERS = 1
# sites = [
#     "http://google.com",
#     "http://youtube.com",
#     "http://baidu.com",
#     "http://bilibili.com",
#     "http://facebook.com",
#     "http://qq.com",
#     "http://twitter.com",
#     "http://zhihu.com",
#     "http://wikipedia.org",
#     "http://amazon.com"
# ]

sites = {'1': 'http://google.com', '2': 'http://youtube.com', '3': 'http://baidu.com', '4': 'http://bilibili.com', '5': 'http://facebook.com', '6': 'http://qq.com', '7': 'http://twitter.com', '8': 'http://zhihu.com', '9': 'http://wikipedia.org', '10': 'http://amazon.com'}


# Loads the default ManagerParams
# and NUM_BROWSERS copies of the default BrowserParams

manager_params = ManagerParams(num_browsers=NUM_BROWSERS)
browser_params = [BrowserParams(display_mode="native") for _ in range(NUM_BROWSERS)]

# Update browser configuration (use this for per-browser settings)
for browser_param in browser_params:
    # Record HTTP Requests and Responses
    browser_param.http_instrument = True
    # Record cookie changes
    browser_param.cookie_instrument = True
    # Record Navigations
    browser_param.navigation_instrument = True
    # Record JS Web API calls
    browser_param.js_instrument = True
    # Record the callstack of all WebRequests made
    browser_param.callstack_instrument = True
    # Record DNS resolution
    browser_param.dns_instrument = True
    browser_param.bot_mitigation = True

# Update TaskManager configuration (use this for crawl-wide settings)
manager_params.data_directory = Path("./datadir/")
manager_params.log_path = Path("./datadir/openwpm.log")

# memory_watchdog and process_watchdog are useful for large scale cloud crawls.
# Please refer to docs/Configuration.md#platform-configuration-options for more information
# manager_params.memory_watchdog = True
# manager_params.process_watchdog = True

REDIS_HOST = os.getenv("REDIS_HOST", "10.214.147.123")
REDIS_QUEUE_NAME = os.getenv("REDIS_QUEUE_NAME", "crawl-queue")
MAX_JOB_RETRIES = int(os.getenv("MAX_JOB_RETRIES", "2"))
DWELL_TIME = int(os.getenv("DWELL_TIME", "10"))
TIMEOUT = int(os.getenv("TIMEOUT", "60"))

# Storage Provider Params
CRAWL_DIRECTORY = os.getenv("CRAWL_DIRECTORY", "crawl-data-local")
GCS_BUCKET = os.getenv("GCS_BUCKET", "openwpm_bucket")
GCP_PROJECT = os.getenv("GCP_PROJECT", "level-gizmo-376804")
AUTH_TOKEN = os.getenv("GCP_AUTH_TOKEN", "./level-gizmo-376804-87d4e9c8fb8d.json")
BROWSE_OR_GET = os.getenv("BROWSE_OR_GET", "BROWSE")
NUM_LINKS = int(os.getenv("NUM_LINKS", "0"))

print('REDIS_HOST = ' + REDIS_HOST)

print('GCS_BUCKET = ' + GCS_BUCKET + '\nGCP_PROJECT = ' + GCP_PROJECT + '\nAUTH_TOKEN = ' + AUTH_TOKEN + '\n')

structured = GcsStructuredProvider(
    project=GCP_PROJECT,
    bucket_name=GCS_BUCKET,
    base_path=CRAWL_DIRECTORY,
    token=AUTH_TOKEN,
)
unstructured = GcsUnstructuredProvider(
    project=GCP_PROJECT,
    bucket_name=GCS_BUCKET,
    base_path=CRAWL_DIRECTORY + "/data",
    token=AUTH_TOKEN,
)

# Commands time out by default after 60 seconds
with TaskManager(
    manager_params,
    browser_params,
    structured,
    unstructured,
    {},
) as manager:
    # Visits the sites
    for index, site in sites.items():

        def callback(success: bool, val: str = site) -> None:
            print(
                f"CommandSequence for {val} ran {'successfully' if success else 'unsuccessfully'}"
            )

        # Parallelize sites over all number of browsers set above.
        command_sequence = CommandSequence(
            site,
            site_rank=int(index),
            callback=callback,
            blocking=True,
            reset=True,
            retry_number=2
        )

        # Start by visiting the page
        # command_sequence.browse()
        command_sequence.append_command(BrowseCommand(url=site, num_links=0, sleep=0), timeout=60)
        # Have a look at custom_command.py to see how to implement your own command
        # command_sequence.append_command(LinkCountingCommand())
        # command_sequence.append_command(CookieAnalyzerCommand())

        # Run commands across all browsers (simple parallelization)
        manager.execute_command_sequence(command_sequence)
