import logging
import app.logger_setup  # Just importing triggers the setup

def test_logger_setup_exists():
    logger = logging.getLogger("uvicorn")
    assert logger is not None
