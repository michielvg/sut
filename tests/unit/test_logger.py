import json
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from sut.logger import NDJSONLogger

# -------------------------
# Helpers
# -------------------------
def read_ndjson(path):
    with open(path) as f:
        return [json.loads(line) for line in f]


# -------------------------
# Tests
# -------------------------
def test_logger_initialization_with_config(tmp_path):
    cfg = {
        "source": "SRC1",
        "device": "DEV1",
        "intent": "TEST",
        "buffer_size": 2,
        "fsync": True
    }

    logger = NDJSONLogger(config=cfg, base_path=str(tmp_path))
    
    assert logger.src == "SRC1"
    assert logger.dev == "DEV1"
    assert logger.intent == "TEST"
    assert logger.buffer_size == 2
    assert logger.fsync is True


@patch("sut.logger.NDJSONLogger._print_dev_menu")
def test_logger_initialization_without_device(mock_menu, tmp_path):
    logger = NDJSONLogger(src="SRC2", intent="TEST2", base_path=str(tmp_path))
    mock_menu.assert_called_once()


def test_logger_buffering_and_flush(tmp_path):
    logger = NDJSONLogger(src="SRC", dev="DEV", intent="TEST", buffer_size=2, base_path=str(tmp_path))

    logger.log("TX1", "RX1")
    # buffer should not flush yet
    assert len(logger.buffer) == 1

    logger.log("TX2", "RX2")
    # buffer should flush automatically (buffer_size=2)
    path, _ = logger._get_file_path()
    path = Path(path)
    assert path.exists()
    
    # buffer should be cleared after flush
    assert len(logger.buffer) == 0

    records = read_ndjson(path)
    assert records[0]["tx"] == "TX1"
    assert records[1]["rx"] == "RX2"
    assert records[0]["src"] == "SRC"


def test_logger_flush_with_notes(tmp_path):
    logger = NDJSONLogger(src="SRC", dev="DEV", intent="TEST", buffer_size=10, base_path=str(tmp_path))

    logger.log("TX", "RX", notes="Important note")
    # flush manually
    logger.flush()
    path, _ = logger._get_file_path()
    path = Path(path)
    assert path.exists()
    
    records = read_ndjson(path)
    assert records[0]["notes"] == "Important note"


def test_logger_flush_empty_buffer(tmp_path):
    logger = NDJSONLogger(src="SRC", dev="DEV", intent="TEST", buffer_size=2, base_path=str(tmp_path))

    # flush on empty buffer should not fail
    logger.flush()
    # nothing created
    path, _ = logger._get_file_path()
    path = Path(path)
    assert not path.exists()


def test_logger_close_flushes(tmp_path):
    logger = NDJSONLogger(src="SRC", dev="DEV", intent="TEST", buffer_size=10, base_path=str(tmp_path))

    logger.log("TX", "RX")
    # buffer not empty yet
    assert len(logger.buffer) == 1

    logger.close()
    # buffer should now be empty
    assert len(logger.buffer) == 0

    path, _ = logger._get_file_path()
    path = Path(path)
    assert path.exists()


def test_logger_directory_created(tmp_path):
    logger = NDJSONLogger(src="SRC", dev="DEV", intent="TEST", buffer_size=1, base_path=str(tmp_path))

    # simulate flush to create file and directories
    logger.log("TX", "RX")
    path, _ = logger._get_file_path()
    path = Path(path)
    
    # The parent directory should exist
    assert path.parent.exists()
    assert path.exists()


def test_logger_date_rollover_creates_new_file(tmp_path):
    logger = NDJSONLogger(src="SRC", dev="DEV", intent="TEST", buffer_size=1, base_path=str(tmp_path))
    
    # patch _get_file_path to simulate a date change
    with patch.object(logger, "_get_file_path") as mock_get_file:
        mock_get_file.side_effect = [
            (str(tmp_path / "01.ndjson"), "2026-04-01"),
            (str(tmp_path / "02.ndjson"), "2026-04-02"),
        ]

        logger.log("TX1", "RX1")  # triggers flush
        logger.log("TX2", "RX2")  # triggers flush to new file

        path1 = tmp_path / "01.ndjson"
        path2 = tmp_path / "02.ndjson"
        assert path1.exists()
        assert path2.exists()

        records1 = read_ndjson(path1)
        records2 = read_ndjson(path2)
        assert records1[0]["tx"] == "TX1"
        assert records2[0]["tx"] == "TX2"