#!/usr/bin/env python3
"""Serve a local report folder on loopback with single HTTP byte-range support."""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import re


def byte_range(value, size):
    match = re.fullmatch(r'bytes=(\d*)-(\d*)', value)
    if not match or not any(match.groups()) or size <= 0:
        raise ValueError('Unsupported or unsatisfiable byte range')
    first, last = match.groups()
    if first:
        start = int(first)
        end = min(int(last), size - 1) if last else size - 1
    else:
        suffix = int(last)
        if suffix <= 0:
            raise ValueError('Empty suffix')
        start, end = max(0, size - suffix), size - 1
    if start > end or start >= size:
        raise ValueError('Unsatisfiable byte range')
    return start, end


class ReportHandler(SimpleHTTPRequestHandler):
    def send_head(self):
        self.remaining = None
        path = Path(self.translate_path(self.path))
        root = Path(self.directory).resolve()
        # Keep symlinks from exposing files outside the chosen report package.
        if not path.resolve().is_relative_to(root):
            self.send_error(403, 'Path outside report folder')
            return None
        request_range = self.headers.get('Range')
        if not request_range or not path.is_file():
            return super().send_head()
        try:
            handle = path.open('rb')
        except OSError:
            self.send_error(404, 'File not readable')
            return None
        size = path.stat().st_size
        try:
            start, end = byte_range(request_range, size)
        except ValueError:
            handle.close()
            self.send_response(416)
            self.send_header('Content-Range', f'bytes */{size}')
            self.send_header('Content-Length', '0')
            self.end_headers()
            return None
        handle.seek(start)
        self.remaining = end - start + 1
        self.send_response(206)
        self.send_header('Content-Type', self.guess_type(str(path)))
        self.send_header('Content-Length', str(self.remaining))
        self.send_header('Content-Range', f'bytes {start}-{end}/{size}')
        self.send_header('Accept-Ranges', 'bytes')
        self.end_headers()
        return handle

    def copyfile(self, source, outputfile):
        try:
            if self.remaining is None:
                return super().copyfile(source, outputfile)
            while self.remaining:
                chunk = source.read(min(256 * 1024, self.remaining))
                if not chunk:
                    break
                outputfile.write(chunk)
                self.remaining -= len(chunk)
        except (BrokenPipeError, ConnectionResetError):
            pass  # A browser may cancel a read when seeking or switching videos.

    def log_message(self, *_):
        pass


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    parser.add_argument('--port', type=int, default=8921)
    args = parser.parse_args()
    if not args.directory.is_dir():
        parser.error('directory must be an existing report folder')
    if not 1 <= args.port <= 65535:
        parser.error('port must be between 1 and 65535')
    try:
        server = ThreadingHTTPServer(('127.0.0.1', args.port), partial(ReportHandler, directory=str(args.directory.resolve())))
    except OSError as error:
        parser.exit(2, f'Cannot start preview: {error}\n')
    print(f'Preview: http://127.0.0.1:{args.port}/ (Ctrl+C to stop)', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
