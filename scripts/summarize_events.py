#!/usr/bin/env python3
"""Validate annotated tennis returns and recompute result summaries. Python stdlib only."""
import argparse
from collections import Counter
import json
import math
from pathlib import Path

STROKES = ('正手', '反手', '类型不明')
RESULTS = ('R', 'N', 'E', 'U')


def summarize(document):
    if not isinstance(document, dict):
        raise ValueError('输入必须是含 scope 与 events 的 JSON 对象')
    scope = document.get('scope')
    if not isinstance(scope, str) or not scope.strip():
        raise ValueError('scope 必须说明统计范围，不能留空')
    events = document.get('events')
    if not isinstance(events, list):
        raise ValueError('events 必须是数组')
    seen = set()
    for index, event in enumerate(events):
        prefix = f'events[{index}]'
        if not isinstance(event, dict):
            raise ValueError(f'{prefix} 必须是对象')
        eid = event.get('id')
        if not isinstance(eid, str) or not eid.strip() or eid in seen:
            raise ValueError(f'{prefix} 的 id 缺失、非字符串或重复')
        seen.add(eid)
        source = event.get('source')
        if type(source) not in (str, int) or not str(source).strip():
            raise ValueError(f'{prefix} 的 source 必须是非空字符串或整数')
        stamp = event.get('source_t')
        if type(stamp) not in (float, int) or not math.isfinite(stamp) or stamp < 0:
            raise ValueError(f'{prefix} 的 source_t 必须是有限非负秒数')
        if event.get('stroke') not in STROKES or event.get('result') not in RESULTS:
            raise ValueError(f'{prefix} 含无效 stroke 或 result，不能静默跳过')
        evidence = event.get('result_evidence')
        if not isinstance(evidence, str) or not evidence.strip():
            raise ValueError(f'{prefix} 缺少结果依据／未知原因')
    summary = {}
    for stroke in (*STROKES, '全部'):
        rows = [row for row in events if stroke == '全部' or row['stroke'] == stroke]
        counts = Counter(row['result'] for row in rows)
        total = len(rows)
        known = total - counts['U']
        summary[stroke] = {
            'count': total,
            'results': {key: counts[key] for key in RESULTS},
            'known_result_count': known,
            'estimated_success_rate_known': round(100 * counts['R'] / known, 1) if known else None,
            'outcome_coverage_pct': round(100 * known / total, 1) if total else None,
            'all_shots_success_bounds_pct': [
                round(100 * counts['R'] / total, 1),
                round(100 * (counts['R'] + counts['U']) / total, 1),
            ] if total else None,
        }
    # Canonical string IDs match JSON object keys; 1 and "1" mean the same source.
    source_ids = sorted({str(event['source']) for event in events})
    source_counts = {
        source: {stroke: sum(str(e['source']) == source and e['stroke'] == stroke for e in events)
                 for stroke in STROKES}
        for source in source_ids
    }
    return {'scope': scope, 'event_count': len(events), 'source_counts': source_counts, 'summary': summary}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--output', type=Path, help='Optional new output path. Existing files are not overwritten.')
    args = parser.parse_args()
    try:
        result = summarize(json.loads(args.input.read_text(encoding='utf-8')))
        rendered = json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + '\n'
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            with args.output.open('x', encoding='utf-8') as handle:
                handle.write(rendered)
        else:
            print(rendered, end='')
    except (ValueError, OSError) as error:
        parser.exit(2, f'错误：{error}\n')


if __name__ == '__main__':
    main()
