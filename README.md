# Okular

Parses and does summary of Jenkins job logs.

#### To install:
Install poetry in your python environment and do  `make install`

#### To run:
`make run`

#### To create container image:
`podman build . --net host --build-arg JENKINS_API=<https://jenkins-instance> --build-arg JOB=<default_jenkins_job>`
