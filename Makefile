VERSION = $(shell git describe --always)

SRCS = 
SRCS += docs/preface.md
SRCS += docs/introduction.md
SRCS += docs/processor.md
SRCS += docs/instruction-set.md
SRCS += docs/registers.md
SRCS += docs/mode-and-csr.md
SRCS += docs/exception-and-interrupt.md
SRCS += docs/memory-model.md
SRCS += docs/memory-subsystem.md
SRCS += docs/vector.md
SRCS += docs/interruption-controller.md
SRCS += docs/bus-interface.md
SRCS += docs/debug.md
SRCS += docs/performance-monitor.md

SVG_FIGS := $(wildcard docs/figs/*.svg)
PDF_FIGS := $(patsubst docs/figs/%.svg, build/figs/%.pdf, $(SVG_FIGS))

DEPS =
DEPS += resources/meta-vars.lua
DEPS += resources/template.tex

PANDOC_FLAGS += --variable=version:"$(VERSION)"
PANDOC_FLAGS += --from=markdown+table_captions+multiline_tables+grid_tables+header_attributes
PANDOC_FLAGS += --top-level-division=part
PANDOC_FLAGS += --table-of-contents
PANDOC_FLAGS += --number-sections
PANDOC_FLAGS += --pdf-engine=xelatex
PANDOC_FLAGS += --lua-filter=resources/meta-vars.lua
PANDOC_FLAGS += --lua-filter=resources/svg-to-pdf.lua
PANDOC_FLAGS += --lua-filter=resources/remove-md-links.lua
PANDOC_FLAGS += --filter pandoc-crossref
PANDOC_FLAGS += --template=resources/template.tex

all: xiangshan-user-guide.pdf

clean:
	rm -f xiangshan-user-guide.tex xiangshan-user-guide.pdf *.aux *.log *.toc
	rm -rf build

build/figs/%.pdf: docs/figs/%.svg
	mkdir -p build/figs
	rsvg-convert -f pdf -o $@ $<

xiangshan-user-guide.tex: $(SRCS) $(DEPS)
	pandoc $(SRCS) $(PANDOC_FLAGS) -s -o $@
	sed -i 's/@{}//g' $@

xiangshan-user-guide.pdf: xiangshan-user-guide.tex $(PDF_FIGS)
	xelatex $^
	xelatex $^
	xelatex $^

.PHONY: all clean
