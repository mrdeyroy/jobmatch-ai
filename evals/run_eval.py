"""Stub: offline eval pipeline (golden set + LLM-as-a-judge) for CI."""
import json
import os

GOLDEN_SET_PATH = os.path.join(os.path.dirname(__file__), "golden_set.jsonl")


def load_golden_set():
    with open(GOLDEN_SET_PATH) as f:
        return [json.loads(line) for line in f if line.strip()]


def run_eval():
    golden = load_golden_set()
    print(f"Loaded {len(golden)} golden-set examples.")
    print("TODO: Run each example through ATS agent + CV tailor agent.")
    print("TODO: Score with LLM-as-a-judge (see judge_prompt.txt).")
    print("TODO: Block CI if regression > threshold.")


if __name__ == "__main__":
    run_eval()