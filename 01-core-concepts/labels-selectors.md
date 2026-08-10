# Labels & Selectors

> **Category:** Core Concept
> **Also known as:** Kubernetes Labels, Kubernetes Selectors

## What It Is

**Labels** are key-value pairs attached to Kubernetes objects (like Pods) that are used to **identify and organize** objects. Objects can have the same labels as many other objects, as well as the **same combination of keys and values**.

**Selectors** are the mechanism that uses **labels** to:
- Find (select) a set of objects
- Group objects for services, deployments, replica sets, etc.
- Implement affinity rules and network policies

## Why It Exists

Pods and other K8s objects are dynamic — they come and go. You need a way to:
- Target a group of pods with the **same set of pods** (service discovery)
- **Update** (rollouts) without changing the selector
- **Query** objects by attributes (env, tier, version)
- **Filter** resources for scheduling (node/affinity)

Labels and selectors provide a **declarative addressing mechanism** for grouping and selecting objects.

## Label Syntax

A **label** is a key-value pair:

```
key: value
```

### Key Rules

- Must be 63 characters or fewer (before the optional prefix)
- Must begin and end with an alphanumeric character
- Prefix is optional, separated by `/`
- The prefix is the DNS subdomain (e.g., `example.com/team`)

### Allowed Characters

For **keys**:
- Prefix: `<dns-name>/<key>` (prefix must be a valid DNS subdomain — max 253 chars)
- Name: `[a-z0-9]([A-Z-a-z0-9._-]*)*`

For **values**:
- Must be 63 characters or fewer
- Must begin and end with an alphanumeric character
- Same character rules as keys (no prefix)

### Label Examples

```yaml
metadata:
  labels:
    app: nginx               # "app" is the key, "nginx" is the value
    tier: frontend           # Simple label
    version: v1              # Version label
    environment: production  # Environment label
    team: backend            # Team label (with prefix)
    example.com/owner: alice
```

## Selector Operators

| Operator | Meaning | Example |
|----------|---------|---------|
| `In` | Is one of (plural) | `environment in (production, staging)` |
| `NotIn` | Is NOT one of | `environment notin (dev, test)` |
| `Exists` | Key exists | `key` |
| `DoesNotExist` | Key does NOT exist | `!key` |

## Equality-based vs Set-based Selectors

### Equality-based (`=`)

```yaml
selector:
  matchLabels:
    app: nginx              # app = nginx
```

### Set-based (`In`, `NotIn`, `Exists`)

```yaml
selector:
  matchExpressions:
  - key: environment
    operator: In
    values: [production, staging]    # environment IN (production, staging)
  - key: version
    operator: NotIn
    values: [old, deprecated]
  - key: tier
    operator: Exists                 # tier key exists on object
  - key: deprecated
    operator: DoesNotExist           # deprecated key does NOT exist
```

## matchLabel vs matchExpressions

- `matchLabels` is a map of `{key: value}` — equivalent to a single `matchExpression` with `key: key, operator: In, values: [value]`
- `matchExpressions` is a list of condition objects — all conditions must be satisfied (logical AND)

```yaml
selector:
  matchLabels:              # Simple mapping
    app: nginx
  matchExpressions:        # Complex conditions
  - {key: tier, operator: In, values: [frontend, backend]}
  - {key: version, operator: Exists}
```

## Label Use Cases

### 1. Grouping for Services
```yaml
# Service selects pods with app=web-app
apiVersion: v1
kind: Service
metadata:
  name: web-service
spec:
  selector:
    app: web-app
  ports:
  - port: 80
```

### 2. Deployments & ReplicaSets
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web-app
  template:
    metadata:
      labels:
        app: web-app
```

### 3. Node Selection

```yaml
spec:
  nodeSelector:
    disktype: ssd           # Only schedule on nodes labeled disktype=ssd
    kubernetes.io/hostname: node-2
```

### 4. Network Policies

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-app
spec:
  podSelector:
    matchLabels:
      app: nginx          # Select the pods
  ingress:
  - from:
    - podSelector:
        matchLabels:
          tier: frontend
```

### 5. Kubernetes System Labels

| Label | Managed By | Purpose |
|--------|-----------|----------|
| `kubernetes.io/role` | Control plane | `master` or node role |
| `kubernetes.io/arch` | System | CPU architecture (amd64, arm64) |
| `kubernetes.io/os` | System | OS (linux, windows) |
| `node-role.kubernetes.io/control-plane` | kubeadm | Control plane node |
| `node-role.kubernetes.io/worker` | kubeadm | Worker node |
| `topology.kubernetes.io/zone` | cloud-controller | Availability zone |
| `topology.kubernetes.io/region` | cloud-controller | Region |

