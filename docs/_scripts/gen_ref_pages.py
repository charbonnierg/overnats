"""Generate the code reference pages and navigation."""

import sys
from pathlib import Path

import mkdocs_gen_files.nav
import requests

nav = mkdocs_gen_files.nav.Nav()

for path in sorted(Path("src").rglob("*.py")):
    module_path = path.relative_to("src").with_suffix("")
    doc_path = path.relative_to("src").with_suffix(".md")
    full_doc_path = Path("developer/reference", doc_path)

    parts = tuple(module_path.parts)

    if parts[-1] == "__init__":
        parts = parts[:-1]
        doc_path = doc_path.with_name("index.md")
        full_doc_path = full_doc_path.with_name("index.md")
    elif parts[-1] == "__main__":
        continue

    nav[parts] = doc_path.as_posix()

    with mkdocs_gen_files.open(full_doc_path, "w") as fd:
        ident = ".".join(parts)
        fd.write(f"::: {ident}")

    mkdocs_gen_files.set_edit_path(full_doc_path, path)

with mkdocs_gen_files.open("developer/reference/SUMMARY.md", "w") as nav_file:
    nav_file.writelines(nav.build_literate_nav())


with mkdocs_gen_files.open("CHANGELOG.md", "w") as changelog_file:
    changelog = Path("CHANGELOG.md")
    if changelog.is_file():
        changelog_file.write(changelog.read_text())
    else:
        changelog_file.write("No version released yet")


with mkdocs_gen_files.open("LICENSE.md", "w") as license_file:
    LICENSE = "Apache-2.0"
    response = requests.get(
        f"https://raw.githubusercontent.com/spdx/license-list-data/main/text/{LICENSE}.txt",
    )
    data = response.text
    if response.status_code != 200:
        print("Failed to fetch license:", file=sys.stderr)
        print(data, file=sys.stderr)
        sys.exit(1)
    license_file.write(
        data.replace("[yyyy]", "2023").replace(
            "[name of copyright owner]", "Guillaume Charbonnier"
        )
    )


with mkdocs_gen_files.open("index.md", "w") as index_file:
    index = Path("README.md")
    index_content = index.read_text()
    # Rewrite relative links found in README.md
    index_content = index_content.replace(
        "](./tasks.py)",
        "](https://github.com/charbonnierg/genid/blob/next/tasks.py){target=_blank}",
    )
    index_content = index_content.replace(
        "](./setup.cfg)",
        "](https://github.com/charbonnierg/genid/blob/next/setup.cfg){target=_blank}",
    )
    index_content = index_content.replace(
        "](./docs/)",
        "](https://github.com/charbonnierg/genid/blob/next/docs){target=_blank}",
    )
    index_content = index_content.replace(
        "](https://www.pyinvoke.org/)",
        "](https://www.pyinvoke.org/){target=_blank}",
    )
    index_content = index_content.replace(
        "](https://docs.pyinvoke.org/en/stable/getting-started.html#defining-and-running-task-functions)",
        "](https://docs.pyinvoke.org/en/stable/getting-started.html#defining-and-running-task-functions){target=_blank}",
    )
    index_content = index_content.replace(
        "](https://docs.python.org/fr/3/distutils/sourcedist.html)",
        "](https://docs.python.org/fr/3/distutils/sourcedist.html){target=_blank}",
    )
    index_content = index_content.replace(
        "](https://peps.python.org/pep-0427/)",
        "](https://peps.python.org/pep-0427/){target=_blank}",
    )
    index_content = index_content.replace(
        "](https://pip.pypa.io/en/stable/topics/repeatable-installs/#using-a-wheelhouse-aka-installation-bundles)",
        "](https://pip.pypa.io/en/stable/topics/repeatable-installs/#using-a-wheelhouse-aka-installation-bundles){target=_blank}",
    )
    index_content = index_content.replace(
        "](https://mypy.readthedocs.io/en/stable/)",
        "](https://mypy.readthedocs.io/en/stable/){target=_blank}",
    )
    index_content = index_content.replace(
        "](https://flake8.pycqa.org/en/latest/)",
        "](https://flake8.pycqa.org/en/latest/){target=_blank}",
    )
    index_content = index_content.replace(
        "](https://black.readthedocs.io/en/stable/)",
        "](https://black.readthedocs.io/en/stable/){target=_blank}",
    )
    index_content = index_content.replace(
        "](https://isort.readthedocs.io/en/latest/)",
        "](https://isort.readthedocs.io/en/latest/){target=_blank}",
    )
    index_content = index_content.replace(
        "](https://www.conventionalcommits.org/en/v1.0.0/)",
        "](https://www.conventionalcommits.org/en/v1.0.0/){target=_blank}",
    )
    index_content = index_content.replace(
        "](https://github.com/semantic-release/release-notes-generator)",
        "](https://github.com/semantic-release/release-notes-generator){target=_blank}",
    )
    index_content = index_content.replace(
        "](https://www.mkdocs.org/)",
        "](https://www.mkdocs.org/){target=_blank}",
    )
    index_content = index_content.replace(
        "](https://docs.github.com/fr/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax)",
        "](https://docs.github.com/fr/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax){target=_blank}",
    )
    index_file.write(index_content)
