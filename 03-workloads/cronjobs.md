# CronJob

> **Category:** Workload / Scheduled Tasks

## What It Is

A **CronJob** creates **Jobs** on a **schedule** (using Cron syntax). It is used for periodic, time-based tasks like log rotation, backup jobs, report generation, and health check jobs.

## Why It Exists

Manual scheduling is error-prone:
- Need a separate scheduler system
- No built-in retry
- Hard to track execution history
- No integration with cluster lifecycle

CronJob provides **Kubernetes-native scheduled jobs** — using standard Cron syntax, with retries, history tracking, and concurrency control.

## Architecture

```mermaid
graph TD
    A[Cron Scheduler<br/>builtin to kube-controller-manager] --> B[CronJob<br/>schedule: */5 * * * *]
    B --> C{Time to run?}
    C -->|Yes| D[Job Created]
    C -->|No| B
    D --> E[Pod 1<br/>backup-script]
    D --> F[Concurrency<br/>Allow | Forbid | Replace]
    E --> G[Succeeded]
```

## CronJob Spec

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: backup-job
spec:
  schedule: "0 2 * * *"        # Cron schedule: daily at 2 AM UTC
  # schedule: "*/5 * * * *"     # Every 5 minutes
  # schedule: "0 9 * * 1-5"     # Weekdays at 9 AM
  concurrencyPolicy: "Forbid"  # Allow | Forbid | Replace (default: Allow)
  suspend: false               # Suspend all jobs (default: false)
  successfulJobsHistoryLimit: 3 # Keep only last 3 successful jobs
  failedJobsHistoryLimit: 5    # Keep only last 5 failed jobs
  startingDeadlineSeconds: 300 # If missed by 5 minutes, still run once
  jobTemplate:                 # Standard Job spec
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: backup-image:1.0
            imagePullPolicy: IfNotPresent
            args:
            - "-mode=backup"
            - "-target=s3://my-backups"
          restartPolicy: OnFailure
```

## Cron Schedule Syntax

Standard Cron format: `minute hour day-of-month month day-of-week`

```text
┌───────────── minute (0 - 59)
│ ┌───────────── hour (0 - 23)
│ │ ┌───────────── day of the month (1 - 31)
│ │ │ ┌───────────── month (1 - 12)
│ │ │ │ ┌───────────── day of the week (0 - 6) (Sunday to Saturday; 0 is also Sunday)
│ │ │ │ │
│ │ │ │ │
│ │ │ │ │
* * * * * <command to execute>
```

### Cron Schedule Examples

| Schedule | Meaning |
|----------|---------|
| `*/5 * * * *` | Every 5 minutes |
| `0 * * * *` | Every hour on the hour |
| `0 9 * * *` | Every day at 9:00 AM |
| `0 2 * * 0` | Every Sunday at 2:00 AM |
| `*/30 * * * *` | Every 30 minutes |
| `0 2 * * 1-5` | Weekdays at 2:00 AM |
| `0 12 1 * *` | 1st of every month at noon |
| `0 0 1 1 *` | Every year on New Year's Day |
| `@hourly` | Every hour (shorthand) |
| `@daily` | Every day (equivalent to `0 0 * * *`) |
| `@weekly` | Every week (equivalent to `0 0 * * 0`) |
| `@monthly` | Every month (equivalent to `0 0 1 * *`) |
| `@yearly` | Every year (equivalent to `0 0 1 1 *`) |

## Concurrency Policies

| Policy | Behavior |
|--------|----------|
| **Allow** (default) | New jobs can start even if the previous one hasn't finished |
| **Forbid** | New job is skipped if the previous is still running |
| **Replace** | New job starts; previous (still running) is killed and replaced |

## Commands

```bash
# Create from a file
kubectl apply -f cronjob.yaml

# Run a quick job immediately (for testing)
kubectl create job --from=cronjob/<name> quick-job-001

# Get
kubectl get cronjob
kubectl get cj                                         # Shortname
kubectl get job -l job-name=<cronjob-name>             # Jobs created by this CronJob

# Describe
kubectl describe cj <name>
kubectl describe job <job-name>

# Check execution history
kubectl get jobs --field-selector=controller-uid=<uid>

# Check last schedule time
kubectl get cj <name> -o jsonpath='{.status.lastScheduleTime}'

# Suspend / resume
kubectl patch cj <name> -p '{"spec":{"suspend":true}}'   # Suspend
kubectl patch cj <name> -p '{"spec":{"suspend":false}}'  # Resume

# Logs from a successful/failed job's pods
kubectl logs job/<job-name>  # latest pod logs from the job

# Delete the CronJob (does NOT delete existing Jobs by default)
kubectl delete cj <name>

