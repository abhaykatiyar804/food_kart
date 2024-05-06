
SCRIPT_PATH = ./scripts


setup:
	@echo "Setting up environment"
	@${SCRIPT_PATH}/setup.sh
lint:
	@echo "Running Linting"
	@${SCRIPT_PATH}/lint.sh

lint-black:
	@echo "Running Linting"
	@${SCRIPT_PATH}/lint-black.sh


coverage:
	@echo "Running Coverage"
	@${SCRIPT_PATH}/coverage.sh

coverage-report:
	@echo "Generating Report"
	@${SCRIPT_PATH}/coverage-report.sh
