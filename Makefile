REPO_NAME=movies-notifier
VENV_NAME=.venv
VENV_ACTIVATE=. $(VENV_NAME)/bin/activate
PYTHON=$(VENV_NAME)/bin/python3
DOCKER_TAG=artdgn/$(REPO_NAME)
DOCKER_DATA_ARG=-v $(realpath ./data):/$(REPO_NAME)/data
DOCKER_GDOCS_ARG=-v $(HOME)/.config/gspread_pandas/:/root/.config/gspread_pandas/

venv:
	python3 -m venv $(VENV_NAME)

requirements: venv
	$(VENV_ACTIVATE); \
	pip install -U pip pip-tools; \
	pip-compile requirements.in

install: venv
	$(VENV_ACTIVATE); \
	pip install -r requirements.txt

python:
	@echo $(PYTHON)

build-docker:
	docker build -t $(DOCKER_TAG) .

docker-bash: build-docker
	docker run --rm -it \
	$(DOCKER_DATA_ARG) \
	$(DOCKER_GDOCS_ARG) \
	--entrypoint=bash \
	$(DOCKER_TAG)

# run by specifying ARGS: `make ARGS="-n 100 -ne" docker-run`
docker-run: build-docker
	docker run --rm -it \
	$(DOCKER_DATA_ARG) \
	$(DOCKER_GDOCS_ARG) \
	$(DOCKER_TAG) $(ARGS)
