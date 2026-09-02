"""Create Canvas assignment groups, weekly shells, and week modules for 35483."""

from __future__ import annotations

import json
from typing import Any

BOOK = "https://kylemath.github.io/Psych302-305-KyleMathewson"

WEEKLIES = [
    {
        "n": 1,
        "name": "Week 1 · Laboratory report",
        "due": "2026-09-08T17:00:00-06:00",
        "due_display": "8 September 2026",
        "meet": "2 September",
        "lab": f"{BOOK}/playground.html",
        "lab_label": "Week 1 playground",
        "note_path": "lab-notes/week01.md",
        "ask": "The three ways you made the page about yourself.",
        "module": "Week 1 · GitHub and playground (2 Sep)",
        "preamble": "Own repo, Pages, fork the whole class repo, then a PR. The coolest one becomes the homepage.",
    },
    {
        "n": 2,
        "name": "Week 2 · Laboratory report",
        "due": "2026-09-15T17:00:00-06:00",
        "due_display": "15 September 2026",
        "meet": "9 September",
        "lab": f"{BOOK}/rt.html",
        "lab_label": "Week 2 reaction time",
        "note_path": "lab-notes/week02.md",
        "ask": "Your predicted mean, then n, mean RT, SD, and one limitation. CSV in data/.",
        "module": "Week 2 · Reaction time (9 Sep)",
    },
    {
        "n": 3,
        "name": "Week 3 · Laboratory report",
        "due": "2026-09-22T17:00:00-06:00",
        "due_display": "22 September 2026",
        "meet": "16 September",
        "lab": f"{BOOK}/inventory.html",
        "lab_label": "Week 3 inventory",
        "note_path": "lab-notes/week03.md",
        "ask": "One subscale mean, item count, and one limitation of self-report. CSV in data/.",
        "module": "Week 3 · Inventory (16 Sep)",
    },
    {
        "n": 4,
        "name": "Week 4 · Laboratory report",
        "due": "2026-09-29T17:00:00-06:00",
        "due_display": "29 September 2026",
        "meet": "23 September",
        "lab": f"{BOOK}/stats.html",
        "lab_label": "Week 4 descriptives",
        "note_path": "lab-notes/week04.md",
        "ask": "n, mean, SD, and what you excluded. Due 29 September (no class 30 September).",
        "module": "Week 4 · Descriptives (23 Sep)",
    },
    {
        "n": 5,
        "name": "Week 5 · Laboratory report",
        "due": "2026-10-13T17:00:00-06:00",
        "due_display": "13 October 2026",
        "meet": "7 October",
        "lab": f"{BOOK}/compare.html",
        "lab_label": "Week 5 comparison",
        "note_path": "lab-notes/week05.md",
        "ask": "The comparison you wrote before looking, two means, two ns, and whether the data agreed.",
        "module": "Week 5 · Comparison (7 Oct)",
    },
    {
        "n": 6,
        "name": "Week 6 · Laboratory report",
        "due": "2026-10-20T17:00:00-06:00",
        "due_display": "20 October 2026",
        "meet": "14 October",
        "lab": f"{BOOK}/cite.html",
        "lab_label": "Week 6 citation",
        "note_path": "lab-notes/week06.md",
        "ask": "Complete reference, path or URL in papers/, and the question / method / one limit.",
        "module": "Week 6 · Citation (14 Oct)",
    },
    {
        "n": 7,
        "name": "Week 7 · Laboratory report",
        "due": "2026-10-27T17:00:00-06:00",
        "due_display": "27 October 2026",
        "meet": "21 October",
        "lab": f"{BOOK}/methods.html",
        "lab_label": "Week 7 Methods",
        "note_path": "lab-notes/week07.md",
        "ask": "Path to your Methods file. Timing, keys, and exclusion rules in numbers.",
        "module": "Week 7 · Methods (21 Oct)",
    },
    {
        "n": 8,
        "name": "Week 8 · Laboratory report",
        "due": "2026-11-03T17:00:00-07:00",
        "due_display": "3 November 2026",
        "meet": "28 October",
        "lab": f"{BOOK}/results.html",
        "lab_label": "Week 8 results page",
        "note_path": "lab-notes/week08.md",
        "ask": "Path to the results page and the claim. The 15% check-in is a separate assignment.",
        "module": "Week 8 · Results and check-in (28 Oct)",
    },
    {
        "n": 9,
        "name": "Week 9 · Laboratory report",
        "due": "2026-11-10T17:00:00-07:00",
        "due_display": "10 November 2026",
        "meet": "4 November",
        "lab": f"{BOOK}/game.html",
        "lab_label": "Week 9 gamified research",
        "note_path": "lab-notes/week09.md",
        "ask": "Your question of interest, the game as the instrument, what was logged (including the Science extra variable). Last weekly report.",
        "module": "Week 9 · Gamified research (4 Nov)",
    },
]

