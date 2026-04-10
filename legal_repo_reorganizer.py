#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

REPO_TOP_LEVELS = [
    "00_Admin",
    "01_Case_Management",
    "02_Pleadings",
    "03_Discovery",
    "04_Exhibits",
    "05_Legal_Authorities",
    "06_Research",
    "07_Depositions",
    "08_Settlement",
    "09_Trial",
    "10_Post_Judgment",
    "11_Templates",
    "98_Needs_Review",
    "99_Archive",
]

DESTINATIONS = [
    "00_Admin/Contacts",
    "00_Admin/Correspondence",
    "00_Admin/Deadlines",
    "00_Admin/Research_Log",
    "01_Case_Management/Case_Caption",
    "01_Case_Management/Court_Orders",
    "01_Case_Management/Docket",
    "01_Case_Management/Service",
    "02_Pleadings/Complaints",
    "02_Pleadings/Motions",
    "02_Pleadings/Responses",
    "02_Pleadings/Replies",
    "02_Pleadings/Notices",
    "02_Pleadings/Proposed_Orders",
    "02_Pleadings/Declarations",
    "02_Pleadings/Briefs",
    "03_Discovery/Initial_Disclosures",
    "03_Discovery/Interrogatories",
    "03_Discovery/Requests_for_Production",
    "03_Discovery/Requests_for_Admission",
    "03_Discovery/Subpoenas",
    "03_Discovery/Meet_and_Confer",
    "03_Discovery/Protective_Orders",
    "04_Exhibits/Exhibit_Indexes",
    "04_Exhibits/Exhibit_Binders",
    "04_Exhibits/Emails",
    "04_Exhibits/Policies",
    "04_Exhibits/Medical_Records",
    "04_Exhibits/Personnel_Records",
    "04_Exhibits/Agency_Records",
    "04_Exhibits/Audio_Video",
    "04_Exhibits/Photos",
    "04_Exhibits/Government_Reports",
    "05_Legal_Authorities/Cases",
    "05_Legal_Authorities/Statutes",
    "05_Legal_Authorities/Regulations",
    "05_Legal_Authorities/Agency_Guidance",
    "05_Legal_Authorities/Local_Rules",
    "05_Legal_Authorities/Federal_Rules",
    "06_Research/Issue_Memos",
    "06_Research/Chronologies",
    "06_Research/Witness_Notes",
    "06_Research/Timelines",
    "07_Depositions/Notices",
    "07_Depositions/Transcripts",
    "07_Depositions/Errata",
    "07_Depositions/Exhibits",
    "08_Settlement/Demands",
    "08_Settlement/Mediation",
    "08_Settlement/Offers",
    "09_Trial/Trial_Briefs",
    "09_Trial/Witnesses",
    "09_Trial/Exhibits",
    "09_Trial/Jury_Instructions",
    "09_Trial/Voir_Dire",
    "09_Trial/Opening",
    "09_Trial/Closing",
    "10_Post_Judgment/Appeal",
    "10_Post_Judgment/Enforcement",
    "11_Templates/Pleadings",
    "11_Templates/Exhibits",
    "11_Templates/Letters",
    "11_Templates/Declarations",
    "98_Needs_Review/Uncertain",
    "99_Archive",
]

TEXT_EXTS = {
    ".txt", ".md", ".markdown", ".csv", ".tsv", ".json", ".jsonl", ".xml", ".yml", ".yaml",
    ".ini", ".cfg", ".conf", ".log", ".sql", ".html", ".htm", ".css", ".js", ".ts", ".jsx",
    ".tsx", ".py", ".ps1", ".psm1", ".bat", ".cmd", ".sh", ".zsh", ".bash", ".rtf", ".eml",
}
EMAIL_EXTS = {".msg", ".eml", ".pst", ".ost", ".mbox", ".olm", ".nsf"}
PHOTO_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tif", ".tiff", ".heic", ".webp", ".svg"}
MEDIA_EXTS = {".wav", ".mp3", ".m4a", ".aac", ".flac", ".wma", ".mp4", ".mov", ".avi", ".mkv", ".wmv", ".m4v"}
DOCX_EXTS = {".docx", ".docm"}
PDF_EXTS = {".pdf"}
SKIP_FILE_NAMES = {"index.html", "_index.html", ".gitattributes", ".gitignore"}
SKIP_DIR_NAMES = {".git", ".github", "node_modules", "__pycache__"}