# Manually trigger a one-off execution
kubectl create job --from=cronjob/backups backups-manual-001

# Clean up old jobs (manual)
kubectl get jobs -l job-name=backups | grep Completed | awk '{print $1}' | xargs kubectl delete job
```

## CronJob Status

| Field | Description |
|-------|-------------|
| `lastScheduleTime` | When the last job was started |
| `lastSuccessfulTime` | When the last job completed successfully |
| `active` | Currently running (recently created) Jobs |
| `successful` / `failed` | Count of past successful/failed runs |

## Common Issues & Solutions

### CronJob doesn't fire (job not created)
```bash
kubectl describe cj <name>
# Check "Events" — look for:
# - "concurrency policy forbids" (job still running from last schedule)
# - "schedule time in the past" (kube-controller-manager clock issue)

# Check controller-manager logs (on the control-plane node)
# Look for the cronjob controller:
journalctl -u kube-controller-manager | grep -i cronjob

# Check timezone — schedules are in UTC:
kubectl get --raw=/healthz  # or check kube-controller-manager timezone

# Fix: use startingDeadlineSeconds to catch missed runs
```

### Jobs keep failing
```bash
# Check failed jobs and their logs
kubectl get jobs -l job-name=<cronjob-name>
kubectl get pods -l job-name=<job-name>
kubectl describe pod <pod>
kubectl logs <pod>
# Fix: correct the job template in the CronJob
kubectl edit cj <name>
# Then wait for the next schedule
```

### Overlapping jobs
```bash
# If jobs overlap (last one still running when new one starts):
spec:
  concurrencyPolicy: "Forbid"  # Skip if still running
  # OR
  concurrencyPolicy: "Replace"  # Kill the old one
  # OR ensure the schedule gives enough time (e.g., not too frequent)
```

### History grows unbounded
```yaml
# Limit the number of retained jobs:
spec:
  successfulJobsHistoryLimit: 3   # Default: 3
  failedJobsHistoryLimit: 5        # Default: 1
```

### Time zone issues

```bash
# CronJob schedules are evaluated in the kubernetes controller-manager timezone
# By default, this is UTC. To use a local timezone, set TZ (Kubernetes 1.29+):

# In kube-controller-manager manifest (or kube-controller-manager.yaml on kubeadm):
spec:
  containers:
  - name: kube-controller-manager
    env:
    - name: TZ
      value: "America/New_York"
```

## CronJob vs other schedulers

| Tool | Scheduling Precision | Retry | History |
|------|---------------------|-------|---------|
| CronJob | Minute (cron) | ✅ (backoffLimit) | ✅ (successful/failed limits) |
| Airflow | Second (cron-like) | ✅ | ✅ |
| Argo Workflows | Second | ✅ | ✅ |

## Best Practices

1. **Set `startingDeadlineSeconds`** — catch up on missed executions (e.g., `300`)
2. **Set reasonable concurrency policy** — `Forbid` or `Replace`, never leave on `Allow` for long-running jobs
3. **Keep history limited** — set `successfulJobsHistoryLimit` and `failedJobsHistoryLimit`
4. **Test cron syntax** — use an online crontab validator before applying
5. **Run on a schedule with sufficient gap** — so each run can complete before the next
6. **Include monitoring** — use Prometheus metrics or alert on repeated failures
7. **Set `ttlSecondsAfterFinished`** — on the Job template, to auto-clean finished job pods
8. **Use UTC or set TZ** — be consistent about timezones

## Interview Questions

**Q: What is the difference between a CronJob and a Job?**
A: A Job runs once to completion. A CronJob creates Jobs on a recurring schedule (using Cron syntax). Each run of a CronJob is itself a standalone Job.

**Q: What happens if a CronJob execution is missed?**
A: If `startingDeadlineSeconds` is set, the missed job runs immediately. If not set, missed schedules are skipped entirely.

**Q: What are the concurrency policies?**
A: `Allow` (run new alongside existing, default), `Forbid` (skip if previous is running), `Replace` (kill existing and start new).

**Q: How do you trigger a CronJob immediately for testing?**
A: `kubectl create job --from=cronjob/<cronjob-name> <job-name>`.

**Q: How does Kubernetes determine "now" for CronJob scheduling?**
A: CronJobs are scheduled by the kube-controller-manager, based on its local clock (typically UTC).

## Related Resources

- [Job](jobs.md)
- [Scheduling & Autoscaling](../07-scheduling-autoscaling/)
- [CI/CD Overview](../11-ci-cd-gitops/ci-cd.md)
- [kubectl Cheatsheet](../cheat-sheets/kubectl.md)
