from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any

import requests

from .constants import API_DIR, DEFAULT_USER_AGENT, LABSTAT_DIR, RAW_DIR


def ensure_data_dirs() -> None:
    for path in (RAW_DIR, LABSTAT_DIR, API_DIR):
        path.mkdir(parents=True, exist_ok=True)


def user_agent() -> str:
    return os.environ.get("BLS_USER_AGENT", DEFAULT_USER_AGENT)


def request_headers() -> dict[str, str]:
    return {"User-Agent": user_agent()}


def decode_response_content(content: bytes) -> str:
    for encoding in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            return content.decode(encoding)
        except UnicodeDecodeError:
            continue
    return content.decode("utf-8", errors="replace")


def download_binary(url: str, path: Path, *, force: bool = False, timeout: int = 90) -> bytes:
    ensure_data_dirs()
    if path.exists() and not force:
        return path.read_bytes()

    response = requests.get(url, headers=request_headers(), timeout=timeout)
    response.raise_for_status()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(response.content)
    return response.content


def download_text(url: str, path: Path, *, force: bool = False, timeout: int = 90) -> str:
    content = download_binary(url, path, force=force, timeout=timeout)
    return decode_response_content(content)


def stable_json_hash(payload: dict[str, Any]) -> str:
    dumped = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(dumped.encode("utf-8")).hexdigest()[:16]


def post_json_cached(
    url: str,
    payload: dict[str, Any],
    *,
    cache_name: str | None = None,
    force: bool = False,
    timeout: int = 120,
) -> dict[str, Any]:
    ensure_data_dirs()
    name = cache_name or stable_json_hash(payload)
    path = API_DIR / f"{name}.json"
    if path.exists() and not force:
        return json.loads(path.read_text(encoding="utf-8"))

    response = requests.post(
        url,
        json=payload,
        headers={**request_headers(), "Content-Type": "application/json"},
        timeout=timeout,
    )
    response.raise_for_status()
    data = response.json()
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
    return data


@dataclass(frozen=True)
class ReleaseCalendarEntry:
    release_date: date
    release_time: str
    text: str


def parse_release_calendar(html: str) -> list[ReleaseCalendarEntry]:
    """Best-effort parser for the BLS release schedule page."""
    entries: list[ReleaseCalendarEntry] = []
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        BeautifulSoup = None  # type: ignore[assignment]

    if BeautifulSoup is not None:
        soup = BeautifulSoup(html, "html.parser")
        for row in soup.find_all("tr"):
            text = " ".join(row.get_text(" ", strip=True).split())
            if "Consumer Price Index" not in text:
                continue
            match = re.search(
                r"([A-Z][a-z]+)\s+(\d{1,2}),\s+(\d{4}).*?(\d{1,2}:\d{2}\s*[AP]\.?\s*M\.?|8:30)",
                text,
            )
            if not match:
                continue
            month, day, year, release_time = match.groups()
            try:
                release_date = datetime.strptime(
                    f"{month} {day} {year}", "%B %d %Y"
                ).date()
            except ValueError:
                continue
            entries.append(
                ReleaseCalendarEntry(
                    release_date=release_date,
                    release_time=release_time.replace(" ", ""),
                    text=text,
                )
            )
        return sorted(entries, key=lambda item: item.release_date)

    for match in re.finditer(
        r"Consumer Price Index.*?([A-Z][a-z]+)\s+(\d{1,2}),\s+(\d{4})",
        html,
        flags=re.I | re.S,
    ):
        month, day, year = match.groups()
        try:
            release_date = datetime.strptime(f"{month} {day} {year}", "%B %d %Y").date()
        except ValueError:
            continue
        entries.append(
            ReleaseCalendarEntry(
                release_date=release_date,
                release_time="8:30 a.m. ET",
                text=match.group(0)[:200],
            )
        )
    return sorted(entries, key=lambda item: item.release_date)


def next_cpi_release(entries: list[ReleaseCalendarEntry], *, as_of: date | None = None) -> ReleaseCalendarEntry | None:
    today = as_of or date.today()
    for entry in entries:
        if entry.release_date >= today:
            return entry
    return entries[-1] if entries else None
