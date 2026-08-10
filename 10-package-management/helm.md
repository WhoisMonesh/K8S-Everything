# Helm

> **Category:** Package Management

## What It Is

**Helm** is the package manager for Kubernetes. A **Helm chart** is a versioned bundle of Kubernetes manifests + templating + metadata that describes a deployable unit (an app or a sub-component). The Helm CLI renders the templates (with your values) into a manifest, then applies it.

## Why It Exists

- **Templated manifests** — one chart produces many variants (prod vs dev).
- **Versioning + dependencies** — a chart pins a subchart version (e.g., `redis==12.3.4`).
- **Release lifecycle** — `helm upgrade --atomic` rolls back on failure; `helm rollback` is first-class.
- **Tests** — `helm test` runs `Pod`-based smoke tests as part of a release.

## Architecture

```mermaid
graph TD
    subgraph "You"
        H[Helm CLI\nversion/v3]
        V[values.yaml\nmy overrides]
        C[Chart\ntemplates + Chart.yaml]
    end
    subgraph "Render (client-side)"
        T[helm template\n→ Go templates rendered]
        M[Manifest set]
    end
    subgraph "Cluster"
        R[Helm Release\n(stored as a Secret\nin kube-system by default)] --> K8s
        K8s[API server]
    end
    C --> T
    V --> T
    H --> T
    M --> K8s
    K8s --> R
```

- Helm **does not run a server** in v3 (the old Tiller agent is gone). The CLI renders templates **client-side** and applies via the API — so you can `helm template` to a file and review, or pipe into `kubectl`.
- A release is stored as a **Secret** (by default) named `sh.helm.install/<release-name>` in the release namespace — that's why `helm list` can recover a release if you delete its Pods. The chart + values are inside that Secret.

## Installation

```bash
# Binary (recommended):
curl -fsSL https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
helm version            # v3.x.y

# macOS:
brew install helm

# Linux:
yum install helm        # or the .tar.gz from GitHubReleases
```

## A Chart, Anatomy of

```
my-chart/
  Chart.yaml          # name, version, dependencies
  values.yaml         # default values (the "defaults")
  templates/
    deployment.yaml
    _helpers.tpl      # helper templates
    configmap.yaml
  charts/             # vendored sub-charts (or packaged .tgz)
  tests/              # smoke tests (run via `helm test`)
```

### Chart.yaml

```yaml
apiVersion: v2          # v2 for Helm 3+ (v1 only needed for legacy Tiller)
name: myapp
description: A Helm chart for my app
type: application
version: 1.2.3          # chart version
appVersion: "1.0"       # version of the APP itself (not the chart)
keywords: [web, api]
home: https://example.com
sources:
- https://github.com/example/myapp
maintainers:
- name: ops
  email: ops@example.com
dependencies:           # declare a sub-chart
- name: postgresql
  version: "12.1.0"
  repository: https://charts.bitnami.com/bitnami
```

### values.yaml (defaults)

```yaml
replicaCount: 2
image:
  repository: myapp
  tag: "1.0.0"
  pullPolicy: IfNotPresent
service:
  type: ClusterIP
  port: 80
env:
  LOG_LEVEL: "info"
```

## Go templates in templates/

Helm templates are **Go `text/template`** + Sprig functions. The big gotcha is **quoting + whitespace control**.

### Basic helpers

```gotpl
# {{ .Values }} — the rendered values file
# {{ .Release.Name }} — the release name
# {{ .Chart.Name }} — chart name
# {{ tpl "..." . }} — render a string as a template (recursion)
# {{ include "mychart.labels" . }} — render a named fragment

{{- /* trim whitespace */ -}}   # {{- -}} collapses leading + trailing whitespace
```

### `_helpers.tpl` — the shared-labels pattern

```gotpl
{{- define "myapp.labels" -}}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version | replace "+" "_" }}
app.kubernetes.io/name: {{ .Chart.Name }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}
```
Used in every manifest:
```gotpl
labels:
  {{- include "myapp.labels" . | nindent 4 }}
```

## Values: how the chain works

`helm install -f my-values.yaml --set image.tag=v2 ...`

### Precedence (highest → lowest)

1. `--set` (CLI, last wins on duplicate keys)
2. `--set-string`, `--set-json`, `--set-file`
3. `-f my-values.yaml` (later files override earlier)
4. `values.yaml` (chart defaults / `values.schema.json` defaults)

### `--set` gotchas

