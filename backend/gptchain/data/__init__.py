import os
from typing import Optional

from gptchain.client.cloud import gptchainCloudClient
from gptchain.config import config

gptchain_client = None  # type: Optional[gptchainCloudClient]

if config.data_persistence:
    gptchain_client = gptchainCloudClient(
        api_key=os.environ.get("gptchain_API_KEY", ""),
        gptchain_server=config.gptchain_server,
    )
