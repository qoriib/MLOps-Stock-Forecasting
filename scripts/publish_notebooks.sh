#!/usr/bin/env bash
set -euo pipefail

NOTEBOOK_DIR="artifact/notebook"
SUMMARY_FILE="${GITHUB_STEP_SUMMARY:-}"

shopt -s nullglob
notebooks=("$NOTEBOOK_DIR"/ml_pipeline_*.ipynb)

if [ ${#notebooks[@]} -eq 0 ]; then
  echo "No notebooks found in $NOTEBOOK_DIR"
  exit 0
fi

HAS_CML=false
if command -v cml &>/dev/null; then
  HAS_CML=true
else
  echo "[INFO] 'cml' command not found. Image URLs will remain local."
fi

for nb in "${notebooks[@]}"; do
  [ -f "$nb" ] || continue

  stage=$(basename "$nb" .ipynb)
  echo "==> Processing: $stage ($nb)"

  if [ -n "$SUMMARY_FILE" ]; then
    echo "## Processing: $stage" >> "$SUMMARY_FILE"
  fi

  echo "Converting $nb to markdown..."
  poetry run jupyter nbconvert \
    --to markdown \
    --no-input \
    "$nb" \
    --output-dir "$NOTEBOOK_DIR"

  md="$NOTEBOOK_DIR/${stage}.md"
  img_dir="$NOTEBOOK_DIR/${stage}_files"

  if [ -d "$img_dir" ] && [ "$HAS_CML" = true ]; then
    echo "Publishing plots to CML..."
    for img in "$img_dir"/*.png; do
      [ -f "$img" ] || continue
      img_url=$(cml publish "$img")
      filename=$(basename "$img")
      python3 -c "
import pathlib, sys
p = pathlib.Path(sys.argv[1])
p.write_text(p.read_text().replace(sys.argv[2], sys.argv[3]))
" "$md" "${stage}_files/${filename}" "$img_url"
      echo "  Published $filename -> $img_url"
    done
  fi

  if [ -f "$md" ] && [ -n "$SUMMARY_FILE" ]; then
    cat "$md" >> "$SUMMARY_FILE"
    printf "\n\n---\n\n" >> "$SUMMARY_FILE"
    echo "Appended $md to GITHUB_STEP_SUMMARY."
  fi
done

echo "==> Done processing all notebooks."