## Recommended Labels

The official Kubernetes labels (under `app.kubernetes.io/*` prefix) help tools like Helm manage resources:

```yaml
metadata:
  labels:
    app.kubernetes.io/name: "nginx"              # Name of the app
    app.kubernetes.io/instance: "my-instance"    # Instance name
    app.kubernetes.io/version: "1.25.0"          # App version
    app.kubernetes.io/managed-by: "Helm"         # Management tool
    app.kubernetes.io/component: "web-server"    # Component within app
```

## Common Label Patterns

| Pattern | Usage |
|---------|-------|
| `app: <name>` | Identifies the application |
| `tier: <frontend/backend>` | Functional role |
| `version: <tag>` | Version identifier |
| `environment: <dev/prod>` | Deployment environment |
| `team: <name>` | Owning team |
| `owner: <person>` | Operator identity |

## Commands

```bash
# Add a label (imperative)
kubectl label pods <name> env=production
kubectl label nodes <name> disktype=ssd --overwrite

# Remove a label (trailing dash)
kubectl label pods <name> env-
kubectl label pods <name> 'env-'

# Filter by label
kubectl get pods --selector=env=production
kubectl get pods -l env=production
kubectl get rs -l app=nginx,tier=backend
kubectl get pods -l tier in (frontend,backend) -A

# Match expressions
kubectl get pods -l 'version notin (v1,v2)'
kubectl get nodes -l kubernetes.io/arch=amd64
```

## Common Issues

### Pod not selected by Service
```bash
# Check if labels match
kubectl get pods --show-labels
kubectl describe svc <name>
# Ensure service selector matches exactly
```

### Label with special characters
```bash
# Keys must start with letter, only [a-z0-9._-]
kubectl label pods <name> 'invalid/key=bad'   # ❌ fails
kubectl label pods <name> 'app.kubernetes.io/name=nginx'  # ✅
```

### Too many labels
- Kubernetes does not impose a hard limit, but performance degrades with many
- Recommended: keep labels small and purposeful

## Best Practices

1. **Use DNS-1123** compliant keys for labels (especially with custom prefixes like `example.com/...`)
2. **Follow the recommended labels** (`app.kubernetes.io/*`) for tool interoperability
3. **Use `matchLabels` for simple selectors** — use `matchExpressions` only when set-based matching is needed
4. **Label for identity first** — `app`, `tier`, `version`
5. **Label all resources** — Pods, Services, Deployments, ConfigMaps, etc.
6. **Use structured labels** — prefix custom labels (e.g., `my-company.com/...`)
7. **Don't store high-churn data** in labels — use annotations instead
8. **Use labels to enforce policies** — network policies, resource quotas
9. **Keep selectors minimal** — don't create complex selectors unless necessary

## Difference: Labels vs Annotations

| Feature | Labels | Annotations |
|---------|--------|-------------|
| Queryable | ✅ Yes (selectors) | ❌ No |
| High cardinality | ❌ No | ✅ Yes |
| Multi-purpose | ✅ Structure, identity | ✅ Arbitrary info |
| Max key length | 63 chars | 63 chars |
| Max value size | 63 chars | No limit |
| Purpose | Grouping, selecting | Documentation, non-identity metadata |

## Interview Questions

**Q: How does a Service know which Pods to route traffic to?**
A: A Service uses a **label selector** (`spec.selector`) to find matching Pods. The endpoints controller automatically creates entries in the Service's endpoints for all healthy matching Pods.

**Q: What is the difference between `matchLabels` and `matchExpressions`?**
A: `matchLabels` is a map (key-value pairs) — equivalent to equality-based matching. `matchExpressions` allows set-based matching (`In`, `NotIn`, `Exists`, `DoesNotExist`).

**Q: Can you select pods by their `app` label only?**
A: Yes — `kubectl get pods -l app=my-app`. Both Services and Deployments use selectors.

**Q: Why should you not use high-cardinality labels?**
A: High cardinality (many unique values) causes excessive memory use, degrades performance, and is harder to cache — labels should represent a few stable, well-known dimensions of identity.

## Related Resources

- [Annotations](annotations.md)
- [Service](services.md)
- [Namespace](namespaces.md)
- [Deployment](deployments.md)
- [kubectl Cheatsheet](../cheat-sheets/kubectl.md)
