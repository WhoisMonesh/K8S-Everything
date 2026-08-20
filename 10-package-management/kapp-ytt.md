# Carvel Tools (kapp + ytt)

> **Category:** Package Management / Alternative to Helm

## What It Is

**Carvel** is a suite of tools for Kubernetes application management. **kapp** deploys and manages apps as logical units; **ytt** is a YAML templating tool. Together they provide a Helm alternative with better diff, change tracking, and YAML-first templating.

## Why Use Carvel

| Feature | Helm | Carvel (kapp + ytt) |
|---------|------|---------------------|
| Templating | Go templates | YAML overlays (ytt) |
| State storage | Secret in kube-system | ConfigMap in app namespace |
| Diff | Limited | Full before/after diff |
| Change tracking | helm history | kapp inspect |
| App CRD | No | Yes (logical app unit) |
| Dependencies | Subcharts | kapp dependency |

---

## kapp — Kubernetes Application Manager

### What It Does

- Deploys YAML as a logical **App** (not individual resources)
- Tracks changes between versions
- Shows diff before applying
- Manages dependencies
- Garbage collects removed resources

### Install

```bash
# macOS
brew install kapp

# Linux
curl -L https://carvel.dev/kapp/install.sh | bash

# Go install
go install github.com/carvel-dev/kapp@latest
```

### Basic Usage

```bash
# Deploy app
kapp deploy -a my-app -f manifests/

# Diff before applying
kapp deploy -a my-app -f manifests/ --diff-changes

# Update app
kapp deploy -a my-app -f new-manifests/

# Inspect app
kapp inspect -a my-app

# Delete app
kapp delete -a my-app

# List all apps
kapp list
```

### App CRD

```yaml
apiVersion: kapp.k14s.io/v1alpha1
kind: App
metadata:
  name: my-app
  namespace: production
spec:
  serviceAccountName: kapp-sa
  fetch:
  - http:
      url: https://github.com/my-org/my-app/releases/download/v1.0/manifests.yml
  template:
  - ytt:
      inline:
        pathsFrom:
        - configMapRef:
            name: my-app-values
  deploy:
  - kapp: {}
```

### kapp with Helm

```bash
# Deploy Helm chart via kapp
helm template my-release bitnami/nginx | kapp deploy -a nginx -f -

# Compare Helm versions
helm template my-release bitnami/nginx --version 1.0 | kapp deploy -a nginx -f - --diff-changes
```

---

## ytt — YAML Templating Tool

### What It Does

- Templates YAML with Starlark (Python-like) syntax
- Overlays for modifying existing YAML
- Schema validation
- Data values for input

### Install

```bash
# macOS
brew install ytt

# Linux
curl -L https://carvel.dev/ytt/install.sh | bash

# Go install
go install github.com/carvel-dev/ytt@latest
```

### Basic Usage

```bash
# Template YAML
ytt -f manifests/

# With data values
ytt -f manifests/ -v namespace=production -v replicas=3

# With values file
ytt -f manifests/ -f values.yaml

# Diff
ytt -f manifests/ --diff

# Lint
ytt -f manifests/ --lint
```

### ytt Template Example

```yaml
#@ load("@ytt:data", "data")

apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
  namespace: #@ data.values.namespace
spec:
  replicas: #@ data.values.replicas
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
      - name: app
        image: #@ data.values.image
        ports:
        - containerPort: 8080
        resources:
          requests:
            cpu: #@ data.values.resources.cpu
            memory: #@ data.values.resources.memory
```

### ytt Overlay Example

```yaml
#@ load("@ytt:overlay", "overlay")

#@overlay/match by=overlay.subset({"kind": "Deployment"})
---
spec:
  replicas: 5
  template:
    spec:
      containers:
      #@overlay/match by="name"
      - name: app
        env:
        - name: ENV
          value: production
```

### Data Values

```yaml
#@data/values
---
namespace: default
replicas: 2
image: nginx:latest
resources:
  cpu: 100m
  memory: 128Mi
```

---

## kapp + ytt Combined

```bash
# Template with ytt, deploy with kapp
ytt -f manifests/ -v namespace=production | kapp deploy -a my-app -f -

# With overlay
ytt -f manifests/ -f overlays/production.yaml | kapp deploy -a my-app -f -

# Diff before deploy
ytt -f manifests/ -v namespace=production | kapp deploy -a my-app -f - --diff-changes
```

## Best Practices

1. **Use ytt overlays** instead of Helm's Go templates for cleaner YAML
2. **Use kapp inspect** to see all resources in an app
3. **Use kapp diff** before every deploy
4. **Use App CRD** for complex apps with dependencies
5. **Use data values** for configuration separation

## Related

- [Helm](helm.md)
- [Kustomize](kustomize.md)
- [OCI Artifacts](oci.md)
