#!/usr/bin/env bash
set -euo pipefail

if [[ "$#" -ne 2 ]]; then
  echo "Usage: $0 <input.docx> <output.md>" >&2
  exit 1
fi

input_path="$1"
output_path="$2"

if [[ ! -f "$input_path" ]]; then
  echo "Error: input docx not found: $input_path" >&2
  exit 1
fi

if [[ "${input_path##*.}" != "docx" && "${input_path##*.}" != "DOCX" ]]; then
  echo "Error: input must be a .docx file: $input_path" >&2
  exit 1
fi

if ! command -v pandoc >/dev/null 2>&1; then
  echo "Error: pandoc is required to render rule_document.docx to markdown" >&2
  exit 1
fi

mkdir -p "$(dirname "$output_path")"

pandoc \
  --track-changes=all \
  --wrap=none \
  --from=docx \
  --to=gfm \
  "$input_path" \
  -o "$output_path"

if [[ ! -s "$output_path" ]]; then
  echo "Error: markdown output is empty: $output_path" >&2
  exit 1
fi

echo "Wrote $output_path"
