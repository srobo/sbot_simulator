from __future__ import annotations

import sys
from typing import IO, Callable
from pathlib import Path


class Tee(IO[str]):
    """
    Forwards calls from its `write` and `flush` methods to each of the given targets.
    """

    def __init__(self, *streams: IO[str]) -> None:
        self.streams = streams

    def write(self, data: str) -> None:
        for stream in self.streams:
            stream.write(data)
        self.flush()

    def flush(self) -> None:
        for stream in self.streams:
            stream.flush()


class InsertPrefix(IO[str]):
    """
    Inserts a prefix into the data written to the stream.
    """

    def __init__(self, stream: IO[str], prefix: Callable[[], str] | str | None) -> None:
        self.stream = stream
        self.prefix = prefix
        self._line_start = True

    def _get_prefix(self) -> str:
        if not self.prefix:
            return ''

        prefix = self.prefix() if isinstance(self.prefix, Callable) else self.prefix
        return prefix

    def write(self, data: str) -> None:
        prefix = self._get_prefix()
        if not prefix:
            self.stream.write(data)
            return

        if self._line_start:
            data = prefix + data

        self._line_start = data.endswith('\n')
        # Append our prefix just after all inner newlines. Don't append to a
        # trailing newline as we don't know if the next line in the log will be
        # from this zone.
        data = data.replace('\n', '\n' + prefix)
        if self._line_start:
            data = data[:-len(prefix)]

        self.stream.write(data)

    def flush(self) -> None:
        self.stream.flush()


def prefix_and_tee_streams(name: Path, prefix: Callable[[], str] | str | None = None) -> None:
    """
    Tee stdout and stderr also to the named log file.

    Note: we intentionally don't provide a way to clean up the stream
    replacement so that any error handling from Python which causes us to exit
    is also captured by the log file.
    """

    log_file = name.open(mode='w')

    sys.stdout = InsertPrefix(
        Tee(
            sys.stdout,
            log_file,
        ),
        prefix=prefix,
    )
    sys.stderr = InsertPrefix(
        Tee(
            sys.stderr,
            log_file,
        ),
        prefix=prefix,
    )
