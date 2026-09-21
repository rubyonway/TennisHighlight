#!/usr/bin/env python3
"""Small behavioral checks with synthetic data, no private media or network beyond loopback."""
from copy import deepcopy
from functools import partial
from http.server import ThreadingHTTPServer
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from serve_report import ReportHandler
from summarize_events import summarize


def main():
    records = [
        {'id': str(i), 'source': 1, 'source_t': float(i), 'stroke': stroke, 'result': result,
         'result_evidence': 'Synthetic test annotation'}
        for i, (stroke, result) in enumerate([('正手', 'R'), ('正手', 'N'), ('正手', 'U'), ('反手', 'U')])
    ]
    data = {'scope': 'Synthetic selected sample, not full match', 'events': records}
    result = summarize(data)['summary']
    assert result['正手']['estimated_success_rate_known'] == 50.0
    assert result['正手']['all_shots_success_bounds_pct'] == [33.3, 66.7]
    assert result['反手']['estimated_success_rate_known'] is None
    assert result['类型不明']['count'] == 0
    assert summarize({'scope': 'No detected returns', 'events': []})['summary']['全部']['outcome_coverage_pct'] is None
    for field, bad_value in [('source_t', -1), ('source_t', float('nan')), ('result', 'WIN'), ('result_evidence', '')]:
        bad = deepcopy(data)
        bad['events'][0][field] = bad_value
        try:
            summarize(bad)
        except ValueError:
            pass
        else:
            raise AssertionError(f'Accepted invalid {field}')
    bad = deepcopy(data)
    bad['events'].append(deepcopy(bad['events'][0]))
    try:
        summarize(bad)
    except ValueError:
        pass
    else:
        raise AssertionError('Accepted duplicate event ID')
    with TemporaryDirectory() as directory:
        path = Path(directory)
        content = bytes(range(256)) * 10
        (path / 'media.mp4').write_bytes(content)
        server = ThreadingHTTPServer(('127.0.0.1', 0), partial(ReportHandler, directory=directory))
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        url = f'http://127.0.0.1:{server.server_port}/media.mp4'
        try:
            with urlopen(url, timeout=3) as response:
                assert response.status == 200 and response.read() == content
            for header, start, end in [('bytes=10-19', 10, 19), ('bytes=2500-', 2500, 2559), ('bytes=-12', 2548, 2559)]:
                with urlopen(Request(url, headers={'Range': header}), timeout=3) as response:
                    assert response.status == 206
                    assert response.headers['Content-Range'] == f'bytes {start}-{end}/{len(content)}'
                    assert response.read() == content[start:end + 1]
            with urlopen(Request(url, method='HEAD', headers={'Range': 'bytes=5-9'}), timeout=3) as response:
                assert response.status == 206 and response.headers['Content-Length'] == '5' and response.read() == b''
            for header in ['bytes=9000-', 'bytes=-0', 'bytes=4-2', 'bytes=0-1,3-4']:
                try:
                    urlopen(Request(url, headers={'Range': header}), timeout=3)
                except HTTPError as error:
                    assert error.code == 416
                else:
                    raise AssertionError(f'Accepted invalid range {header}')
            with TemporaryDirectory() as other:
                external = Path(other) / 'private.txt'
                external.write_text('synthetic')
                (path / 'external').symlink_to(external)
                try:
                    urlopen(url.replace('media.mp4', 'external'), timeout=3)
                except HTTPError as error:
                    assert error.code == 403
                else:
                    raise AssertionError('Served outside symlink')
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)
    print('PASS: result denominators, nulls, invalid records, full reads, byte ranges, HEAD, and outside symlink')


if __name__ == '__main__':
    main()
