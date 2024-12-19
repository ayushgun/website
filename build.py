from pathlib import Path
import subprocess
from datetime import datetime
import markdown
from bs4 import BeautifulSoup
from pygments.formatters import HtmlFormatter


def render_post(md_path: Path) -> str:
    """Convert raw markdown post content to styled HTML and return as a string."""

    # Read the markdown file
    md_content = md_path.read_text(encoding="utf-8")

    # Convert to HTML using markdown with code highlighting extensions include fenced_code
    # and codehilite for syntax highlighting
    html_body = markdown.markdown(md_content, extensions=["fenced_code", "codehilite"])

    # Create Pygments CSS
    formatter = HtmlFormatter(style="lovelace")
    css_code_highlighting = formatter.get_style_defs(".codehilite")
    css_code_highlighting = css_code_highlighting.replace("bold", "normal")
    css_code_highlighting = css_code_highlighting.replace("italic", "normal")

    # Wrap in an HTML template
    html_template = f"""
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <link rel="stylesheet" href="../../stylesheets/styles.css" />
    <style>
      {css_code_highlighting}
      .codehilite {{ background: transparent; }}
    </style>
    <title>Ayush Gundawar &mdash; Post</title>
  </head>
  <body>
    <div class="container">
      <div class="content">
        {html_body}
      </div>
    </div>
  </body>
</html>
"""

    return html_template


def render_blog() -> None:
    """Render blog.html with entries for all blog posts."""

    md_files = sorted(Path("posts/markdown").rglob("*.md"))

    # Extract post data (title, date, corresponding html file name)
    post_data = []
    for md_file_path in md_files:
        lines = md_file_path.read_text(encoding="utf-8").splitlines()

        # First line: # Title
        # Second line: > Month DD, YYYY
        title_line = lines[0].lstrip("# ").strip()
        date_line = lines[2].lstrip("> ").strip()

        # Corresponding HTML file name
        html_name = md_file_path.with_suffix(".html").name
        post_data.append((title_line, date_line, html_name))

    # Sort posts by date descending (newest first)
    post_data.sort(key=lambda x: datetime.strptime(x[1], "%B %d, %Y"), reverse=True)

    # Modify blog.html
    blog_html_path = Path("blog.html")
    soup = BeautifulSoup(blog_html_path.read_text(encoding="utf-8"), "html.parser")

    # Find the div for post links
    post_links_div = soup.find(id="post-links")
    if post_links_div is None:
        raise RuntimeError("No element with id='post-links' found in blog.html")

    # Clear existing content
    post_links_div.clear()  # type: ignore

    # Add each post
    for title, date_str, html_name in post_data:
        # Create a link to the post
        link_tag = soup.new_tag("a", href=f"posts/html/{html_name}")
        link_tag.string = title
        post_links_div.append(link_tag)

        # Add a blockquote with the date
        date_tag = soup.new_tag("blockquote")
        date_tag.string = date_str
        post_links_div.append(date_tag)

        # Add a line break for spacing
        post_links_div.append(soup.new_tag("br"))

    # Write the updated blog.html
    blog_html_path.write_text(str(soup), encoding="utf-8")


def main() -> None:
    # Ensure output directory exists
    html_output_dir = Path("posts/html")
    html_output_dir.mkdir(parents=True, exist_ok=True)

    md_files = sorted(Path("posts/markdown").rglob("*.md"))

    # Convert each MD to HTML
    for md_file_path in md_files:
        html_content = render_post(md_file_path)
        html_file_path = html_output_dir / md_file_path.with_suffix(".html").name
        html_file_path.write_text(html_content, encoding="utf-8")
        subprocess.run(["prettier", "--write", str(html_file_path)], check=False)

    # Update the blog listing
    render_blog()
    subprocess.run(["prettier", "--write", "blog.html"], check=False)


if __name__ == "__main__":
    main()