```bash
helm install myapp ./my-chart \
  --set image.tag=v2 \
  --set-string env.DEBUG=true \
  --set-file nginx.conf=config/nginx.conf
```
- `--set` is parsed *left-to-right*; a later `--set image.tag=v2` overrides an earlier one.
- `--set` is untyped → `image.tag=1.0` becomes a *string*. Use `--set-json image.tag='"1.0"'` if you need a number, or just don't (Helm handles it).
- For nested maps, `--set env={DEBUG=true,LEVEL=info}` works but is error-prone — prefer a values file.

## Managing Releases

```bash
helm install <release> <chart>        # new release
helm upgrade <release> <chart>        # upgrade in place
  --set image.tag=v2                  # change values
  --atomic                            # roll back on failure
  --timeout 5m                        # wait deadline
  --cleanup-on-fail                 # delete on failure
helm uninstall <release>              # delete (does NOT keep history)
helm list -A                         # all releases
helm status <release>                # current state, manifest hash
helm rollback <release> [revision]    # go back
```

### `--atomic` is your friend

`helm upgrade --atomic` does a `kubectl apply` → wait → on failure does `helm rollback` to the previous revision automatically. Combined with `--wait` and proper **readiness probes**, you get safe rolling upgrades.

## Dependencies

A chart depends on subcharts.

### `dependencies:` + the cache / mirror

```yaml
# Chart.yaml
dependencies:
- name: postgresql
  version: "12.1.0"
  repository: https://charts.bitnami.com/bitnami
- name: common
  version: "1.x"
  repository: https://raw.githubusercontent.com/bitnami/charts/master/bitnami-common
```

```bash
helm dependency update        # pulls the charts/ dir (a local cache ~/.cache)
helm dependency build        # same, but for subcharts already packaged
helm dependency list          # versions resolved
```

- By default subcharts are vendored into `charts/` (committed or CI-built).
- `repository:` is a URL or an **alias** from `--repo` / `HELM_REPOSITORIES_CACHE`.

### Subcharts are isolated

A subchart has its own `values.yaml`. The **parent** passes values via key name:
```yaml
# in the parent values.yaml:
postgresql:
  postgresqlPassword: "secret"
```
The subchart reads `.Values.postgresql.postgresqlPassword`. The parent and child **values are not auto-merged** unless the subchart is designed to (most charts are).

## Hooks (`pre-install`, `post-upgrade`, etc.)

Hooks run at specific points in the release lifecycle and are **NOT** part of the steady-state manifest (they run, then often get cleaned up). They're how you do migrations, DB setup, or schema updates.

```yaml
# templates/migration-job.yaml
{{- if .Release.IsUpgrade }}
apiVersion: batch/v1
kind: Job
metadata:
  name: schema-migration
  annotations:
    "helm.sh/hook": pre-upgrade           # runs BEFORE upgrade
    "helm.sh/hook-delete-policy": before-hook-creation
    "helm.sh/hook-weight": "-5"           # run early
spec:
  template:
    spec:
      containers:
      - name: migrate
        image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
        command: ["/bin/sh", "-c", "alembic upgrade head"]
      restartPolicy: Never
{{- end }}
```

### Hook types

| Annotation | Runs at |
|------------|---------|
| `pre-install` | after template render, before any k8s objects are created |
| `post-install` | after all objects created |
| `pre-delete` | before release deletion |
| `post-delete` | after release deletion |
| `pre-upgrade` | before upgrading (use this for DB migrations!) |
| `post-upgrade` | after upgrade succeeds |
| `pre-rollback` / `post-rollback` | around a rollback |

Use `helm.sh/hook-delete-policy` (`before-hook-creation`, `hook-succeeded`) so you don't accumulate hook Jobs.

## Testing

Helm supports smoke tests via `helm test`. Test pods are defined in `tests/` and annotated as tests:

```yaml
# tests/test-connection.yaml
apiVersion: v1
kind: Pod
metadata:
  name: "{{ include "myapp.fullname" . }}-test-connection"
  labels:
    {{- include "myapp.labels" . | nindent 4 }}
  annotations:
    "helm.sh/hook": test             # ← mark as a test
spec:
  restartPolicy: Never
  containers:
  - name: wget
    image: busybox
    command: ['wget']
    args: ['{{ include "myapp.fullname" . }}:{{ .Values.service.port }}']
```
```bash
helm test <release>
```

## Release History

Every `helm install / upgrade / rollback` creates an **immutable revision** stored in the release Secret (`sh.helm.release.v1.<name>.v<rev>`).

```bash
helm history myapp                 # list revisions
helm show values bitnami/nginx     # dump a chart's default values (great for discovery)
helm get manifest myapp            # the CURRENT rendered manifest
helm get manifest myapp --revision 1
helm get values myapp              # your last values
```

## Common Issues

