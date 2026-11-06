# Okular

Parses and does summary of Jenkins job logs.

#### To install:
Install poetry in your python environment and do  `make install`

#### To run:
`make run`

#### To create container image:
`podman build . --net host --build-arg JENKINS_API=<https://jenkins-instance> --build-arg JOB=<default_jenkins_job>`

#### JSON API:
`GET /api/job/<job>/dashboard?date=YYYY-MM-DD` returns the dashboard summary for one day
(the `date` parameter defaults to today). Unlike the dashboard page it lists every failing
test, not only the top 10:

```json
{
  "job": "online-cypress",
  "date": "2026-11-05",
  "builds_count": 14,
  "build_fails_count": 13,
  "success_rate": 7,
  "fails": [
    {"test_name": "writer/a11y_dialog_spec.js", "count": 2}
  ]
}
```

`success_rate` is an integer percentage, or `null` when the day has no builds.
