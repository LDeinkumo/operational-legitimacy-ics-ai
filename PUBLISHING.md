# How to publish this repository

This package is ready to deposit. Two steps give you a citable archive.

1. Version control and host (GitHub, GitLab, or similar).
   From this directory, under your own identity:
     git init
     git add .
     git commit -m "Reproducibility package for the operational-legitimacy shield manuscript"
     git branch -M main
     git remote add origin <your-remote-url>
     git push -u origin main
   Commit under your own name and email so the authorship record is yours.

2. Mint a DOI for citation (Zenodo or figshare).
   Zenodo can archive a GitHub release automatically: connect the repository in
   Zenodo, then publish a release (e.g. v1.0.0). Zenodo issues a DOI for that
   release. Put that DOI (or the repository URL) into the manuscript's Data
   Availability Statement.

Before publishing:
  - Add a LICENSE file (MIT for the code and CC-BY 4.0 for the documentation is a
    sensible default; the choice is yours).
  - Set the license field in CITATION.cff to match.
  - Run `python3 verify_all.py` once in a clean checkout to confirm it prints
    ALL CHECKS PASS on your machine.
