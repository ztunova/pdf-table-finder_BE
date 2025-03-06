format:
	black . --line-length 120

run:
	uvicorn main:app --reload