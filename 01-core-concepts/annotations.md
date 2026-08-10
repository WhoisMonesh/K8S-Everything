# Annotations

> **Category:** Core Concept / Metadata

## What It Is

**Annotations** are key-value pairs attached to Kubernetes objects (Pods, Services, etc.) alongside **Labels**. However, unlike Labels, annotations are **not used for selection** or to group objects — they are used to carry **non-identifying, arbitrary metadata**.

## Why It Exists

Labels are for **grouping and selecting** — they must be low-cardinality, queryable, and structured. But you often need to attach **unstructured, high-cardinality, or large** data:

| Need | Use |
|------|-----|
| Large data (URLs, configs) | Annotations |
| Build IDs, timestamps | Annotations |
| Tool/tooling metadata | Annotations (not Labels) |
| Debug logs, comments | Annotations |

Kubernetes and tooling rely on annotations for:
- Deployment tracking (e.g., "deployment revision")
- Resource monitoring
- External system integration

## Syntax

Same as labels — `key: value`, stored as strings.

```yaml
metadata:
  annotations:
    description: "This description is too long to be a label."
    build-timestamp: "2024-01-23T11:00:00Z"
    checksum/config: "8a3b6b14..."
    kubernetes.io/change-trigger: "configmap/v1"
```

## Annotation Rules

| Rule | Description |
|------|-------------|
| Keys | Same syntax as labels |
| Values | Arbitrary strings (no size limit in the spec, but etcd has practical limits ~1.5 MiB) |
| Queryable | **No** — cannot select/filter by annotations |
| Multi-version | Can change frequently (unlike labels) |
| Use prefix | Prefix for tool-managed annotations (e.g., `my-tool.com/version`) |

## Common Use Cases

### 1. Deployment Metadata

```yaml
metadata:
  annotations:
    kubernetes.io/change-trigger: "configmap/app-config-v2"
    deployment.kubernetes.io/revision: "3"
```

### 2. CI/CD Tracking

```yaml
metadata:
  annotations:
    build.id: "12345"
    build.commit: "a1b2c3d4e5f6"
    built-by: "team-ci"
```

### 3. Documentation & Ownership

```yaml
metadata:
  annotations:
    owner: "team-backend"
    contact: "team-backend@example.com"
    sla: "99.9%"
    description: "Production backend API server"
```

### 4. Tooling

```yaml
metadata:
  annotations:
    # Helm tracks which chart released this object
    meta.helm.sh/release-name: "my-nginx"
    meta.helm.sh/release-namespace: "default"
    # Argo CD tracks sync status
    argocd.argoproj.io/sync-wave: "3"
    # Kubectl last applied
    kubectl.kubernetes.io/last-applied-configuration: |
      {"apiVersion":"apps/v1",...}
```

### 5. External System Integration

```yaml
metadata:
  annotations:
    service.beta.kubernetes.io/aws-Load-balancer-type: "nlb"
    prometheus.io/scrape: "true"
    prometheus.io/port: "9090"
```

## Commands

```bash
# Annotate (imperative)
kubectl annotate pods <name> description="My app pod"
kubectl annotate pods <name> owner=team-a --overwrite
kubectl annotate deployment <name> build-id=12345

# Remove an annotation
kubectl annotate pods <name> description-

# Annotate multiple
kubectl annotate rs,deploy,daemonset newAnnotation=foo

# Get (shown as base64 in raw view, but decoded)
kubectl get pod <name> -o jsonpath='{.metadata.annotations}'
kubectl get pod <name> -o yaml  # annotations visible here

# Filter / describe
kubectl describe pod <name>
```

### Example: View All Annotations

```bash
# List annotations for a resource
kubectl get pod <name> -o yaml | grep -A 5 annotations:
```

### Example: Check CI/CD Metadata

```bash
# Find the build commit for a pod
kubectl get pod <name> -o jsonpath='{.metadata.annotations.build\.commit}'
```

