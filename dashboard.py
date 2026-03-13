#!/usr/bin/env python3
"""Dashboard module for displaying system stats using Rich."""
from typing import List, Dict, Optional

from rich.live import Live
from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from rich.table import Table
import time


class Dashboard:
    def __init__(self):
        self.console = Console()
        self.layout = self._create_layout()
        self.live = Live(self.layout, console=self.console, refresh_per_second=2)
        self.live.start()

    def _create_layout(self) -> Layout:
        layout = Layout()
        body = Layout()
        body.split_row(
            Layout(name="gpu", ratio=1),
            Layout(name="power", ratio=1),
            Layout(name="system", ratio=1)
        )
        layout.split_column(
            Layout(name="header", size=3),
            body,
            Layout(name="servers"),
            Layout(name="footer", size=2)
        )
        return layout

    def _header_panel(self, timestamp: str) -> Panel:
        title = Text()
        title.append("AI System Monitor - ", style="bold cyan")
        title.append(timestamp)
        return Panel(title, border_style="cyan")

    def _gpu_panel(self, gpu_data: Optional[List[Dict]]) -> Panel:
        lines = []
        if gpu_data:
            for i, gpu in enumerate(gpu_data):
                if i > 0:
                    lines.append("")
                util_bar = self._make_bar(gpu["utilization"])
                vram_bar = self._make_bar(gpu["vram_pct"])
                lines.append(f"GPU{i} Util: {util_bar} {gpu['utilization']}%")
                lines.append(
                    f"VRAM: {vram_bar} "
                    f"{gpu['vram_used_gb']:.1f}/{gpu['vram_total_gb']:.1f}GB ({gpu['vram_pct']:.0f}%)")
        else:
            lines.append("No NVIDIA GPU detected")
            lines.append("(or nvidia-smi not available)")
        return Panel("\n".join(lines), title="GPU", border_style="green")

    def _power_panel(self, power_data: Optional[Dict]) -> Panel:
        if not power_data:
            content = "Power data unavailable"
            return Panel(content, title="POWER / CONNECTOR RISK", border_style="dim")
        
        risk_styles = {"LOW": "green", "MODERATE": "yellow", "HIGH": "red"}
        risk_style = risk_styles.get(power_data["risk_level"], "white")
        power_bar = self._make_bar(power_data["power_pct"])
        
        lines = [
            f"Power: {power_bar} {power_data['power_draw']:.0f}W / {power_data['power_limit']:.0f}W ({power_data['power_pct']:.0f}%)",
            f"Temp:  {power_data['gpu_temp']}°C",
            f"Fan:   {power_data['fan_speed']}%",
            f"Risk:  [{risk_style}]{power_data['risk_level']}[/{risk_style}]"
        ]
        
        content = "\n".join(lines)
        content += "\n\nNote: Connector temp estimated via proxy (no direct sensor)"
        return Panel(content, title="POWER / CONNECTOR RISK", border_style=risk_style)

    def _system_panel(self, cpu_usage: float, ram_used: int, 
                      ram_total: int, ram_pct: float) -> Panel:
        cpu_bar = self._make_bar(cpu_usage)
        ram_bar = self._make_bar(ram_pct)
        ram_used_gb = ram_used / 1024
        ram_total_gb = ram_total / 1024
        content = (
            f"CPU: {cpu_bar} {cpu_usage:.0f}%\n"
            f"RAM: {ram_bar} {ram_pct:.0f}% ({ram_used_gb:.1f}/{ram_total_gb:.1f}GB)"
        )
        return Panel(content, title="System", border_style="blue")

    def _servers_panel(self, llm_servers: List[Dict],
                        comfyui_servers: List[Dict],
                        comfyui_labels: List[Dict]) -> Panel:
        lines = []

        # LLM Servers
        lines.append("LLM SERVERS")
        lines.append("-" * 15)
        for server in llm_servers:
            icon = "●" if server["status"] == "ONLINE" else "○"
            model = server.get("model_id") or "N/A"
            status_style = "green" if server["status"] == "ONLINE" else "dim"
            lines.append(f"  Port {server['port']}: [{status_style}]{icon} {server['status']} {model}[/{status_style}]")

        lines.append("")
        lines.append("COMFYUI SERVERS")
        lines.append("-" * 15)

        # Build server status lookup by port
        server_lookup = {s["port"]: s for s in comfyui_servers}

        # Iterate over expected labels to ensure all ports are shown
        for label_config in comfyui_labels:
            port = label_config["port"]
            label = label_config["label"]
            server = server_lookup.get(port, {"status": "OFFLINE", "error": None})

            icon = "●" if server["status"] == "ONLINE" else "○"
            status_style = "green" if server["status"] == "ONLINE" else "dim"
            lines.append(f"  [{status_style}]{icon}[/{status_style}] {label} ({port})")

        return Panel("\n".join(lines), title="Servers", border_style="magenta")

    def _footer_panel(self) -> Panel:
        content = Text()
        content.append("Refreshing every second... Press Ctrl+C to exit", style="dim")
        return Panel(content, border_style="dim", expand=True)

    def _make_bar(self, value: float, max_val: int = 100) -> str:
        filled = int((value / max_val) * 24)
        empty = 24 - filled
        return "█" * filled + "░" * empty

    def update(self,
               gpu_data: Optional[List[Dict]],
               cpu_usage: float,
               ram_used: int,
               ram_total: int,
               ram_pct: float,
               llm_servers: List[Dict],
               comfyui_servers: List[Dict],
               comfyui_labels: List[Dict],
               power_data: Optional[Dict] = None) -> None:
        timestamp = time.strftime("%H:%M:%S")
        
        self.layout["header"].update(self._header_panel(timestamp))
        self.layout["gpu"].update(self._gpu_panel(gpu_data))
        self.layout["power"].update(self._power_panel(power_data))
        self.layout["system"].update(self._system_panel(cpu_usage, ram_used, ram_total, ram_pct))
        self.layout["servers"].update(self._servers_panel(llm_servers, comfyui_servers, comfyui_labels))
        self.layout["footer"].update(self._footer_panel())

    def stop(self) -> None:
        self.live.stop()
