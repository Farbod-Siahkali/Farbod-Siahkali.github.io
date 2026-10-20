#!/bin/sh
# Compile the maintained LaTeX CV; Tectonic handles TeX dependencies.
set -eu
repo_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$repo_dir"
tectonic documents/Academic_CV.tex --outdir files
mv files/Academic_CV.pdf files/Farbod_Siahkali_CV.pdf
