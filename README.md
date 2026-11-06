# Okular

Parses and does summary of Jenkins job logs.

#### To install:
Install poetry in your python environment and do  `make install`

#### To run:
`make run`

#### To create container image:
`podman build . --net host --build-arg JENKINS_API=<https://jenkins-instance> --build-arg JOB=<default_jenkins_job>`

#### Summary API:
`GET /api/job/<job>/dashboard?date=YYYY-MM-DD&format=<json|prometheus>` returns the dashboard
summary for one day (the `date` parameter defaults to today). Unlike the dashboard page it lists
every failing test, not only the top 10. Without the `format` parameter a client that sends
`Accept: application/json` gets JSON and any other client gets the Prometheus text exposition
format, so a Prometheus scrape target needs no parameter.

`format=json`:

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

`format=prometheus`:

```
# HELP okular_day_builds Number of builds that started on the day.
# TYPE okular_day_builds gauge
okular_day_builds{jenkins_job="online-cypress",date="2026-11-05"} 14
# HELP okular_day_failed_builds Number of builds on the day with at least one failed test.
# TYPE okular_day_failed_builds gauge
okular_day_failed_builds{jenkins_job="online-cypress",date="2026-11-05"} 13
# HELP okular_day_success_rate_percent Percentage of builds on the day without failed tests.
# TYPE okular_day_success_rate_percent gauge
okular_day_success_rate_percent{jenkins_job="online-cypress",date="2026-11-05"} 7
# HELP okular_day_test_failures Number of builds on the day in which the test failed.
# TYPE okular_day_test_failures gauge
okular_day_test_failures{jenkins_job="online-cypress",date="2026-11-05",test="writer/a11y_dialog_spec.js"} 2
```

The success rate sample is left out on a day without builds. The job label is called
`jenkins_job` because Prometheus adds its own `job` label to every scraped sample.
