import os
import subprocess
from pathlib import Path

import markdown
from bs4 import BeautifulSoup


def convert_md_to_html(md_file_path, html_file_path):
    with open(md_file_path, "r", encoding="utf-8") as md_file:
        md_content = md_file.read()

    html_content = markdown.markdown(
        md_content, extensions=["fenced_code", "codehilite"]
    )

    html_content_wrapped = f"""
<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8" />
    <link href="../../static/styles.css" rel="stylesheet" />
    <link href="../../static/highlights.css" rel="stylesheet" />
  </head>
  <body>
    <div class="centered-div">
        {html_content}
    </div>
  </body>
</html>
"""

    with open(html_file_path, "w", encoding="utf-8") as html_file:
        html_file.write(html_content_wrapped)

    # Format the html file using prettier
    subprocess.run(["prettier", "--write", html_file_path], check=True)


def update_blog_html(md_files_path, html_files):
    with open("blog.html", "r", encoding="utf-8") as blog_file:
        blog_html = blog_file.read()

    soup = BeautifulSoup(blog_html, "html.parser")

    # Clear the content of the div with id post-links
    div = soup.find(id="post-links")
    div.clear()

    # Sort html files by creation time (newest first)
    md_files_path.sort(key=os.path.getmtime, reverse=True)
    sorted_html_files = [Path(file).with_suffix(".html").name for file in md_files_path]

    for html_file in sorted_html_files:
        a = soup.new_tag("a", href=f"posts/html/{html_file}")

        # Remove .html extension and format post's name to title case
        post_name = html_file.replace(".html", "").replace("_", " ").title()
        a.string = post_name
        div.append(a)
        div.append(soup.new_tag("br"))

    with open("blog.html", "w", encoding="utf-8") as blog_file:
        blog_file.write(str(soup))

    # Format the updated blog.html file using prettier
    subprocess.run(["prettier", "--write", "blog.html"], check=True)


def main():
    md_files_path = sorted(Path("posts/markdown").rglob("*.md"))
    html_files = [file.with_suffix(".html").name for file in md_files_path]

    for md_file_path, html_file in zip(md_files_path, html_files):
        html_file_path = Path("posts/html") / html_file
        convert_md_to_html(md_file_path, html_file_path)

    update_blog_html(md_files_path, html_files)


if __name__ == "__main__":
    main()