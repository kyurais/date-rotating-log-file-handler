import io
import os.path
from logging.handlers import BaseRotatingHandler
from datetime import datetime, timedelta, date
from zoneinfo import ZoneInfo


class DateRotatingFileHandler(BaseRotatingHandler):

    @property
    def now_date(self) -> date:
        return datetime.now(self._tz).date()

    def __init__(
        self,
        filename: str,
        tz: ZoneInfo | None = None,
        date_format: str = "ISO",
        as_suffix: bool = False,
        separator: str = ".",
        mode="a",
        encoding=None,
        errors=None,
    ):
        encoding = io.text_encoding(encoding)

        if not filename.endswith(".log"):
            filename += ".log"

        self._baseFileName = filename
        self._tz = tz or ZoneInfo("UTC")

        self.date_format = date_format
        if not isinstance(date_format, str):
            raise TypeError(
                f"date_format must be str, not {type(date_format).__name__}"
            )

        self.as_suffix = as_suffix
        self.separator = separator

        self.rotator = self._rotator
        self.namer = self._namer

        super().__init__(self._namer(filename), mode, encoding, False, errors)

        self.rolloverAt = self.now_date + timedelta(1)

    def _rotator(self, source, dest):
        if os.path.exists(dest):
            os.remove(dest)
        self.baseFilename = dest
        return None

    def _namer(self, dfn: str) -> str:
        rotate_date = self.now_date

        if self.date_format != "ISO":
            datestr = rotate_date.strftime(self.date_format)
        else:
            datestr = rotate_date.isoformat()

        stem, ext = os.path.splitext(os.path.basename(dfn))

        if self.as_suffix:
            new_filename = stem + self.separator + datestr + ext
        else:
            new_filename = datestr + self.separator + stem + ext

        return os.path.join(os.path.dirname(dfn), new_filename)

    def shouldRollover(self, record):
        return self.now_date >= self.rolloverAt

    def doRollover(self):
        if self.stream:
            self.stream.close()
            self.stream = None

        dfn = self.rotation_filename(self._baseFileName)
        self.rotate(self._baseFileName, dfn)
        self.stream = self._open()

        self.rolloverAt += timedelta(1)

        return None
