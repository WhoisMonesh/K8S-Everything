# Pod Security Admission (PSA)

> **Category:** Security / Admission

## What It Is

**Pod Security Admission (PSA)** is the built-in Kubernetes admission controller that enforces **pod security standards** (like "must not run as root", "must set capabilities"). It **replaces PodSecurityPolicy (PSP)** which was removed in Kubernetes 1.25.

A pod either passes the namespace-level mode + policy, or it is **rejected**.

## Why It Exists

PSPs were complex, easily bypassed, and created an **RBAC nightmare** (required a PSP *and* RBAC *bindings* to use it). PSA simplifies this into a **namespace-level label** approach.

PSA enforces baseline security **default-deny** without custom resource definitions.

## Three Pod Security Standards (Levels)

| Level | Enforce | What changes |
|-------|---------|--------------|
| `privileged` | Default for legacy / permissive | Allows privileged, host namespace, root, caps |
| `baseline` | Default for restricted namespaces | Baseline / minimized privilege |
| `restricted` | Most strict | Must run as non-root, read-only root FS, drop all caps |

### Example constraints per level

| Rule | `privileged` | `baseline` | `restricted` |
|------|--------------|------------|--------------|
| Run as root allowed? | Yes | No | No (non-root required) |
| `privileged: true` | Yes | No | No |
| Host namespace (PID/IPC) | Yes | No | No |
| HostPath volumes | Yes | Yes | Yes (no, restricted by rules) |
| Capabilities added | Any | Limited set | None / limited |
| Read-only root FS | No | No | Yes (required) |

## Namespace Modes

A namespace labels itself with the mode for each policy type:

```
pod-security.kubernetes.io / <type>: <level>
```

| Label `type` | Enforcement type | Behavior |
|--------------|-----------------|----------|
| `enforce` | Active enforcement | Pods that violate the policy are **rejected** |
| `enforce-version` | Pin the policy version | (Usually latest / `latest`) |
| `audit` | Logged in audit logs | Violation is **logged but allowed** |
| `warn` | Warning in API response | Violation is **warned but allowed** |

### Example Namespace

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: production
  labels:
    # Enforce "restricted" — pods rejected if they violate
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/enforce-version: latest
    # Audit "baseline" too
    pod-security.kubernetes.io/audit: baseline
    pod-security.kubernetes.io/audit-version: v1.28
    # Warn on deprecated/legacy in dev
    pod-security.kubernetes.io/warn: baseline
```

### Three modes to apply:
```
enforce: restricted    # Reject violating pods
audit:     baseline
warn:      baseline
```

The hierarchy is: `enforce` > `audit` > `warn` (audit/warn just log).

## Pod Security Standards (Details)

The three standard levels defined in the upstream [`pod-security-standards`](https://github.com/kubernetes/pod-security-standards) repo:

| Standard | `privileged` | `baseline` | `restricted` |
|----------|--------------|------------|--------------|
| `host-namespaces` | Allowed | Must not share | Must not share |
| `host-network` | Allowed | Must not use | Must not use |
| `host-ports` | Allowed | Restricted (no privileged) | Restricted |
| `host-pid/paths` | Allowed | Must set | Must not share |
| `selinux` | Unrestricted | Must be set | Must be set |
| `run-as-user` | Any | >= 1000 or set | Must be > 1000 |
| `run-as-non-root` | Allowed | Recommended | **Required** (`true`) |
| `run-as-non-root` (image) | Allowed | — | — |
| `se-linux-options` | Any | Must have | Must have |
| `fsGroup` | Any | — | Must be set |
| `supplemental-groups` | Any | — | Must have |
| `read-only-root-filesystem` | Allowed | — | **Required** (`true`) |
| `cap-… / capabilities` | All | Drop dangerous | Drop ALL, add specific |
| `allowPrivilegeEscalation` | Any | Must be false | Must be false |
| `host-path volumes` | All | Check rules | Check rules |
| `host-IPC` | Allowed | No | No |

## Migrating from PodSecurityPolicy (PSP)

| PSP | PSA equivalent | Notes |
|-----|----------------|-------|
| PodSecurityPolicy object | No equivalent object | PSA uses namespace labels instead |
| `privileged` PSP | `enforce: privileged` | Permissive |
| `non-root` PSP | `enforce: baseline` | Blocks root |
| `non-root + read-only` | `enforce: restricted` | Strictest defaults |
| `podSecurityPolicy` RBAC | No RBAC needed | Built-in admission, no per-SAP bindings |

For most teams, `restricted` (with `warn: baseline` for a soft rollout) is the goal.

## Commands

```bash
# Create a namespace with PSA
kubectl create ns restricted-ns
kubectl label ns restricted-ns pod-security.kubernetes.io/enforce=restricted
kubectl label ns restricted-ns pod-security.kubernetes.io/warn=baseline

