# Helm Hooks

> **Category:** Advanced Patterns

A **Helm hook** is a manifest annotated with `helm.sh/hook: <phase>` that runs **at a specific point** in a release's lifecycle — instead of being a normal, steady-state object. Hooks are how you do **migrations, jobs, and cleanup** around a `helm install`/`upgrade`.

## Hook Lifecycle

| Hook | Fires when | Typical use |
|------|-----------|-------------|
| `pre-install` | after render, before any resource is created | Schema migration, namespace preflight |
| `post-install` | after all resources created | Smoke test, notify |
| `pre-delete` | before release deletion | Backup, cleanup external state |
| `post-delete` | after deletion | Cleanup cloud resources |
| `pre-upgrade` | before an upgrade | **DB migration** (the classic) |
| `post-upgrade` | after upgrade succeeds | Smoke test the new version |
| `pre-rollback` / `post-rollback` | around a rollback | |

## How It Works

Helm renders the manifest **with hook annotations** but stores it only as a hook — it's **not** part of the steady-state manifest that `helm diff`/`helm template` (normal) shows unless you pass `--show-only`. On upgrade, Helm:
1. Creates the hook (usually a `Job`) with a generated name `<release>-<hook>-<random>`.
2. **Waits for the Job to complete** before continuing (unless `--wait` is off).
3. Deletes it (per `hook-delete-policy`) or leaves it per the policy.

### Annotations

```yaml
metadata:
  annotations:
    "helm.sh/hook": pre-upgrade
    "helm.sh/hook-weight": "0"        # lower = runs earlier
    "helm.sh/hook-delete-policy": before-hook-creation   # or hook-succeeded / never
    "helm.sh/hook-delete-timeout": 5m
```

## The DB Migration Hook (the canonical example)

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: schema-migration
  annotations:
    "helm.sh/hook": pre-upgrade
    "helm.sh/hook-weight": "-5"
    "helm.sh/hook-delete-policy": before-hook-creation
spec:
  backoffLimit: 0
  template:
    spec:
      restartPolicy: Never
      containers:
      - name: migrate
        image: myapp:{{ .Chart.AppVersion }}
        command: ["/bin/sh","-c","alembic upgrade head"]
        envFrom:
        - configMapRef:
            name: app-config
```
The hook runs the migration, the Deployment (a normal template) rolls the new image, and the Job is removed before the next run (`before-hook-creation`).

## hook-delete-policy

| Policy | Behavior |
|--------|----------|
| `before-hook-creation` (default) | Delete a prior hook before creating the new one (avoids name collisions). |
| `hook-succeeded` | Delete only if the hook succeeded. |
| `hook-failed` | Delete only if it failed. |
| `none` | Leave the Job forever (use to inspect failures). |

## Common Mistakes

- **Forgetting `backoffLimit: 0` + `restartPolicy: Never`**: the Job can retry forever and never let the upgrade proceed.
- **Putting a `pre-upgrade` hook on a CronJob** without `startingDeadlineSeconds` — the migration can be starved.
- **Not pinning `hook-weight`**: a `post-install` smoke test can race the Service it probes if it runs too early.
- **Running heavy jobs without `--timeout`**: `helm upgrade` waits for hooks; increase `--timeout` if the migration is slow.

## Testing Hooks

- `helm install --dry-run ... ` does **not** run hooks. Use `helm install --wait` for real integration.
- `helm status` lists hooks: `kubectl get jobs,pods -A | grep <release>`.

## Interview Questions

**Q: What is a Helm hook and when do you use it?**
A: A manifest annotated `helm.sh/hook: pre-upgrade` (etc.) that runs at a lifecycle phase, not as steady state. Use it for out-of-band work like DB schema migrations that must complete before the new Deployment rolls out.

**Q: What's the difference between `hook-delete-policy: before-hook-creation` and `hook-succeeded`?**
A: `before-hook-creation` deletes the *previous* hook instance before running the new one (prevents name collisions). `hook-succeeded` deletes the hook only *after it completes successfully*. For migrations you usually want both: `helm.sh/hook-delete-policy: before-hook-creation,hook-succeeded`.

## Related Resources
- [Helm](../10-package-management/helm.md)
- [Application Deployments](../03-workloads/deployments.md)
- [Jobs](../03-workloads/jobs.md)
