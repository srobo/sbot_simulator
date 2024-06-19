"""
Classes and functions for logging robot data to a file.

Includes utilities for prefixing log lines and teeing a stream to multiple
destinations.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import IO, Callable


class Tee(IO[str]):
    """Forwards calls from its `write` and `flush` methods to each of the given targets."""

    def __init__(self, *streams: IO[str]) -> None:
        self.streams = streams

    def write(self, data: str) -> None:  # type: ignore[override]
        """
        Writes the given data to all streams in the logger.

        :param data: The data to be written to the stream.
        """
        for stream in self.streams:
            stream.write(data)
        self.flush()

    def flush(self) -> None:
        """Flushes all the streams in the logger."""
        for stream in self.streams:
            stream.flush()


class InsertPrefix(IO[str]):
    """Inserts a prefix into the data written to the stream."""

    def __init__(self, stream: IO[str], prefix: Callable[[], str] | str | None) -> None:
        self.stream = stream
        self.prefix = prefix
        self._line_start = True

    def _get_prefix(self) -> str:
        if not self.prefix:
            return ''

        prefix = self.prefix() if callable(self.prefix) else self.prefix
        return prefix

    def write(self, data: str) -> None:  # type: ignore[override]
        """
        Writes the given data to the stream, applying a prefix to each line if necessary.

        :param data: The data to be written to the stream.
        """
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
        """
        Flushes the stream.

        This method flushes the stream to ensure that all buffered data is written
        to the underlying file or device.
        """
        self.stream.flush()
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