KEYWORDS: List[Tuple[str, List[str], int]] = [
    ("02_Pleadings/Complaints", ["complaint", "amended complaint", "fac", "sac", "tac", "fourth amended"], 80),
    ("02_Pleadings/Motions", ["motion", "motion to", "mtd", "mtn", "leave to file"], 70),
    ("02_Pleadings/Responses", ["response", "opposition", "opp.", "answering brief"], 70),
    ("02_Pleadings/Replies", ["reply", "reply brief"], 75),
    ("02_Pleadings/Notices", ["notice", "notice of", "certificate of service", "notice leave"], 65),
    ("02_Pleadings/Proposed_Orders", ["proposed order", "lodged order"], 85),
    ("02_Pleadings/Declarations", ["declaration", "affidavit", "sworn statement", "verification"], 80),
    ("02_Pleadings/Briefs", ["brief", "memorandum", "memo", "points and authorities"], 70),

    ("01_Case_Management/Court_Orders", ["order", "minute entry", "ruling", "scheduling order"], 75),
    ("01_Case_Management/Docket", ["docket", "cm/ecf", "ecf", "dkt", "docket report"], 80),
    ("01_Case_Management/Case_Caption", ["caption", "civil cover sheet", "summons"], 70),
    ("01_Case_Management/Service", ["service", "waiver", "proof of service", "return of service"], 70),

    ("03_Discovery/Initial_Disclosures", ["initial disclosure", "rule 26"], 85),
    ("03_Discovery/Interrogatories", ["interrogatory", "interrogatories"], 90),
    ("03_Discovery/Requests_for_Production", ["request for production", "requests for production", "rfp"], 90),
    ("03_Discovery/Requests_for_Admission", ["request for admission", "requests for admission", "rfa"], 90),
    ("03_Discovery/Subpoenas", ["subpoena", "duces tecum"], 90),
    ("03_Discovery/Meet_and_Confer", ["meet and confer", "meet-confer", "meet confer"], 90),
    ("03_Discovery/Protective_Orders", ["protective order", "confidentiality order"], 85),

    ("04_Exhibits/Exhibit_Indexes", ["exhibit index", "index of exhibits"], 95),
    ("04_Exhibits/Exhibit_Binders", ["binder", "tabbed exhibits", "exhibit binder"], 85),
    ("04_Exhibits/Policies", ["policy", "procedure", "sop", "manual", "protocol", "instruction"], 75),
    ("04_Exhibits/Medical_Records", ["medical record", "medical records", "physician", "progress note", "diagnosis", "treatment", "hospital", "clinic", "lab result"], 85),
    ("04_Exhibits/Personnel_Records", ["personnel", "hr", "sf-50", "eopf", "performance", "disciplinary", "leave record", "employee relations"], 85),
    ("04_Exhibits/Agency_Records", ["roi", "record of investigation", "agency record", "administrative record", "foia", "investigation"], 80),
    ("04_Exhibits/Government_Reports", ["gao", "oig", "cms", "eeoc", "mspb", "opm", "inspector general", "audit report", "oversight hearing", "government report"], 90),

    ("05_Legal_Authorities/Cases", [" v. ", " vs. ", "f.3d", "f.4th", "f.supp", "u.s.", "slip op", "westlaw", "lexis"], 85),
    ("05_Legal_Authorities/Statutes", ["u.s.c", "usc", "statute", "act", "title vii", "rehabilitation act", "ada", "fmla"], 80),
    ("05_Legal_Authorities/Regulations", ["c.f.r", "cfr", "regulation", "federal register", "opm guidance"], 80),
    ("05_Legal_Authorities/Agency_Guidance", ["guidance", "handbook", "directive", "bulletin", "faq"], 70),
    ("05_Legal_Authorities/Local_Rules", ["local rule", "lrciv", "district of arizona"], 90),
    ("05_Legal_Authorities/Federal_Rules", ["frcp", "fed. r. civ. p", "federal rules of civil procedure", "fre", "federal rules of evidence"], 90),

    ("06_Research/Issue_Memos", ["issue memo", "research memo", "analysis memo"], 90),
    ("06_Research/Chronologies", ["chronology", "chronological"], 90),
    ("06_Research/Witness_Notes", ["witness", "interview notes", "statement notes"], 70),
    ("06_Research/Timelines", ["timeline", "time line"], 90),

    ("07_Depositions/Notices", ["deposition notice", "notice of deposition", "de bene esse"], 90),
    ("07_Depositions/Transcripts", ["deposition transcript", "transcript"], 80),
    ("07_Depositions/Errata", ["errata"], 95),
    ("07_Depositions/Exhibits", ["deposition exhibit", "dep exhibit"], 90),

    ("08_Settlement/Demands", ["settlement demand", "demand letter"], 90),
    ("08_Settlement/Mediation", ["mediation", "mediator", "settlement conference"], 85),
    ("08_Settlement/Offers", ["offer of judgment", "settlement offer", "offer"], 80),

    ("09_Trial/Trial_Briefs", ["trial brief", "motions in limine", "in limine"], 85),
    ("09_Trial/Witnesses", ["witness list", "witnesses"], 85),
    ("09_Trial/Exhibits", ["trial exhibit", "exhibit list"], 80),
    ("09_Trial/Jury_Instructions", ["jury instruction", "verdict form"], 95),
    ("09_Trial/Voir_Dire", ["voir dire"], 95),
    ("09_Trial/Opening", ["opening statement", "opening"], 80),
    ("09_Trial/Closing", ["closing argument", "closing"], 80),

    ("10_Post_Judgment/Appeal", ["appeal", "notice of appeal", "opening brief", "ninth circuit"], 85),
    ("10_Post_Judgment/Enforcement", ["enforcement", "collection", "writ", "garnishment", "execution"], 85),

    ("11_Templates/Pleadings", ["template", "sample pleading", "pleading template"], 80),
    ("11_Templates/Exhibits", ["exhibit template", "exhibit sticker"], 90),
    ("11_Templates/Letters", ["letter template", "sample letter"], 85),
    ("11_Templates/Declarations", ["declaration template", "affidavit template"], 90),

    ("00_Admin/Contacts", ["contact", "phone list", "address list"], 75),
    ("00_Admin/Correspondence", ["letter", "correspondence", "email chain"], 65),
    ("00_Admin/Deadlines", ["deadline", "calendar", "schedule"], 75),
    ("00_Admin/Research_Log", ["research log", "research tracker"], 85),

    ("99_Archive", ["archive", "archived", "superseded", "obsolete", "deprecated", "backup", "old version"], 95),
]


