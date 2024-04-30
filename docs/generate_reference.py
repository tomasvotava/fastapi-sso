"""Generate reference pages for the documentation."""

from pathlib import Path
from typing import TYPE_CHECKING, List, Dict, Union, TypedDict

if TYPE_CHECKING:
    import mkdocs.config.defaults  # pragma: no cover

SKIPPED_MODULES = ("fastapi_sso.sso", "fastapi_sso")

NavItem = Union[str, List[Dict[str, str]]]
Nav = List[Dict[str, NavItem]]


class ConfigType(TypedDict):
    docs_dir: str
    nav: Nav


def generate_reference_pages(docs_dir: str, nav: Nav):
    """Generate reference pages for the documentation."""

    reference_path = Path(docs_dir, "reference")
    reference_path.mkdir(exist_ok=True)

    source_path = Path("./fastapi_sso")
    reference_nav = []

    for path in sorted(source_path.rglob("*.py")):
        module_path = path.relative_to(".").with_suffix("")
        doc_path = str(path.relative_to(
            source_path).with_suffix(".md")).replace("/", ".")
        full_doc_path = reference_path / doc_path
        nav_path = (reference_path / doc_path).relative_to(docs_dir).as_posix()

        parts = module_path.parts
        if parts[-1] == "__init__":
            if len(parts) == 1:
                parts = ("fastapi_sso",)
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


def generate_example_pages(docs_dir: str, nav: Nav):
    """Generate example pages for the documentation."""

    examples_path = Path(docs_dir, "examples.md")
    source_path = Path("./examples")

    examples_path.unlink(missing_ok=True)

    with examples_path.open("w", encoding="utf-8") as file:
        file.write("# Examples\n\n")
        for path in sorted(source_path.rglob("*.py")):
            page_title = path.stem.replace("_", " ").title()
            file.write(
                f"## {page_title}\n\n```python\n{path.read_text(encoding='utf-8')}\n```\n\n")

    nav.append({"Examples": "examples.md"})


def on_config(config: ConfigType):
    """Generate reference pages for the documentation."""

    generate_example_pages(config["docs_dir"], config["nav"])
    generate_reference_pages(config["docs_dir"], config["nav"])
