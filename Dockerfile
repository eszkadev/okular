FROM python:3.12
WORKDIR /usr/local/okular
RUN mkdir -p /usr/local/var/okular.main-instance

# Install the dependencies
RUN pip install --no-cache-dir poetry

# Copy in the source code
COPY okular ./okular
COPY pyproject.toml .
COPY README.md .

# Install project dependencies
ENV POETRY_VIRTUALENVS_CREATE=false
RUN poetry install

EXPOSE 8000

# Setup an app user so the container doesn't run as the root user
RUN useradd okular
RUN chown okular:users /usr/local/var/okular.main-instance
USER okular

ARG JENKINS_API=
ARG JOB=
ENV JENKINS_API=$JENKINS_API
ENV JOB=$JOB

CMD ["sh", "-c", "gunicorn \"okular.main:create_app('${JENKINS_API}', '${JOB}')\" -b 0.0.0.0"]