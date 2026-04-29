from pathlib import Path
from html import escape
from datetime import datetime, timezone

REPO_ROOT = Path(__file__).resolve().parents[1]

IGNORE_PARTS = {
    ".git",
    ".github",
    "scripts",
    "__pycache__",
}

IGNORE_FILES = {
    "index.html",
    "README.md",
}

ALLOWED_EXTENSIONS = {
    ".html",
    ".htm",
    ".pdf",
    ".docx",
    ".xlsx",
    ".pptx",
    ".txt",
    ".md",
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".webp",
}


def should_include(path: Path) -> bool:
    rel = path.relative_to(REPO_ROOT)

    if any(part in IGNORE_PARTS for part in rel.parts):
        return False

    if path.name in IGNORE_FILES:
        return False

    if path.suffix.lower() not in ALLOWED_EXTENSIONS:
        return False

    return True


def nice_title(path: Path) -> str:
    name = path.stem.replace("_", " ").replace("-", " ")
    return " ".join(word.capitalize() for word in name.split())


def build_index() -> str:
    files = sorted(
        [p for p in REPO_ROOT.rglob("*") if p.is_file() and should_include(p)],
        key=lambda p: str(p.relative_to(REPO_ROOT)).lower(),
    )

    rows = []

    for file_path in files:
        rel_path = file_path.relative_to(REPO_ROOT).as_posix()
        title = nice_title(file_path)
        size_kb = file_path.stat().st_size / 1024

        rows.append(
            f"""
            <tr>
                <td><a href="{escape(rel_path)}">{escape(title)}</a></td>
                <td>{escape(rel_path)}</td>
                <td>{size_kb:.1f} KB</td>
            </tr>
            """
        )

    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Repository Index</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 40px;
            line-height: 1.5;
            color: #222;
            background: #f7f7f7;
        }}

        main {{
            max-width: 1100px;
            margin: auto;
            background: white;
            padding: 32px;
            border-radius: 12px;
            box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
        }}

        h1 {{
            margin-top: 0;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 24px;
        }}

        th, td {{
            border-bottom: 1px solid #ddd;
            padding: 10px;
            text-align: left;
            vertical-align: top;
        }}

        th {{
            background: #f0f0f0;
        }}

        a {{
            color: #0645ad;
            text-decoration: none;
            font-weight: bold;
        }}

        a:hover {{
            text-decoration: underline;
        }}

        .updated {{
            color: #666;
            font-size: 0.95rem;
        }}
    </style>
</head>
<body>
<main>
    <h1>Repository Index</h1>
    <p class="updated">Automatically updated: {generated}</p>

    <table>
        <thead>
            <tr>
                <th>Title</th>
                <th>Path</th>
                <th>Size</th>
            </tr>
        </thead>
        <tbody>
            {''.join(rows) if rows else '<tr><td colspan="3">No indexed files found.</td></tr>'}
        </tbody>
    </table>
</main>
</body>
</html>
"""


def main() -> None:
    output_path = REPO_ROOT / "index.html"
    output_path.write_text(build_index(), encoding="utf-8")
    print(f"Updated {output_path}")


if __name__ == "__main__":
    main()
