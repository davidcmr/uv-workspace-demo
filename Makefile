dev:
	@uv sync --all-extras --all-packages

lint:
	@uv run mypy libs/ apps/

build:
	@uv build --all-packages --wheel

release: build
	@uv export --frozen --no-dev --no-editable --output-file requirements.txt --all-packages

bundle: release
	@uv pip install \
		-r requirements.txt \
		--find-links dist \
		--no-installer-metadata \
		--no-compile-bytecode \
		--python 3.13 \
		--no-sources \
		--no-cache \
		--target $(target)

zip:
	@echo "Zipping neuralbooru directory..."
	@powershell Compress-Archive -Path neuralbooru -DestinationPath neuralbooru.zip -Force
	@echo "Created neuralbooru.zip"