## Built-in Annotations

| Annotation | Purpose | Scope |
|-----------|---------|-------|
| `kubectl.kubernetes.io/last-applied-configuration` | Stores last `kubectl apply` config | All objects |
| `kubernetes.io/change-trigger` | Used by ConfigMap/Secret for rolling updates | ConfigMap, Secret |
| `deployment.kubernetes.io/revision` | Tracks Deployment revision | Deployment, ReplicaSet |
| `meta.helm.sh/release-name` | Helm release tracking | Helm-managed |
| `argocd.argoproj.io/sync-wave` | ArgoCD ordering | ArgoCD-managed |
| `prometheus.io/scrape` | Prometheus scraping toggle | Prometheus |
| `prometheus.io/port` | Prometheus scrape port | Prometheus |
| `prometheus.io/path` | Prometheus scrape path | Prometheus |
| `fluentbit.io/sidecar.*` | Fluent Bit sidecar config | Logging |

## Common Issues & Solutions

### Annotation too large
```yaml
# Avoid storing large blobs (base64 configs) in annotations
annotations:
  config: <very-large-string>  # ❌ Bad
# Use ConfigMaps or Secrets for large data
```

### Change trigger not updating
```bash
# When a ConfigMap changes, pods using it as an env var need restart
# But if mounted as files, add annotation to force reload:
kubectl patch deploy <name> -p '{"spec":{"template":{"metadata":{"annotations":{"configmap-version":"v2"}}}}}'
```

### Annotation key conflicts
```bash
# Use tool prefixes to avoid conflicts (e.g., prometheus.io, argocd.argoproj.io)
# Prefix format: <dns-name>/<key>
```

## Difference: Annotations vs Labels

| Feature | Annotations | Labels |
|---------|-------------|--------|
| **Queryable** | ❌ No | ✅ Yes (selectors) |
| **High cardinality** | ✅ Yes | ❌ No |
| **Large values** | ✅ Yes | ❌ No (63 chars) |
| **Purpose** | Arbitrary metadata | Object identity, grouping |
| **Indexable** | ❌ No | ✅ Yes (efficient) |
| **Filter with `-l`** | ❌ No | ✅ Yes |

## Best Practices

1. **Use annotations for non-queryable metadata** — descriptions, timestamps, build info
2. **Use labels for queryable/selector data** — app, version, tier, env
3. **Use tool-prefixed annotations** — `prometheus.io/`, `argocd.argoproj.io/`, etc.
4. **Keep annotations structured** — key-value pairs, not huge blobs
5. **Use annotations for CI/CD tracking** — build, commit, author info
6. **Avoid large annotations** — prefer ConfigMaps for configuration data
7. **Use change-trigger annotation** — when mounting ConfigMap/Secret as env vars (forces reload on change)

## Interview Questions

**Q: What is the difference between a label and an annotation?**
A: Labels are for selecting/grouping objects (used by Services, Deployments); annotations carry arbitrary metadata that is not queryable. Labels must be low-cardinality and short; annotations can be large and high-cardinality.

**Q: Can you filter resources by annotations?**
A: No. Annotations cannot be used in label selectors (`-l`) or `matchExpressions`. Only labels are queryable.

**Q: What is the `change-trigger` annotation?**
A: The `kubernetes.io/change-trigger` annotation on a ConfigMap/Secret forces an update in Deployment template metadata when the ConfigMap/Secret changes — used for env var consumption that doesn't reload automatically.

**Q: What does the `last-applied-configuration` annotation do?**
A: It stores the raw JSON of the last `kubectl apply` so that subsequent `apply` operations can perform a three-way merge (current + previous + new).

## Related Resources

- [Labels & Selectors](labels-selectors.md)
- [ConfigMap](configmaps.md)
- [Deployment](deployments.md)
- [kubectl Cheatsheet](../cheat-sheets/kubectl.md)