# ensure_module matches by name. A title change creates a second module.
# Unpublish leftovers only after the replacement exists (see run()).
LEFTOVER_UNPUBLISH = {
    "Week 1 · Codespace (2 Sep)",
    "Week 9 · Small n (4 Nov)",
}


def fill(template: str, **kwargs: str) -> str:
    text = template
    for key, value in kwargs.items():
        text = text.replace("{{" + key + "}}", str(value))
    text = text.replace("{{preamble}}", "")
    return text


def ensure_group(notify, cid: str, groups: list[dict], name: str, weight: float, drop_lowest: int = 0) -> dict:
    for g in groups:
        if g["name"] == name:
            body: dict[str, Any] = {"name": name, "group_weight": weight}
            if drop_lowest:
                body["rules"] = {"drop_lowest": drop_lowest}
            updated = notify("PUT", f"/courses/{cid}/assignment_groups/{g['id']}", json=body)
            return updated
    body = {"name": name, "group_weight": weight}
    if drop_lowest:
        body["rules"] = {"drop_lowest": drop_lowest}
    return notify("POST", f"/courses/{cid}/assignment_groups", json=body)


def ensure_assignment(notify, client, cid: str, *, name: str, description: str, due_at: str, points: float, group_id: int) -> dict:
    existing = client.find_assignment_by_name(name)
    payload = {
        "assignment": {
            "name": name,
            "description": description,
            "submission_types": ["online_text_entry"],
            "points_possible": points,
            "grading_type": "points",
            "published": True,
            "allowed_attempts": -1,
            "due_at": due_at,
            "assignment_group_id": group_id,
            "omit_from_final_grade": False,
            "notify_of_update": True,
        }
    }
    if existing:
        return notify("PUT", f"/courses/{cid}/assignments/{existing['id']}", json=payload)
    return notify("POST", f"/courses/{cid}/assignments", json=payload)


def ensure_module(notify, cid: str, modules: list[dict], name: str, position: int) -> dict:
    for m in modules:
        if m["name"] == name:
            return notify(
                "PUT",
                f"/courses/{cid}/modules/{m['id']}",
                json={"module": {"name": name, "published": True, "position": position}},
            )
    return notify(
        "POST",
        f"/courses/{cid}/modules",
        json={"module": {"name": name, "published": True, "position": position}},
    )


def module_items(client, cid: str, mid: int) -> list[dict]:
    return client._request("GET", f"/courses/{cid}/modules/{mid}/items", params={"per_page": 100})


def ensure_item(notify, cid: str, mid: int, items: list[dict], title: str, spec: dict) -> dict:
    for it in items:
        if it.get("title") == title:
            body = {"module_item": {**spec, "title": title, "published": True}}
            return notify("PUT", f"/courses/{cid}/modules/{mid}/items/{it['id']}", json=body)
    body = {"module_item": {**spec, "title": title, "published": True}}
    return notify("POST", f"/courses/{cid}/modules/{mid}/items", json=body)


def set_module_published(notify, cid: str, mid: int, published: bool) -> None:
    notify("PUT", f"/courses/{cid}/modules/{mid}", json={"module": {"published": published}})


def unpublish_named_modules(notify, cid: str, modules: list[dict], names: set[str]) -> None:
    for m in modules:
        if m["name"] in names and m.get("published"):
            set_module_published(notify, cid, m["id"], False)


