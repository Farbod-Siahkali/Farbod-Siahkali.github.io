# CV and research resume

- `files/Farbod_Siahkali_CV.pdf` is the full academic CV.
- `files/Farbod_Siahkali_Resume.pdf` is the one-page research resume.

The academic CV uses the website's `_pages/cv.md` and
`_data/research_publications.yml`, so public author lists and manuscript statuses
share the same source as the website. Build it with Python, ReportLab, and Ruby:

```sh
python3 scripts/build_academic_cv.py
```

The generator embeds Times New Roman when available on macOS and otherwise uses
standard PDF Times fonts. Visually check every page after regeneration.

Build the separate resume with Tectonic:

```sh
tectonic documents/Research_Resume.tex --outdir files
mv files/Research_Resume.pdf files/Farbod_Siahkali_Resume.pdf
```

The October 2026 versions were checked as three CV pages and one resume page.
The two nonpublic manuscripts use the author's confirmed first-author attribution;
their full collaborator lists have not been supplied.