# Check effective policies
kubectl describe ns restricted-ns      # Labels show the modes

# Try to create a privileged pod (will be rejected under restricted)
kubectl run test --image=nginx --privileged -- sh
# Error from server: ... violated pod spec...

# List namespaces and their policies
kubectl get ns --show-labels | grep pod-security

# Apply mode + version
kubectl label --overwrite ns my-ns \
  pod-security.kubernetes.io/enforce=restricted \
  pod-security.kubernetes.io/enforce-version=latest

# Audit mode — see warnings (doesn't reject)
kubectl apply -f pod.yaml -n audit-mode-ns   # May emit a warning
```

## Common Issues

### "Pod is forbidden" even in dev
```bash
kubectl run test --image=nginx --privileged
# Error: violated: must not be privileged, ...
# Cause: namespace is restricted (enforce: restricted)
# Fix: in dev, set:
# pod-security.kubernetes.io/enforce=baseline
# or: pod-security.kubernetes.io/warn=restricted (allow but warn)
```

### Pods rejected in a new namespace
```bash
# New namespaces created after K8s 1.25 get "privileged" by default
# (no labels = privileged mode)
kubectl label ns my-ns pod-security.kubernetes.io/enforce=baseline
```

### Old cluster still requires PSP
```bash
# PSPs are removed after 1.25
# If using < 1.25: PSPs still required; upgrade to PSA
```

### "runAsNonRoot must be explicitly set" under restricted
```yaml
# Fix: set it explicitly in the securityContext:
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  readOnlyRootFilesystem: true
  capabilities:
    drop: ["ALL"]
```

## Example: Restricted-Compliant Pod

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: restricted-pod
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 10000
    fsGroup: 2000
  containers:
  - name: app
    image: httpd:3
    securityContext:
      runAsNonRoot: true
      runAsUser: 10000
      readOnlyRootFilesystem: true
      allowPrivilegeEscalation: false
      capabilities:
        drop: ["ALL"]
```

## Example: Namespace Policy

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: restricted
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/enforce-version: latest
    pod-security.kubernetes.io/audit: baseline
    pod-security.kubernetes.io/audit-version: latest
    pod-security.kubernetes.io/warn: baseline
    pod-security.kubernetes.io/warn-version: latest
```

## Best Practices

1. **Start namespaces at `baseline`** (or `privileged` in dev), then move to `restricted`
2. **Use `warn` first** — allow violations but log warnings, before enforcing
3. **Pin a version** (`enforce-version: v1.28`) for a controlled rollout
4. **Apply to all namespaces** — including kube-*, or add an exception for system pods
5. **Test workloads** against `restricted` before enforcing
6. **Use admission tooling** (Kyverno/OPA) for anything PSA can't handle (e.g., custom seccomp, image signing)
7. **Don't set `enforce: restricted` on `kube-system`** — system components often need privileged pods (kube-proxy, CNI)
8. **Migrate away from PSP** — it's removed since 1.25
9. **Document** the security posture per namespace (prod vs dev)
10. **Monitor warnings** in audit logs / CI linting tools

## Related Resources

- [Admission Controllers](admission-controllers.md)
- [Secrets](secrets.md)
- [RBAC](rbac.md)
- [Kyverno (alternative)](kyverno.md)
- [OPA Gatekeeper (alternative)](opa-gatekeeper.md)