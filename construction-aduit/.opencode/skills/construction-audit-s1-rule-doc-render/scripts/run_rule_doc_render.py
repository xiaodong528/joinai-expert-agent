#!/usr/bin/env python3
"""
run_rule_doc_render.py - Stage 2 entrypoint for rendering rule_document.docx to rule_doc.md.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore


def friendly_error(message: str) -> int:
    print(f"Error: {message}", file=sys.stderr)
    return 1


def load_config(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ValueError(f"配置文件不存在: {path}")
    if yaml is not None:
        with path.open("r", encoding="utf-8") as file_obj:
            data = yaml.safe_load(file_obj) or {}
    else:  # pragma: no cover
        with path.open("r", encoding="utf-8") as file_obj:
            data = json.load(file_obj)
    if not isinstance(data, dict):
        raise ValueError(f"配置文件格式不正确: {path}")
    return data


def validate_rule_document_config(config: dict[str, Any]) -> tuple[str, Path, Path]:
    audit_id = str(config.get("audit_id", "")).strip()
    if not audit_id:
        raise ValueError("配置缺少 audit_id")

    rule_document = config.get("rule_document")
    if not isinstance(rule_document, dict):
        raise ValueError("配置缺少 rule_document")

    input_docx = str(rule_document.get("path", "")).strip()
    if not input_docx:
        raise ValueError("配置缺少 rule_document.path")

    output_markdown = str(rule_document.get("markdown_path", "")).strip()
    if not output_markdown:
        raise ValueError("配置缺少 rule_document.markdown_path")

    return audit_id, Path(input_docx), Path(output_markdown)


def run_renderer(script_path: Path, input_docx: Path, output_markdown: Path) -> None:
    result = subprocess.run(
        [str(script_path), str(input_docx), str(output_markdown)],
        capture_output=True,
        text=True,
        cwd=Path(__file__).resolve().parents[4],
    )
    if result.returncode != 0:
        raise ValueError((result.stderr or result.stdout).strip() or "规则文档渲染失败")


def emit_success_summary(audit_id: str, input_docx: Path, output_markdown: Path) -> None:
    print(
        f"audit_id={audit_id} "
        f"input_docx={input_docx.resolve()} "
        f"output_markdown={output_markdown.resolve()}"
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render rule_document.docx to rule_doc.md")
    parser.add_argument("--config", required=True, help="Path to audit-config.yaml")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    try:
        config = load_config(Path(args.config))
        audit_id, input_docx, output_markdown = validate_rule_document_config(config)
        script_path = Path(__file__).resolve().parent / "render_rule_doc_markdown.sh"

        run_renderer(script_path, input_docx, output_markdown)

        if not output_markdown.is_file() or output_markdown.stat().st_size == 0:
            return friendly_error(f"Markdown 输出为空: {output_markdown}")

        emit_success_summary(audit_id, input_docx, output_markdown)
        return 0
    except ValueError as exc:
        return friendly_error(str(exc))


if __name__ == "__main__":
    raise SystemExit(main())
