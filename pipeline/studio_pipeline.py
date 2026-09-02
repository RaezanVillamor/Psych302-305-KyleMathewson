#!/usr/bin/env python3
"""PSYCH 302/305 Canvas helpers. Reuses the Psych275 Canvas client and token."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TEMPLATES = ROOT / "templates"
OUT = ROOT / "out"
IDS_PATH = OUT / "ids.json"
PSYCH275_PIPELINE = Path("/Users/kylemathewson/Teaching/Psych275_Instructor/pipeline")

FORM_KEYS = (
    "GitHub username",
    "GitHub profile",
    "Account",
    "Education application",
    "Repo consent",
    "No paid Copilot",
)


def _load_env() -> None:
    sys.path.insert(0, str(PSYCH275_PIPELINE))
    from dotenv import load_dotenv

    load_dotenv(PSYCH275_PIPELINE / ".env")
    load_dotenv(ROOT / ".env", override=True)
    os.environ.setdefault("CANVAS_COURSE_ID", "35483")


def _client():
    _load_env()
    from lib.canvas import CanvasClient

    return CanvasClient()


def _notify_request(client, method: str, path: str, **kwargs):
    """Student-visible writes: allow Canvas email, unlike the 275 plant path."""
    resp = client.session.request(method, client._url(path), timeout=60, **kwargs)
    if resp.status_code >= 400:
        from lib.canvas import CanvasError

        raise CanvasError(f"{method} {path} → {resp.status_code}: {resp.text[:800]}")
    return resp.json() if resp.content else None


def _read(name: str) -> str:
    return (TEMPLATES / name).read_text(encoding="utf-8")


def _save_ids(update: dict) -> dict:
    OUT.mkdir(exist_ok=True)
    data = {}
    if IDS_PATH.exists():
        data = json.loads(IDS_PATH.read_text())
    data.update(update)
    IDS_PATH.write_text(json.dumps(data, indent=2) + "\n")
    return data


def cmd_courses(_: argparse.Namespace) -> None:
    client = _client()
    for row in client.list_courses():
        print(f"{row.get('id')}\t{row.get('course_code')}\t{row.get('name')}")


def cmd_week0_create(args: argparse.Namespace) -> None:
    client = _client()
    cid = client.require_course()
    name = "Week 0 · GitHub username"
    existing = client.find_assignment_by_name(name)
    if existing and not args.replace:
        print(f"exists {existing['id']} {existing.get('html_url')}")
        _save_ids({"week0_assignment_id": existing["id"], "course_id": int(cid)})
        return

    assignment = _notify_request(
        client,
        "POST",
        f"/courses/{cid}/assignments",
        json={
            "assignment": {
                "name": name,
                "description": _read("week0_assignment.html"),
                "submission_types": ["online_text_entry"],
                "points_possible": 1,
                "grading_type": "pass_fail",
                "published": True,
                "allowed_attempts": -1,
                "due_at": "2026-09-02T18:00:00-06:00",
                "omit_from_final_grade": True,
                "notify_of_update": True,
            }
        },
    )
    announcement = _notify_request(
        client,
        "POST",
        f"/courses/{cid}/discussion_topics",
        json={
            "title": "Week 0 is up: GitHub username before Wednesday 18:00",
            "message": _read("week0_announcement.html"),
            "is_announcement": True,
            "published": True,
        },
    )
    ids = _save_ids(
        {
            "course_id": int(cid),
            "week0_assignment_id": assignment["id"],
            "week0_announcement_id": announcement.get("id"),
            "week0_assignment_url": assignment.get("html_url"),
        }
    )
    print(json.dumps(ids, indent=2))


def parse_week0_body(body: str) -> dict:
    text = re.sub(r"<[^>]+>", "\n", body or "")
    text = text.replace("&nbsp;", " ").replace("&amp;", "&")
    found = {}
    for key in FORM_KEYS:
        m = re.search(rf"{re.escape(key)}\s*:\s*(\S[^\n]*)", text, re.I)
        found[key] = (m.group(1).strip() if m else "")
    username = re.sub(r"^@", "", found.get("GitHub username", "")).strip()
    profile = found.get("GitHub profile", "").strip()
    if username and not profile:
        profile = f"https://github.com/{username}"
    if not username and profile:
        m = re.search(r"github\.com/([A-Za-z0-9-]+)", profile)
        if m:
            username = m.group(1)
    return {
        "github_username": username,
        "github_profile": profile,
        "account": found.get("Account", "").lower(),
        "education": found.get("Education application", "").lower(),
        "repo_consent": found.get("Repo consent", "").lower(),
        "no_paid_copilot": found.get("No paid Copilot", "").lower(),
        "raw_keys": found,
    }


def cmd_week0_pull(_: argparse.Namespace) -> None:
    client = _client()
    ids = json.loads(IDS_PATH.read_text()) if IDS_PATH.exists() else {}
    aid = os.environ.get("CANVAS_WEEK0_ASSIGNMENT_ID") or ids.get("week0_assignment_id")
    if not aid:
        raise SystemExit("No Week 0 assignment id. Run week0-create first.")
    rows = []
    for sub in client.list_submissions(aid):
        user = sub.get("user") or {}
        parsed = parse_week0_body(sub.get("body") or "")
        rows.append(
            {
                "canvasUserId": sub.get("user_id"),
                "canvasName": user.get("name"),
                "sortableName": user.get("sortable_name"),
                "sisUserId": user.get("sis_user_id"),
                "workflow": sub.get("workflow_state"),
                **parsed,
            }
        )
    OUT.mkdir(exist_ok=True)
    dest = OUT / "week0_roster.json"
    dest.write_text(json.dumps(rows, indent=2) + "\n")
    submitted = [r for r in rows if r["github_username"]]
    print(f"wrote {dest}  {len(submitted)}/{len(rows)} with a username")


def main() -> None:
    p = argparse.ArgumentParser(description="PSYCH 302/305 Canvas studio pipeline")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("courses").set_defaults(func=cmd_courses)
    c = sub.add_parser("week0-create")
    c.add_argument("--replace", action="store_true")
    c.set_defaults(func=cmd_week0_create)
    sub.add_parser("week0-pull").set_defaults(func=cmd_week0_pull)
    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
