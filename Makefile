default: blm_headers

dependencies:
	pip install -r requirements.txt

blm_headers:
	python generate_headers.py

clean:
	rm headers/*

.PHONY: dependencies blm_headers