### "template: ...: function ... not defined"
- You're using `--set` for a function (e.g., `image.tag`) that needs a `tpl` wrap, or you referenced an undefined `include`. Define `{{- define "..." }}` **before** it's used.
- Using chart functions in older-than-3.2 Helm — upgrade the CLI.

### "cannot re-use a share with another cgroup" / Pod stuck creating
Not Helm per se — check `helm status <release>` for the rendered manifest, but the issue is **resource limits** / storage. If a PVC is bound to a fast StorageClass that's full, `helm install` looks "stuck" for minutes while the Pod/container comes up (or `ErrImagePull`, quota, etc.).

### Subchart values not passed through
The parent `values.yaml` key must **exactly** match the subchart's expected key tree. Check the subchart's own `values.yaml` — e.g., `redis.auth.enabled`, `redis.architecture: replication`, etc. Bitnami charts are notoriously nested.

### Hook didn't run / ran too early
- Hook weight ordering: `pre-install` (weight) Job may race the CRD the chart installs.
- If `helm.sh/hook-weight` is missing, hooks run in an undefined order.
- `helm test` failing silently because the test Pod isn't annotated `helm.sh/hook: test`.

### "helm install: cannot re-use" or "already exists"
- Use `--create-namespace`, or the release Secret from a prior partial install is still there. `helm uninstall` then `helm install`, or `helm install --force --replace`.

## Tips & Patterns

- **`helm template` for review**: `helm template myapp . | kubectl apply --dry-run=client -f -` (or server). This validates the rendered manifest without installing.
- **`values.schema.json`**: validate your values before rendering. ChartCI runs the schema too.
- **`Chart.lock`**: commit it so `helm dependency build` is reproducible.
- **Tagging / conditional blocks**: `if .Values.featureX.enabled` is the clean way to toggle whole subtrees — and to avoid rendering unused resources.
- **Immutable tags**: `tag: "1.0.0"` not `latest`. Use `helm upgrade --set image.tag=...` to roll forward. Never `force: true` in `values.yaml` for a prod chart (it deletes/recreates PVCs).

## Interview Questions

**Q: What is a Helm chart and how does templating work?**
A: A chart is a versioned package (Chart.yaml + values.yaml + templates/). Helm renders the Go `text/template` files with the values, producing a manifest set that is applied to the cluster. There's no Helm server in v3 — rendering is client-side.

**Q: What's the difference between `helm install` and `helm upgrade --install` (`-i`)?**
A: `--install` (or `-i`) on `upgrade` is idempotent: it installs if the release doesn't exist, or upgrades if it does. Plain `helm install` fails if a release already exists. In CI the idempotent form is common, but for first-time installs `install` is clearer.

**Q: How are chart dependencies handled, and what are the pitfalls?**
A: `dependencies:` in Chart.yaml (name, version, repository) is resolved by `helm dependency update` which writes a `Chart.lock` and vends the subcharts into `charts/`. Pitfalls: (1) the parent passes values by **exact key path** — nested wrong and the subchart keeps its own default; (2) version **pinning** — use ranges (`~12.3`) then a lock file; (3) transitive dependencies must be in the repo cache or a reachable `repository:` URL.

**Q: How do you do a database migration with Helm without downtime?**
A: A `pre-upgrade` **hook** (`helm.sh/hook: pre-upgrade`) that runs a Job which completes (with backoff) before the main upgrade proceeds. Pair it with `--atomic` and `--wait` so a failed migration rolls back the release. The hook must outlive itself: set `helm.sh/hook-delete-policy: hook-succeeded`.

**Q: What's the difference between a hook and a normal manifest?**
A: A normal manifest is part of the steady-state release and is reconciled/updated each render. A hook (Job/Pod) runs **only** at a lifecycle point (`pre-install`, `post-upgrade`, `test`) and is treated as a one-shot — by default Helm leaves them behind, but with `hook-delete-policy` you control cleanup.

**Q: How does `helm template` help with GitOps?**
A: It renders the chart to a plain manifest **without a cluster** — you can `helm template myapp . > out.yaml` and diff it in a PR, then feed the result into ArgoCD/`kubectl`. It's how you get a code-reviewed, static manifest for an otherwise dynamic chart.

**Q: What does `--atomic` do on `helm upgrade`, and why use it with `--wait`?**
A: `--atomic` makes Helm **automatically roll back** to the prior revision if the upgrade fails (or times out). `--wait` adds "wait for all resources to be Ready" before considering the upgrade successful. Together they make "fail the deploy cleanly" reliable instead of leaving a half-upgraded cluster.

## Related Resources

- [Package Management Overview](README.md)
- [Kustomize](kustomize.md)
- [Application Deployments](../03-workloads/deployments.md)
- [CI/CD](../11-ci-cd-gitops/README.md)
