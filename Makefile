default: blm_headers

dependencies:
	pip install -r requirements.txt

blm_headers:
	./generate_headers.py

clean:
	rm headers/*

.PHONY: dependencies blm_headers
