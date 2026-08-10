# Authoring Helm Charts

> **Category:** Package Management / Helm

## What It Is

A **Helm Chart** is a package that describes a Kubernetes application: its manifests (templates), default config (values), dependencies, and metadata. Authoring charts lets you make your app **installable and configurable** via `helm install`.

## Chart Structure

```
my-app/
├── Chart.yaml          # Metadata
├── values.yaml         # Default values (templates fill these in)
├── charts/             # Sub-charts (dependencies)
├── templates/          # Jinja2-style templates (manifests)
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── configmap.yaml
│   ├── _helpers.tpl        # Shared template helpers (partials)
│   ├── NOTES.txt           # Post-install notes (printed to stdout)
│   └── tests/              # Test manifests (helm test)
└── crds/               # CustomResourceDefinitions (installed first)
```

## Chart.yaml

```yaml
apiVersion: v2          # v2 for Helm 3
name: my-app            # The chart name
description: A Helm chart for my-app
type: application       # or 'library' (for reusable helpers, no manifests)
version: 0.2.0          # Chart version (semver)
appVersion: "1.0.0"     # The app version (used in the image tag)
keywords:
  - web
maintainers:
  - name: me
    email: me@example.com
```

## Templates (the heart)

Templates are ordinary K8s manifests with **Jinja2-style** placeholders `{{ ... }}` and Helm-specific objects.

### Key Helm objects

| Variable | Meaning |
|----------|---------|
| `.Chart` | The Chart.yaml contents |
| `.Values` | The merged values (values.yaml + overrides) |
| `.Release` | The release (`Name`, `Namespace`, `Revision`, `Time`) |
| `.Files` | Access to non-template files in the chart (`Get`, `Glob`) |
| `.Capabilities` | Cluster capabilities (K8s version, enabled APIs) |
| `.Template` | The template path/base |

### Template example

```yaml
# templates/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Release.Name }}-{{ .Chart.Name }}
  labels:
    {{- include "my-app.labels" . | nindent 4 }}
spec:
  replicas: {{ .Values.replicaCount | default 1 }}
  selector:
    matchLabels:
      {{- include "my-app.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels:
        app: {{ .Chart.Name }}
        version: {{ .Chart.AppVersion }}
    spec:
      containers:
      - name: {{ .Chart.Name }}
        image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
        ports:
        - containerPort: {{ .Values.service.port }}
        envFrom:
        - configMapRef:
            name: {{ .Release.Name }}-config
        resources:
          {{- toYaml .Values.resources | nindent 10 }}
```

### `values.yaml`
```yaml
replicaCount: 2
image:
  repository: nginx
  tag: ""                  # defaults to .Chart.AppVersion if empty
service:
  port: 80
resources:
  limits:
    cpu: 200m
    memory: 256Mi
  requests:
    cpu: 100m
    memory: 128Mi
```

## Template Functions & Pipelines

```yaml
# default
tag: {{ .Values.image.tag | default .Chart.AppVersion }}
# quote
name: {{ .Release.Name | quote }}
# nindent (re-indent multi-line YAML — very common)
labels: {{- toYaml .Values.labels | nindent 4 }}
# include a named template
{{- include "my-app.labels" . | nindent 4 }}
# conditional
{{- if .Values.secret.enabled }}
...
{{- end }}
# range over a list
{{- range .Values.extraEnv }}
- name: {{ .name }}
  value: {{ .value | quote }}
{{- end }}
```

## Named Templates & `_helpers.tpl`

A partial reusable template, stored in `templates/_helpers.tpl` (the `_` prefix means it is NOT rendered into a manifest file).

```yaml
# templates/_helpers.tpl
{{- define "my-app.selectorLabels" -}}
app.kubernetes.io/name: {{ .Chart.Name }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}
```

Used in a template:
```yaml
selector:
  matchLabels:
    {{- include "my-app.selectorLabels" . | nindent 8 }}
```

## Conditional Rendering (`include`)

