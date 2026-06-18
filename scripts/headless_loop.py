#!/usr/bin/env python3
from pathlib import Path
import argparse, sys
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from cabinet_framework.model import ensure_runtime
from cabinet_framework.dispatcher import heartbeat

def main() -> int:
    ap=argparse.ArgumentParser(description='Cabinet Agent Framework headless heartbeat runner')
    ap.add_argument('--cycles', type=int, default=1)
    ap.add_argument('--sleep', type=int, default=0)
    ap.add_argument('--mode', choices=['prompt','hermes'], default='prompt')
    ns=ap.parse_args()
    ensure_runtime()
    print(heartbeat(mode=ns.mode, cycles=ns.cycles, sleep_s=ns.sleep))
    return 0
if __name__ == '__main__': raise SystemExit(main())
