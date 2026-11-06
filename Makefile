.PHONY: run test demo
run:
	PYTHONPATH=src python3 -m ops_triage.cli run
test:
	PYTHONPATH=src python3 -m unittest discover -s tests -v
demo:
	PYTHONPATH=src python3 -m ops_triage.cli serve
