import unittest
from unittest.mock import patch

import os.path
import logging
import datetime as dt
from tempfile import TemporaryDirectory

from handler import DateRotatingFileHandler


class TestFileCreation(unittest.TestCase):
    def setUp(self):
        self._tmpdir = TemporaryDirectory(dir=".")
        self._tmpdir.__enter__()

        self.file_name = "test"
        self.separator = "."
        self._TEST_START_DT = dt.datetime(2001, 1, 1)

        with patch(
            "handler.DateRotatingFileHandler.now_date", self._TEST_START_DT.date()
        ) as _:
            self.handler = DateRotatingFileHandler(
                os.path.join(self._tmpdir.name, self.file_name),
                separator=self.separator,
            )

        self.handler.setLevel(logging.DEBUG)
        self.logger = logging.getLogger(__name__)

        self.logger.addHandler(self.handler)

    def tearDown(self):
        self.logger.removeHandler(self.handler)
        self.handler.close()
        self._tmpdir.__exit__(None, None, None)

    def test_file_creation(self):

        with self.assertLogs(__name__, level="DEBUG") as logctx:

            isodate = self._TEST_START_DT.date().isoformat()
            log_msg = f"Test date: {isodate}"
            self.logger.info(log_msg)

            self.assertEqual([f"INFO:{__name__}:{log_msg}"], logctx.output)

        expected_log_fname = self.separator.join((isodate, self.file_name, "log"))
        expected_log_fpath = os.path.join(self._tmpdir.name, expected_log_fname)

        self.assertTrue(os.path.exists(expected_log_fpath))