@dataclass
class Classification:
    destination: str
    score: int
    reasons: List[str]


def tokenize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower())


def safe_read_text(path: Path, max_chars: int = 50000) -> str:
    suffix = path.suffix.lower()
    try:
        if suffix in TEXT_EXTS:
            return path.read_text(encoding="utf-8", errors="ignore")[:max_chars]
        if suffix in DOCX_EXTS:
            with zipfile.ZipFile(path) as zf:
                try:
                    data = zf.read("word/document.xml").decode("utf-8", errors="ignore")
                    text = re.sub(r"<[^>]+>", " ", data)
                    return text[:max_chars]
                except KeyError:
                    return ""
        if suffix in PDF_EXTS:
            try:
                import pypdf  # type: ignore
                reader = pypdf.PdfReader(str(path))
                parts = []
                for page in reader.pages[:5]:
                    parts.append(page.extract_text() or "")
                return "\n".join(parts)[:max_chars]
            except Exception:
                return ""
    except Exception:
        return ""
    return ""


def score_file(path: Path, repo_root: Path) -> Classification:
    scores: Dict[str, int] = defaultdict(int)
    reasons: Dict[str, List[str]] = defaultdict(list)

    rel = path.relative_to(repo_root).as_posix().lower()
    filename = path.name.lower()
    suffix = path.suffix.lower()
    stem = path.stem.lower()
    text_blob = tokenize(f"{rel} {filename} {stem} {safe_read_text(path)}")

    def add(dest: str, pts: int, reason: str) -> None:
        scores[dest] += pts
        reasons[dest].append(reason)

    # Extension-first heuristics
    if suffix in EMAIL_EXTS:
        add("04_Exhibits/Emails", 85, f"email extension {suffix}")
    if suffix in PHOTO_EXTS:
        add("04_Exhibits/Photos", 90, f"image extension {suffix}")
    if suffix in MEDIA_EXTS:
        add("04_Exhibits/Audio_Video", 90, f"media extension {suffix}")
    if suffix in {".ics", ".vcf"}:
        add("00_Admin/Contacts", 60, f"contact/calendar extension {suffix}")
    if suffix in {".ppt", ".pptx", ".potx", ".potm"} and "template" in text_blob:
        add("11_Templates/Pleadings", 60, "template presentation")
    if suffix in {".dotx", ".dotm", ".xltx", ".xltm"}:
        add("11_Templates/Pleadings", 80, f"template extension {suffix}")

    # Existing folder hint gets modest weight.
    for dest in DESTINATIONS:
        dest_name = dest.lower().replace("_", " ")
        if any(part in text_blob for part in dest_name.split("/")):
            add(dest, 8, f"path/name mentions {dest}")

    for dest, kws, pts in KEYWORDS:
        for kw in kws:
            if kw in text_blob:
                add(dest, pts, f"matched '{kw}'")

    # Special filename rules
    if filename.startswith("exhibit"):
        add("04_Exhibits/Exhibit_Binders", 35, "filename begins with exhibit")
        add("09_Trial/Exhibits", 20, "filename begins with exhibit")
    if re.search(r"\beeoc\b|\bmspb\b|\boig\b|\bgao\b", text_blob):
        add("04_Exhibits/Government_Reports", 25, "government-agency acronym")
    if re.search(r"\bfrcp\b|\blrciv\b|\bfederal rules\b|\blocal rules\b", text_blob):
        add("05_Legal_Authorities/Federal_Rules", 20, "rules reference")
        add("05_Legal_Authorities/Local_Rules", 15, "rules reference")

    if not scores:
        return Classification("98_Needs_Review/Uncertain", 0, ["no confident match"]) 

    destination = max(scores, key=scores.get)
    return Classification(destination, scores[destination], reasons[destination][:8])


