"""Constants for the reGen bridge."""

BRIDGE_CONFIG_FILENAME = "bridgeData.yaml"

VERSION_META_REMOTE_URL = (
    "https://raw.githubusercontent.com/Haidra-Org/horde-worker-reGen/main/horde_worker_regen/_version_meta.json"
)


KNOWN_SLOW_MODELS_DIFFICULTIES = {"Stable Cascade 1.0": 6.0}
VRAM_HEAVY_MODELS = ["Stable Cascade 1.0"]

BASE_LORA_DOWNLOAD_TIMEOUT = 45
EXTRA_LORA_DOWNLOAD_TIMEOUT = 15
MAX_LORAS = 5

TOTAL_LORA_DOWNLOAD_TIMEOUT = BASE_LORA_DOWNLOAD_TIMEOUT + (EXTRA_LORA_DOWNLOAD_TIMEOUT * MAX_LORAS)
