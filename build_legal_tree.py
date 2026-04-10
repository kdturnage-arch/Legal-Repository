from pathlib import Path
from urllib.parse import quote

REPO_ROOT = Path(".").resolve()
REPO_FULL_NAME = "kdturnage-arch/Legal"
BRANCH = "main"
OUTPUT = REPO_ROOT / "legal_tree.html"

IGNORE_DIRS = {".git", "__pycache__", ".venv", "venv", "node_modules"}
IGNORE_FILES = {"legal_tree.html", "repo_contents.md"}

def build_tree(root: Path):
    tree = {}
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root)
        if any(part in IGNORE_DIRS for part in rel.parts):
            continue
        if path.is_file() and path.name not in IGNORE_FILES:
            node = tree
            parts = rel.parts
            for part in parts[:-1]:
                node = node.setdefault(part, {})
            node[parts[-1]] = None
    return tree

def render_node(node, parent=""):
    html = "<ul>\n"
    for name, child in sorted(node.items(), key=lambda x: (x[1] is None, x[0].lower())):
        rel_path = f"{parent}/{name}" if parent else name
        if child is None:
            github_url = f"https://github.com/{REPO_FULL_NAME}/blob/{BRANCH}/{quote(rel_path.replace(chr(92), '/'))}"
            html += f'<li>📄 <a href="{github_url}" target="_blank">{name}</a></li>\n'
        else:
            html += f"<li><details open><summary>📁 {name}</summary>\n"
            html += render_node(child, rel_path)
            html += "</details></li>\n"
    html += "</ul>\n"
    return html

tree = build_tree(REPO_ROOT)

html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Legal Repo Tree</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 20px; }}
h1 {{ margin-bottom: 8px; }}
p {{ margin-top: 0; color: #444; }}
ul {{ list-style-type: none; padding-left: 20px; }}
li {{ margin: 4px 0; }}
a {{ text-decoration: none; }}
a:hover {{ text-decoration: underline; }}
summary {{ cursor: pointer; font-weight: 600; }}
</style>
</head>
<body>
<h1>Legal Repo Tree</h1>
<p>Repository: {REPO_FULL_NAME} | Branch: {BRANCH}</p>
{render_node(tree)}
</body>
</html>
"""

OUTPUT.write_text(html, encoding="utf-8")
print(f"Created: {OUTPUT}")