def run(client, notify, read_template, save_ids) -> dict:
    cid = client.require_course()
    notify(
        "PUT",
        f"/courses/{cid}",
        json={"course": {"apply_assignment_group_weights": True}},
    )
    groups = client._request("GET", f"/courses/{cid}/assignment_groups", params={"per_page": 50})
    g_gate = ensure_group(notify, cid, groups, "Complete / incomplete", 0)
    groups = client._request("GET", f"/courses/{cid}/assignment_groups", params={"per_page": 50})
    g_week = ensure_group(notify, cid, groups, "Weekly reports", 50)
    groups = client._request("GET", f"/courses/{cid}/assignment_groups", params={"per_page": 50})
    g_mid = ensure_group(notify, cid, groups, "Midterm check-in", 15)
    groups = client._request("GET", f"/courses/{cid}/assignment_groups", params={"per_page": 50})
    g_fin = ensure_group(notify, cid, groups, "Final project", 35)

    week0 = client.find_assignment_by_name("Week 0 · GitHub username")
    if week0:
        notify(
            "PUT",
            f"/courses/{cid}/assignments/{week0['id']}",
            json={
                "assignment": {
                    "name": "Week 0 · GitHub username",
                    "description": read_template("week0_assignment.html"),
                    "assignment_group_id": g_gate["id"],
                    "omit_from_final_grade": True,
                    "due_at": "2026-09-02T21:00:00-06:00",
                    "notify_of_update": True,
                }
            },
        )

    notify(
        "PUT",
        f"/courses/{cid}/pages/introduction",
        json={
            "wiki_page": {
                "title": "Introduction",
                "body": read_template("introduction.html"),
                "published": True,
                "front_page": True,
            }
        },
    )
    notify(
        "PUT",
        f"/courses/{cid}/pages/schedule",
        json={
            "wiki_page": {
                "title": "Schedule",
                "body": read_template("schedule_page.html"),
                "published": True,
            }
        },
    )

    weekly_ids = {}
    weekly_tpl = read_template("weekly_report.html")
    week1_tpl = read_template("week1_report.html")
    for row in WEEKLIES:
        tpl = week1_tpl if row["n"] == 1 else weekly_tpl
        asg = ensure_assignment(
            notify,
            client,
            cid,
            name=row["name"],
            description=fill(tpl, **{k: str(row[k]) for k in row}),
            due_at=row["due"],
            points=10,
            group_id=g_week["id"],
        )
        weekly_ids[f"week{row['n']:02d}"] = {"id": asg["id"], "url": asg.get("html_url")}

    notify(
        "PUT",
        f"/courses/{cid}/assignment_groups/{g_week['id']}",
        json={"name": "Weekly reports", "group_weight": 50, "rules": {"drop_lowest": 1}},
    )

    checkin = ensure_assignment(
        notify,
        client,
        cid,
        name="Midterm check-in",
        description=read_template("checkin.html"),
        due_at="2026-10-28T21:00:00-06:00",
        points=15,
        group_id=g_mid["id"],
    )
    final = ensure_assignment(
        notify,
        client,
        cid,
        name="Final project",
        description=read_template("final.html"),
        due_at="2026-12-02T21:00:00-07:00",
        points=35,
        group_id=g_fin["id"],
    )

    modules = client._request("GET", f"/courses/{cid}/modules", params={"per_page": 100})
    unpublish_named_modules(
        notify,
        cid,
        modules,
        {
            "Welcome to the Course: Your Journey Begins Here!",
            "Template Module",
            "Course Conclusion",
        },
    )

    qa = None
    for topic in client._request("GET", f"/courses/{cid}/discussion_topics", params={"per_page": 50}):
        if topic.get("title") == "Course Q&A":
            qa = topic
            break

    start = ensure_module(notify, cid, modules, "Start here", 1)
    start_items = module_items(client, cid, start["id"])
    ensure_item(notify, cid, start["id"], start_items, "Introduction", {"type": "Page", "page_url": "introduction"})
    start_items = module_items(client, cid, start["id"])
    ensure_item(notify, cid, start["id"], start_items, "Schedule", {"type": "Page", "page_url": "schedule"})
    if week0:
        start_items = module_items(client, cid, start["id"])
        ensure_item(
            notify,
            cid,
            start["id"],
            start_items,
            "Week 0 · GitHub username",
            {"type": "Assignment", "content_id": week0["id"]},
        )
    start_items = module_items(client, cid, start["id"])
    ensure_item(
        notify,
        cid,
        start["id"],
        start_items,
        "Computing environment",
        {"type": "ExternalUrl", "external_url": f"{BOOK}/workflow.html", "new_tab": True},
    )
    start_items = module_items(client, cid, start["id"])
    ensure_item(
        notify,
        cid,
        start["id"],
        start_items,
        "Laboratory handbook",
        {"type": "ExternalUrl", "external_url": f"{BOOK}/labs.html", "new_tab": True},
    )
    if qa:
        start_items = module_items(client, cid, start["id"])
        ensure_item(
            notify,
            cid,
            start["id"],
            start_items,
            "Course Q&A",
            {"type": "Discussion", "content_id": qa["id"]},
        )

    week_mods = {}
    for i, row in enumerate(WEEKLIES, start=2):
        modules = client._request("GET", f"/courses/{cid}/modules", params={"per_page": 100})
        mod = ensure_module(notify, cid, modules, row["module"], i)
        items = module_items(client, cid, mod["id"])
        ensure_item(
            notify,
            cid,
            mod["id"],
            items,
            row["lab_label"],
            {"type": "ExternalUrl", "external_url": row["lab"], "new_tab": True},
        )
        items = module_items(client, cid, mod["id"])
        ensure_item(
            notify,
            cid,
            mod["id"],
            items,
            row["name"],
            {"type": "Assignment", "content_id": weekly_ids[f"week{row['n']:02d}"]["id"]},
        )
        if row["n"] == 1 and week0:
            items = module_items(client, cid, mod["id"])
            ensure_item(
                notify,
                cid,
                mod["id"],
                items,
                "Week 0 · GitHub username",
                {"type": "Assignment", "content_id": week0["id"], "position": 1},
            )
        if row["n"] == 8:
            items = module_items(client, cid, mod["id"])
            ensure_item(
                notify,
                cid,
                mod["id"],
                items,
                "Midterm check-in",
                {"type": "Assignment", "content_id": checkin["id"]},
            )
        week_mods[row["n"]] = mod["id"]

    modules = client._request("GET", f"/courses/{cid}/modules", params={"per_page": 100})
    unpublish_named_modules(notify, cid, modules, LEFTOVER_UNPUBLISH)

    modules = client._request("GET", f"/courses/{cid}/modules", params={"per_page": 100})
    proj = ensure_module(notify, cid, modules, "Weeks 10–12 · Individual project", 11)
    items = module_items(client, cid, proj["id"])
    ensure_item(
        notify,
        cid,
        proj["id"],
        items,
        "Project brief",
        {"type": "ExternalUrl", "external_url": f"{BOOK}/project.html", "new_tab": True},
    )
    items = module_items(client, cid, proj["id"])
    ensure_item(
        notify,
        cid,
        proj["id"],
        items,
        "Final project",
        {"type": "Assignment", "content_id": final["id"]},
    )

    ours = {
        "Start here",
        *[row["module"] for row in WEEKLIES],
        "Weeks 10–12 · Individual project",
    }
    modules = client._request("GET", f"/courses/{cid}/modules", params={"per_page": 100})
    for m in modules:
        if m["name"] in ours:
            set_module_published(notify, cid, m["id"], True)
            for it in module_items(client, cid, m["id"]):
                if not it.get("published"):
                    notify(
                        "PUT",
                        f"/courses/{cid}/modules/{m['id']}/items/{it['id']}",
                        json={"module_item": {"published": True}},
                    )
        elif m["name"] == "Need Help?":
            set_module_published(notify, cid, m["id"], False)

    night_title = "Tonight: GitHub first, then the playground"
    night = None
    for topic in client._request("GET", f"/courses/{cid}/discussion_topics", params={"per_page": 50, "only_announcements": True}):
        if topic.get("title") == night_title:
            night = topic
            break
    night_body = {
        "title": night_title,
        "message": read_template("first_night_announcement.html"),
        "is_announcement": True,
        "published": True,
    }
    if night:
        notify("PUT", f"/courses/{cid}/discussion_topics/{night['id']}", json=night_body)
    else:
        night = notify("POST", f"/courses/{cid}/discussion_topics", json=night_body)

    try:
        notify("PUT", f"/courses/{cid}/tabs/modules", json={"hidden": False, "position": 5})
    except Exception as exc:
        print("tab unhide failed:", exc)

    ids = save_ids(
        {
            "assignment_group_gate": g_gate["id"],
            "assignment_group_weekly": g_week["id"],
            "assignment_group_checkin": g_mid["id"],
            "assignment_group_final": g_fin["id"],
            "checkin_assignment_id": checkin["id"],
            "checkin_url": checkin.get("html_url"),
            "final_assignment_id": final["id"],
            "final_url": final.get("html_url"),
            "weekly_assignments": weekly_ids,
            "start_module_id": start["id"],
            "week_module_ids": week_mods,
            "project_module_id": proj["id"],
            "first_night_announcement_id": (night or {}).get("id"),
        }
    )
    print(json.dumps({k: ids[k] for k in ids if k != "weekly_assignments"}, indent=2))
    print("weeklies", json.dumps(weekly_ids, indent=2))
    return ids
