import os

os.environ["HORDE_SDK_DISABLE_CUSTOM_SINKS"] = "1"

from load_env_vars import load_env_vars

load_env_vars()
import argparse
import contextlib
import multiprocessing
import time
from multiprocessing.context import BaseContext

from loguru import logger


def main(ctx: BaseContext) -> None:
    from horde_model_reference.model_reference_manager import ModelReferenceManager
    from pydantic import ValidationError

    from horde_worker_regen.bridge_data.load_config import BridgeDataLoader, reGenBridgeData
    from horde_worker_regen.consts import BRIDGE_CONFIG_FILENAME
    from horde_worker_regen.process_management.main_entry_point import start_working

    def ensure_model_db_downloaded() -> ModelReferenceManager:
        horde_model_reference_manager = ModelReferenceManager(
            download_and_convert_legacy_dbs=False,
            override_existing=True,
        )

        while True:
            try:
                if not horde_model_reference_manager.download_and_convert_all_legacy_dbs(override_existing=True):
                    logger.error("Failed to download and convert legacy DBs. Retrying in 5 seconds...")
                    time.sleep(5)
                else:
                    return horde_model_reference_manager
            except Exception as e:
                logger.error(f"Failed to download and convert legacy DBs: ({type(e).__name__}) {e}")
                logger.error("Retrying in 5 seconds...")
                time.sleep(5)

    horde_model_reference_manager = ensure_model_db_downloaded()

    bridge_data: reGenBridgeData
    try:
        bridge_data = BridgeDataLoader.load(
            file_path=BRIDGE_CONFIG_FILENAME,
            horde_model_reference_manager=horde_model_reference_manager,
        )
    except Exception as e:
        logger.exception(e)

        if "No such file or directory" in str(e):
            logger.error(f"Could not find {BRIDGE_CONFIG_FILENAME}. Please create it and try again.")

        if isinstance(e, ValidationError):
            # Print a list of fields that failed validation
            logger.error(f"The following fields in {BRIDGE_CONFIG_FILENAME} failed validation:")
            for error in e.errors():
                logger.error(f"{error['loc'][0]}: {error['msg']}")

        input("Press any key to exit...")
        return

    bridge_data.load_env_vars()

    start_working(
        ctx=ctx,
        bridge_data=bridge_data,
        horde_model_reference_manager=horde_model_reference_manager,
    )


if __name__ == "__main__":
    with contextlib.suppress(Exception):
        multiprocessing.set_start_method("spawn", force=True)

    print(f"Multiprocessing start method: {multiprocessing.get_start_method()}")

    # Create args for -v, allowing -vvv
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", action="count", default=0, help="Increase verbosity of output")

    args = parser.parse_args()

    logger.remove()
    from hordelib.utils.logger import HordeLog

    if args.v == 2:

        def _verbosity_hack(*args, **kwargs) -> None:  # noqa
            return

        HordeLog.verbosity = 25
        HordeLog.set_logger_verbosity = _verbosity_hack  # type: ignore

    # Initialise logging with loguru
    HordeLog.initialise(
        setup_logging=True,
        process_id=None,
        verbosity_count=args.v if args.v != 0 else 3,  # FIXME
    )

    # We only need to download the legacy DBs once, so we do it here instead of in the worker processes

    main(multiprocessing.get_context("spawn"))
