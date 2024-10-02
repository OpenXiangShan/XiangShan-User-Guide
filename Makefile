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

DEPS =
DEPS += resources/meta-vars.lua
DEPS += resources/template.tex

PANDOC_FLAGS += --from=markdown+table_captions+multiline_tables+grid_tables
PANDOC_FLAGS += --top-level-division=part
PANDOC_FLAGS += --table-of-contents
PANDOC_FLAGS += --number-sections
PANDOC_FLAGS += --pdf-engine=xelatex
PANDOC_FLAGS += --lua-filter=resources/meta-vars.lua
PANDOC_FLAGS += --template=resources/template.tex

all: xiangshan-user-guide.pdf

clean:
	rm -f xiangshan-user-guide.tex

xiangshan-user-guide.tex: $(SRCS) $(DEPS)
	pandoc $(SRCS) $(PANDOC_FLAGS) -s -o $@
	sed -i 's/@{}//g' $@
    
xiangshan-user-guide.pdf: xiangshan-user-guide.tex
	xelatex $^
	xelatex $^
	xelatex $^

.PHONY: all clean
