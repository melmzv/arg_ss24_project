# If you are new to Makefiles: https://makefiletutorial.com

PAPER := output/paper.pdf
PRESENTATION := output/presentation.pdf

TARGETS :=  $(PAPER) $(PRESENTATION)

# Configs
PULLED_DATA := data/pulled/financial_data.csv
PREPARED_DATA := data/generated/financial_data_prepared.csv
TABLE_1 := data/generated/table_1.pickle
ANALYSIS_RESULTS := output/em_results.pickle

.PHONY: all clean very-clean dist-clean

all: $(TARGETS)

clean:
	rm -f $(TARGETS)

very-clean: clean
	rm -f $(PULLED_DATA) $(PREPARED_DATA) $(TABLE_1) $(ANALYSIS_RESULTS)

dist-clean: very-clean
	rm -f config.csv

$(PAPER): doc/paper.qmd doc/references.bib
	quarto render $< --quiet
	mv doc/paper.pdf output
	rm -f doc/paper.ttt doc/paper.fff

$(PRESENTATION): doc/presentation.qmd doc/beamer_theme_trr266.sty
	quarto render $< --quiet
	mv doc/presentation.pdf output
	rm -rf doc/presentation_files