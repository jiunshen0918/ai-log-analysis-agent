import os
import re
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(r"c:/Users/shen0/ai-log-analysis-agent/ai-log-analysis-agent")
LOG_DIR = BASE_DIR / "sample_logs"
OUTPUT_DIR = BASE_DIR / "generated_report"
OUTPUT_FILE = OUTPUT_DIR / "analysis_report.md"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

log_line_regex = re.compile(r"^(?P<date>\d{4}-\d{2}-\d{2})\s+(?P<time>\d{2}:\d{2}:\d{2})\s+(?P<level>\w+)\s+(?P<msg>.*)$")

EVENT_KEYWORDS = {
    "scan": ["scan", "scheduled scan", "scan started", "scan completed"],
    "detection": ["detected", "malware detection", "threat detected"],
    "update": ["signature update", "update"],
    "warning": ["warning"],
    "error": ["error", "failed"]
}

def classify_message(message: str) -> str:
    low = message.lower()
    for evt, words in EVENT_KEYWORDS.items():
        for w in words:
            if w in low:
                return evt
    return "other"

summary = defaultdict(lambda: defaultdict(int))
raw_logs = defaultdict(list)

for log_file in LOG_DIR.glob("*.log"):
    with open(log_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            m = log_line_regex.match(line)
            if m:
                date = m.group("date")
                msg = m.group("msg")
                evt_type = classify_message(msg)
                summary[date][evt_type] += 1
                raw_logs[date].append(line)
            else:
                date = log_file.stem
                evt_type = classify_message(line)
                summary[date][evt_type] += 1
                raw_logs[date].append(line)

lines = []
lines.append("# Antivirus Log Analysis Report")
lines.append("")
lines.append("**Goal**: Provide observations, detected issues, anomalies, correlations, root‑cause analysis, and recommendations for the sample antivirus logs.")
lines.append("")
lines.append("---")
lines.append("")
lines.append("## Overview")
lines.append(f"Analyzed **{len(summary)}** days of logs covering {sum(len(v) for v in raw_logs.values())} entries.")
lines.append("")
lines.append("## Daily Summary")
lines.append("")
lines.append("| Date | Scans | Detections | Updates | Warnings | Errors | Other | Total |")
lines.append("|------|-------|------------|---------|----------|--------|-------|-------|")
for date in sorted(summary.keys()):
    s = summary[date]
    total = sum(s.values())
    lines.append(f"| {date} | {s.get('scan',0)} | {s.get('detection',0)} | {s.get('update',0)} | {s.get('warning',0)} | {s.get('error',0)} | {s.get('other',0)} | {total} |")
lines.append("")
lines.append("## Anomalies & Correlations")
lines.append("")
all_detections = [summary[d].get('detection',0) for d in summary]
if all_detections:
    avg = sum(all_detections)/len(all_detections)
    var = sum((x-avg)**2 for x in all_detections)/len(all_detections)
    std = var**0.5
    threshold = avg + 2*std
    anomalous = [d for d in summary if summary[d].get('detection',0) > threshold]
    if anomalous:
        lines.append("**Anomalous detection days** (detections > avg + 2·std):")
        for d in anomalous:
            lines.append(f"- {d}: {summary[d]['detection']} detections")
    else:
        lines.append("No significant detection anomalies detected.")
else:
    lines.append("No detection events found.")
lines.append("")
lines.append("## Root‑Cause Analysis")
lines.append("")
lines.append("- Correlate detections with preceding signature updates where possible.")
lines.append("- If a detection follows an update, consider potential false positives.")
lines.append("")
lines.append("## Recommendations")
lines.append("")
lines.append("- Review any anomalous detection spikes and verify threat signatures.")
lines.append("- Ensure signature updates succeed without causing false positives.")
lines.append("- Audit warning and error logs regularly.")
lines.append("")
lines.append("## Approval Status")
lines.append("")
lines.append("- **Pending Review**")
lines.append("")
with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
    out.write("\n".join(lines))
print(f"Report written to {OUTPUT_FILE}")
