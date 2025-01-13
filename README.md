# XiangShan User Guide

![build via pandoc](https://github.com/OpenXiangShan/XiangShan-User-Guide/actions/workflows/build-pandoc.yml/badge.svg)

## Build

We use Pandoc and MkDocs to build the document.

### Pandoc

Pandoc is used to build PDF and single-page HTML documents.

```bash
# Install dependencies
bash ./utils/dependency.sh

# Build
make
```

### MkDocs

MkDocs is used to build and deploy a static website on the internet

```bash
# Install dependencies
pip install -r ./utils/requirements.txt

# Preview the website
mkdocs serve

# Build the website
mkdocs build
```

## LICENSE

This document is licensed under CC BY 4.0.

Copyright © 2024 The XiangShan Team, Beijing Institute of Open Source Chip
