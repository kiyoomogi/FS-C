import logging
import traceback

__all__ = [
    "logged",
]


class logged:
    def __init__(self, func):
        """
        Decorator for coupling functions.

        Catch and log execution errors in FLAC3D.

        """
        self.func = func

    def __call__(self, *args, **kwargs):
        """Return 0 if function is called without error, 1 otherwise."""
        logging.basicConfig(
            filename="toughflac.log",
            level=logging.DEBUG,
            format="%(asctime)s: %(levelname)s - %(message)s",
        )
        try:
            self.func(*args, **kwargs)
            return 0
        except KeyboardInterrupt:
            message = "Simulation has been interrupted by the user\nKeyboardInterrupt\n"
            logging.error(message)
            return 1
        except Exception:
            logging.error(traceback.format_exc())
            return 1
