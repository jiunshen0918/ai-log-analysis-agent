import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='[HumanReview] %(message)s')

# This file is created by the security checkpoint
REVIEW_QUEUE = Path(__file__).parents[2] / "human_review_queue.json"


def run():
    """Load queued entries and present them for manual handling."""
    if not REVIEW_QUEUE.is_file():
        logging.info("No items awaiting human review.")
        return

    try:
        with open(REVIEW_QUEUE, "r", encoding="utf-8") as f:
            items = json.load(f)
    except Exception as e:
        logging.error(f"Failed to read review queue: {e}")
        return

    if not items:
        logging.info("Human‑review queue is empty.")
        return

    logging.info(f"=== {len(items)} log entry(ies) require human review ===")
    for idx, entry in enumerate(items, start=1):
        logging.info(f"\n--- Entry {idx} ---")
        logging.info(f"Original : {entry.get('original')}")
        logging.info(f"Redacted : {entry.get('redacted')}")
        # In a real deployment you would prompt the operator or raise a ticket.
        # Here we just log; you can later clear the queue once reviewed.
    # Optionally clear after review:
    # REVIEW_QUEUE.unlink()