```yaml
{{- if .Values.serviceAccount.create }}
apiVersion: v1
kind: ServiceAccount
metadata:
  name: {{ include "my-app.serviceAccountName" . }}
{{- end }}
```

## Dependencies / sub-charts

`Chart.yaml`:
```yaml
dependencies:
- name: postgresql
  version: "12.x.x"
  repository: https://charts.bitnami.com/bitnami
  condition: postgresql.enabled       # Install only if this value is true
  tags: postgres                      # Group for enabling/disabling by tag
- name: redis
  version: "17.x.x"
  repository: https://charts.bitnami.com/bitnami
  enabled: false
```

Build/update deps:
```bash
helm dependency update ./my-chart
helm dependency build   # Uses charts/ dir + Chart.lock
```

## Tests (`helm test`)

```yaml
# templates/tests/test-ping.yaml
apiVersion: v1
kind: Pod
metadata:
  name: "{{ .Release.Name }}-test"
  annotations:
    "helm.sh/hook": test
spec:
  restartPolicy: Never
  containers:
  - name: curl
    image: curlimages/curl
    command: ["curl", "http://{{ .Release.Name}}.{{ .Release.Namespace }}:80/health"]
```

Run:
```bash
helm test my-release          # Runs hooks tagged test
helm test my-release --logs   # See test pod logs
```

## CRDs (install before templates)

Files in `crds/` are installed **first** and are **not upgraded** by `helm upgrade`:

```
my-chart/
  crds/
    mycrd.example.com_crd.yaml
  templates/
    mycustomresourcedefinition.yaml   # DON'T put CR DS here (it is managed)
```

## NOTES.txt

A message printed after install/upgrade:
```
Your {{ .Chart.Name }} is being installed in namespace {{ .Release.Namespace }}...
To check the pods: kubectl get pods -l app.kubernetes.io/name={{ .Chart.Name }}
```

## Lint & package

```bash
helm lint ./my-chart            # Validate structure + YAML
helm template my ./my-chart     # Render without installing (debug!)
helm package ./my-chart         # Creates my-chart-0.2.0.tgz
helm push my-chart-0.2.0.tgz oci://ghcr.io/org   # Publish to OCI
```

## Best Practices

1. **Use `nindent 4`** to indent multi-line blocks cleanly
2. **Use `{{- ` / ` -}}`** to trim whitespace (leading `{{` + `-` trims preceding; trailing `-` trims following)
3. **Set a `chart-testing` lint** in CI (`ct lint`)
4. **Don't hardcode values** — expose them in `values.yaml`
5. **Use `_helpers.tpl`** for `labels` and `selectorLabels`
6. **Version `Chart.yaml`** — bump chart version on every change
7. **Pin dependency versions** with a `Chart.lock` (via `helm dependency update`)
8. **Test with `helm test`**
9. **Separate CRDs** from templates so they upgrade gracefully
10. **Keep secrets out of templates** — use `.Values` + env injection, not hardcoded

## Interview Questions

**Q: What's the difference between Chart.yaml `version` and `appVersion`?**
A: `version` is the **chart's own version** (for dependency pinning, upgrades). `appVersion` is the **application's version** (the containerized app — e.g., nginx 1.25).

**Q: How do you share a chart across environments (dev/staging/prod)?**
A: Use `values.yaml` for defaults, and pass environment-specific values via `-f prod.yaml` or `--set key=val`. Same chart, different values.

**Q: What does `{{- end }}` do?**
A: The `{{-` (whitespace-trim) removes whitespace before the tag; `-}}` removes after. Keeps rendered YAML clean.

**Q: How do you render a chart without installing?**
A: `helm template <release> <chart>` or `helm install <release> <chart> --dry-run=client`.

**Q: How are sub-charts used?**
A: Declared in `Chart.yaml`'s `dependencies` and vendored into `charts/`. Enable/disable via `tags` or `enabled` flags. Override with `<subchart>.<key>` paths.

## Related Resources

- [helm.md](helm.md)
- [Kustomize](kustomize.md)