def in_managed_tree(path: Path, repo_root: Path) -> bool:
    try:
        first = path.relative_to(repo_root).parts[0]
        return first in REPO_TOP_LEVELS
    except Exception:
        return False


def find_files(repo_root: Path) -> Iterable[Path]:
    for path in repo_root.rglob("*"):
        if path.is_dir():
            if path.name in SKIP_DIR_NAMES:
                # rglob can't prune, but children will be skipped by prefix check below.
                continue
            continue
        if any(part in SKIP_DIR_NAMES for part in path.relative_to(repo_root).parts):
            continue
        if path.name in SKIP_FILE_NAMES:
            continue
        yield path


def git_available(repo_root: Path) -> bool:
    try:
        result = subprocess.run(
            ["git", "-C", str(repo_root), "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode == 0 and result.stdout.strip() == "true"
    except FileNotFoundError:
        return False


def resolve_destination(repo_root: Path, destination: str, source: Path) -> Path:
    base = repo_root / destination
    base.mkdir(parents=True, exist_ok=True)
    target = base / source.name
    if not target.exists():
        return target
    stem = source.stem
    suffix = source.suffix
    i = 2
    while True:
        candidate = base / f"{stem} ({i}){suffix}"
        if not candidate.exists():
            return candidate
        i += 1


def move_file(src: Path, dst: Path, use_git: bool) -> str:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if use_git:
        tracked = subprocess.run(
            ["git", "-C", str(src.parent), "ls-files", "--error-unmatch", str(src)],
            capture_output=True,
            text=True,
            check=False,
        )
        # above relative path may fail across repo, so just try git mv and fallback
        result = subprocess.run(["git", "mv", str(src), str(dst)], capture_output=True, text=True, check=False)
        if result.returncode == 0:
            return "git mv"
    shutil.move(str(src), str(dst))
    return "move"


def main() -> int:
    parser = argparse.ArgumentParser(description="Classify and reorganize files in a legal Git repository.")
    parser.add_argument("repo_root", help="Path to the local clone of the repository")
    parser.add_argument("--min-score", type=int, default=70, help="Minimum score required to auto-move a file")
    parser.add_argument("--apply", action="store_true", help="Actually move files. Without this flag the script performs a dry run.")
    parser.add_argument("--include-managed", action="store_true", help="Also review files already inside the managed legal tree. Default is to only classify files outside the tree.")
    parser.add_argument("--send-uncertain-to-review", action="store_true", help="Move low-confidence files to 98_Needs_Review/Uncertain when --apply is used.")
    parser.add_argument("--report", default="reorg_report.csv", help="CSV report filename written in the repo root")
    parser.add_argument("--json-report", default="reorg_report.json", help="JSON report filename written in the repo root")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).expanduser().resolve()
    if not repo_root.exists() or not repo_root.is_dir():
        print(f"Repository path not found: {repo_root}", file=sys.stderr)
        return 2

    use_git = git_available(repo_root)
    report_rows: List[Dict[str, str]] = []
    summary: Dict[str, int] = defaultdict(int)

    for path in sorted(find_files(repo_root)):
        managed = in_managed_tree(path, repo_root)
        if managed and not args.include_managed:
            continue

        classification = score_file(path, repo_root)
        auto_move = classification.score >= args.min_score
        if not auto_move and not args.send_uncertain_to_review:
            target_rel = ""
            action = "review_only"
            method = ""
        else:
            destination = classification.destination if auto_move else "98_Needs_Review/Uncertain"
            target_path = resolve_destination(repo_root, destination, path)
            target_rel = target_path.relative_to(repo_root).as_posix()
            if target_path == path:
                action = "already_correct"
                method = ""
            elif args.apply:
                method = move_file(path, target_path, use_git)
                action = "moved"
            else:
                action = "would_move"
                method = ""

        report_rows.append(
            {
                "source": path.relative_to(repo_root).as_posix(),
                "predicted_destination": classification.destination,
                "target_path": target_rel,
                "score": str(classification.score),
                "action": action,
                "method": method,
                "reasons": " | ".join(classification.reasons),
            }
        )
        summary[action] += 1

    csv_path = repo_root / args.report
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["source", "predicted_destination", "target_path", "score", "action", "method", "reasons"],
        )
        writer.writeheader()
        writer.writerows(report_rows)

    json_path = repo_root / args.json_report
    json_path.write_text(json.dumps(report_rows, indent=2), encoding="utf-8")

    print("Done.")
    print(f"Git detected: {'yes' if use_git else 'no'}")
    for key in sorted(summary):
        print(f"{key}: {summary[key]}")
    print(f"CSV report:  {csv_path}")
    print(f"JSON report: {json_path}")
    if not args.apply:
        print("Dry run only. Re-run with --apply to move files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
