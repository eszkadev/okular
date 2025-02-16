all: install run

install:
	poetry install

run:
	gunicorn -w 2 "okular.main:create_app('$(JENKINS_API)', '$(JOB)')"

routes:
	flask --app "okular.main:create_app('$(JENKINS_API)', '$(JOB)')" routes
