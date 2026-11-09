"""Cluster launcher for the 4-Agent A2A Topology (`adk_agents/run_a2a_cluster.py`).

Starts the 3 specialist A2A servers in background processes:
- `builder`     -> http://localhost:8001 (/.well-known/agent-card.json)
- `executioner` -> http://localhost:8002 (/.well-known/agent-card.json)
- `revisor`     -> http://localhost:8003 (/.well-known/agent-card.json)

And launches the interactive Google ADK Web UI on port 8000 scoped ONLY to the
customer-facing `orchestrator` agent (`http://localhost:8000`).
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

REPO_ROOT = Path(__file__).resolve().parent.parent

SPECIALIST_A2A_AGENTS = [
    ("builder", "adk_agents.builder.a2a_server:app", 8001),
    ("executioner", "adk_agents.executioner.a2a_server:app", 8002),
    ("revisor", "adk_agents.revisor.a2a_server:app", 8003),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Start the 4-agent A2A cluster (Customer Web UI on http://localhost:8000)"
    )
    parser.add_argument(
        "--host",
        default="localhost",
        help="Host interface to bind servers (default: localhost)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for the customer-facing Orchestrator Web UI (default: 8000)",
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Run all 4 agents in deterministic offline mode (no external LLM key required)",
    )
    parser.add_argument(
        "--headless-a2a",
        action="store_true",
        help="Run orchestrator as a headless A2A server instead of the browser ADK Web UI",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    env = os.environ.copy()
    if args.offline:
        env["BUILDER_OFFLINE_MODE"] = "1"
        env["EXECUTIONER_OFFLINE_MODE"] = "1"
        env["REVISOR_OFFLINE_MODE"] = "1"

    processes: list[tuple[str, int, subprocess.Popen[bytes]]] = []

    print("============================================================")
    print("🚀 Starting 4-Agent A2A Cluster for Agent Traveler")
    print("============================================================")

    try:
        # 1. Start the 3 background A2A specialist servers (:8001, :8002, :8003)
        for name, app_target, port in SPECIALIST_A2A_AGENTS:
            cmd = [
                sys.executable,
                "-m",
                "uvicorn",
                app_target,
                "--host",
                args.host,
                "--port",
                str(port),
                "--log-level",
                "warning",
            ]
            proc = subprocess.Popen(cmd, cwd=str(REPO_ROOT), env=env)
            processes.append((name, port, proc))
            print(
                f"  • [{name.upper():<12}] (INTERNAL A2A SERVER) -> "
                f"http://{args.host}:{port}/.well-known/agent-card.json (PID {proc.pid})"
            )

        # 2. Start the customer-facing Orchestrator on port 8000 with the ADK Web UI
        if args.headless_a2a:
            orch_cmd = [
                sys.executable,
                "-m",
                "uvicorn",
                "adk_agents.orchestrator.a2a_server:app",
                "--host",
                args.host,
                "--port",
                str(args.port),
                "--log-level",
                "warning",
            ]
            ui_url = f"http://{args.host}:{args.port}/.well-known/agent-card.json"
        else:
            adk_bin = str(Path(sys.executable).parent / "adk")
            orchestrator_dir = str(REPO_ROOT / "adk_agents" / "orchestrator")
            orch_cmd = [
                adk_bin,
                "web",
                orchestrator_dir,
                "--host",
                args.host,
                "--port",
                str(args.port),
            ]
            ui_url = f"http://{args.host}:{args.port}/dev-ui/?app=orchestrator"

        orch_proc = subprocess.Popen(orch_cmd, cwd=str(REPO_ROOT), env=env)
        processes.append(("orchestrator", args.port, orch_proc))

        print(
            f"  • [{'ORCHESTRATOR':<12}] (CUSTOMER WEB UI)     -> "
            f"{ui_url} (PID {orch_proc.pid})"
        )
        print("------------------------------------------------------------")
        print(f"🌐 Open Customer Chat UI in your browser: {ui_url}")
        print("Press Ctrl+C to stop all 4 agents.")
        print("------------------------------------------------------------")

        while True:
            time.sleep(1.0)
            for name, port, proc in processes:
                if proc.poll() is not None:
                    raise RuntimeError(
                        f"Agent '{name}' on port {port} exited unexpectedly with code {proc.returncode}"
                    )
    except KeyboardInterrupt:
        print("\nShutting down 4-agent A2A cluster...")
    finally:
        for _name, _port, proc in processes:
            if proc.poll() is None:
                proc.send_signal(signal.SIGTERM)
        for _name, _port, proc in processes:
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()


if __name__ == "__main__":
    main()
