"""Generate reference pages for the documentation."""

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import mkdocs.config.defaults


SKIPPED_MODULES = ("fastapi_sso.sso", "fastapi_sso")


def generate_reference_pages(docs_dir: str, nav: list):
    """Generate reference pages for the documentation."""
    reference_path = Path(docs_dir, "reference")
    reference_path.mkdir(exist_ok=True)
    source_path = Path("./fastapi_sso")
    reference_nav = []
    for path in sorted(source_path.rglob("*.py")):
        module_path = path.relative_to(".").with_suffix("")
        doc_path = str(path.relative_to(source_path).with_suffix(".md")).replace("/", ".")
        full_doc_path = reference_path / doc_path
        nav_path = (reference_path / doc_path).relative_to(docs_dir).as_posix()

        parts = module_path.parts

        if parts[-1] == "__init__":
            if len(parts) == 1:
                parts = ["fastapi_sso"]
            else:
                parts = parts[:-1]
        elif parts[-1] == "__main__":
            continue

        import_path = ".".join(parts)

        if import_path in SKIPPED_MODULES:
            continue

        full_doc_path.parent.mkdir(exist_ok=True, parents=True)
        with open(full_doc_path, "w", encoding="utf-8") as file:
            file.write(f"::: {import_path}\n")

        reference_nav.append({import_path: Path(nav_path).as_posix()})
    nav.append({"Reference": reference_nav})


def generate_example_pages(docs_dir: str, nav: list):
    """Generate example pages for the documentation."""
    examples_path = Path(docs_dir, "examples.md")
    source_path = Path("./examples")
    examples_path.unlink(missing_ok=True)
    with examples_path.open("w", encoding="utf-8") as file:
        file.write("# Examples\n\n")
        for path in sorted(source_path.rglob("*.py")):
            page_title = path.stem.replace("_", " ").title()
            file.write(f"## {page_title}\n\n```python\n{path.read_text(encoding='utf-8')}\n```\n\n")
    nav.append({"Examples": "examples.md"})


def on_config(config: "mkdocs.config.defaults.MkDocsConfig"):
    """Generate reference pages for the documentation."""
    generate_example_pages(config.docs_dir, config.nav)
    generate_reference_pages(config.docs_dir, config.nav)


# from pathlib import Path

# import mkdocs_gen_files

# nav = mkdocs_gen_files.Nav()

# for path in sorted(Path("./fastapi_sso").rglob("*.py")):
#     module_path = path.relative_to(".").with_suffix("")
#     doc_path = path.relative_to("./fastapi_sso/").with_suffix(".md")
#     full_doc_path = Path("./reference/", doc_path)

#     parts = list(module_path.parts)

#     if parts[-1] == "__init__":
#         parts = parts[:-1]
#     elif parts[-1] == "__main__":
#         continue

#     nav[parts] = Path("./reference", doc_path).as_posix()

#     with mkdocs_gen_files.open(full_doc_path, "w") as fd:
#         identifier = ".".join(parts)
#         print("::: " + identifier, file=fd)
#         print(identifier, parts, doc_path, full_doc_path)

#     mkdocs_gen_files.set_edit_path(full_doc_path, path)

# with mkdocs_gen_files.open("reference.md", "w") as nav_file:
#     nav_file.writelines(nav.build_literate_nav())
