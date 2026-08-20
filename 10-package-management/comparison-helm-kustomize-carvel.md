# Helm vs Kustomize vs Carvel

> **Category:** Package Management / Comparisons
> Decision guide for Kubernetes package management tools.

## Overview

| Feature | Helm | Kustomize | Carvel (kapp + ytt) |
|---------|------|-----------|---------------------|
| **Approach** | Go templates | YAML overlays | Starlark templates |
| **State storage** | Secret in kube-system | ConfigMap in app namespace | ConfigMap in app namespace |
| **Diff** | Limited | Full | Full |
| **Rollback** | `helm rollback` | `kubectl rollout undo` | `kapp undo` |
| **Dependencies** | Subcharts | Overlays | kapp dependency |
| **Learning curve** | Medium | Low | Medium |
| **Community** | Large | Large | Growing |

## When to Use What

### Use Helm When:

- You need a **package manager** with versioning
- You want **pre-built charts** from Bitnami, Prometheus, etc.
- You need **lifecycle management** (install, upgrade, rollback)
- You want **test** support (`helm test`)

```bash
# Example: Install Prometheus with Helm
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install kube-prometheus-stack prometheus-community/kube-prometheus-stack -n monitoring
```

### Use Kustomize When:

- You want **template-free** customization
- You need to **overlay** existing manifests
- You want to **avoid Go template syntax**
- You're using **kubectl** (built-in support)

```bash
# Example: Customize Prometheus with Kustomize
kubectl kustomize overlays/production | kubectl apply -f -
```

### Use Carvel When:

- You want **YAML-first** templating
- You need **schema validation**
- You want **diff** before apply
- You prefer **Starlark** over Go templates

```bash
# Example: Deploy with Carvel
ytt -f manifests/ -v namespace=production | kapp deploy -a my-app -f -
```

## Comparison Matrix

| Criteria | Helm | Kustomize | Carvel |
|----------|------|-----------|--------|
| **Templating** | Go templates | None (overlays) | Starlark |
| **State tracking** | Secret | ConfigMap | ConfigMap |
| **Diff support** | Basic | Full | Full |
| **Schema validation** | JSON Schema | None | Starlark schema |
| **Dependency mgmt** | Subcharts | None | kapp dependency |
| **Test support** | `helm test` | None | None |
| **Rollback** | Built-in | kubectl | kapp undo |
| **Built into kubectl** | No | Yes | No |
| **Popular charts** | Thousands | Few | Few |

## Migration Guide

### Helm to Kustomize

```bash
# Extract manifests from Helm
helm template my-release bitnami/nginx > base/nginx.yaml

# Create kustomization.yaml
cat <<EOF > kustomization.yaml
resources:
- base/nginx.yaml

patchesStrategicMerge:
- overlays/production.yaml
```

### Kustomize to Helm

```bash
# Wrap kustomize output in Helm chart
mkdir -p my-chart/templates
kubectl kustomize . > my-chart/templates/all.yaml

# Add Chart.yaml and values.yaml
```

### Helm to Carvel

```bash
# Extract manifests from Helm
helm template my-release bitnami/nginx > base/nginx.yaml

# Use ytt for templating
ytt -f base/nginx.yaml -v namespace=production | kapp deploy -a my-app -f -
```

## Decision Tree

```
Do you need pre-built charts?
├─ Yes → Helm
└─ No
   ├─ Do you want template-free customization?
   │  ├─ Yes → Kustomize
   │  └─ No
   │     ├─ Do you want YAML-first templating?
   │     │  ├─ Yes → Carvel
   │     │  └─ No → Helm
```

## Best Practices

| Tool | Practice |
|------|----------|
| Helm | Use `--dry-run` before install, review values.yaml |
| Kustomize | Use overlays for environments, base for shared resources |
| Carvel | Use ytt for validation, kapp for deployment tracking |

## Related

- [Helm](helm.md)
- [Kustomize](kustomize.md)
- [Carvel (kapp + ytt)](kapp-ytt.md)
