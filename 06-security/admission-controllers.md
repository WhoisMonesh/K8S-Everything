# Admission Controllers

> **Category:** Security / Admission

## What It Is

An **Admission Controller** is a Kubernetes interceptor that runs **before a resource is persisted** to etcd. It can **validate** (reject/allow) or **mutate** (modify) the request — enforcing cluster-wide rules at creation time.

Admission controllers run during the API request lifecycle:
**Authenticate** -> **Authorize (RBAC)** -> **Admit & Mutate** -> **Persist to etcd**

## Why It Exists

- **Enforce policies** (no privileged pods, enforce image registry, require resources)
- **Default-set fields** (inject sidecars, set default namespace, default resources)
- **Reject misconfigurations** (bad labels, no readiness probe, insecure images)

## Two Phases

| Kind | Runs | Can | Examples |
|------|------|-----|----------|
| **Mutating Admission** | Before validation | **Modify** the request | Set defaults, inject sidecars |
| **Validating Admission** | After mutating | **Accept or reject** the request | Enforce policies (must-have labels) |

## Built-in Admission Controllers

To see which admission plugins are enabled (most distros enable a set on the kube-apiserver):
```bash
kubectl api-resources
# On the apiserver: --enable-admission-plugins=...,NodeRestriction,ServiceAccount,...
```

### Common Built-in Controllers

| Controller | Mutating? | Validates | Purpose |
|------------|-----------|-----------|---------|
| `PodSecurity` | No | Yes | Enforce Pod Security Standards (PSA; replaces PSP) |
| `NamespaceLifecycle` | No | Yes | Prevent deletion of default namespaces; auto-set namespace |
| `ServiceAccount` | Yes | No | Auto-mount a service account token if none specified |
| `NodeRestriction` | No | Yes | Restrict kubelets to modifying only their own Node's resources |
| `PodSecurityPolicy` | Yes | Yes | **(Removed in 1.25)** — use PodSecurity instead |
| `SecurityContextDeny` | Yes | No | Reject certain securityContext fields |
| `ResourceQuota` | No | Yes | Enforce per-namespace resource quotas |
| `DefaultStorageClass` | Yes | No | Set the default StorageClass for unqualified PVCs |
| `MutatingAdmissionWebhook` | Yes | Yes | Calls an external webhook to mutate |
| `ValidatingAdmissionWebhook` | No | Yes | Calls an external webhook to validate |
| `PodTolerationNode` | Yes | Yes | Add NotReady:NoExecute tolerations to pods |

## Admission Webhooks (custom logic)

Two plugin types call **external services** for custom logic:

| Plugin | Mutating? | Validates | Purpose |
|--------|-----------|-----------|---------|
| `MutatingAdmissionWebhook` | Yes | Yes | **Modify** the object before persistence |
| `ValidatingAdmissionWebhook` | No | Yes | Accept or **reject** the object |

### ValidatingAdmissionWebhook CR

```yaml
apiVersion: admissionregistration.k8s.io/v1
kind: ValidatingWebhookConfiguration
metadata:
  name: pod-policy.my-company
webhooks:
- name: pod-policy.my-company.com      # MUST be a qualified domain
  clientConfig:
    service:
      namespace: default
      name: policy-webhook
      path: "/validate/pods"
    caBundle: LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0t...   # base64 CA cert
  rules:
  - apiGroups: [""]
    apiVersions: ["v1"]
    operations: ["CREATE"]
    resources: ["pods"]
  admissionReviewVersions: ["v1"]      # Use v1 (stable)
  sideEffects: None
  failurePolicy: Fail                # Fail (default) or Ignore
```

### Request flow

1. API Server sends an HTTPS `POST` to the webhook's Service (at `/validate/pods`)
2. Payload is an `AdmissionReview` (the object + user + operation)
3. The webhook responds with `allowed: true` or `false`

```go
// Simplified Go handler
func validate(review AdmissionReview) AdmissionResponse {
    pod := review.Request.Object.Object   // The incoming Pod
    if !hasRequiredLabels(pod) {
        return AdmissionResponse{Allowed: false, Reason: "missing required labels"}
    }
    return AdmissionResponse{Allowed: true}
}
```

## Mutating vs Validating Examples

### Mutating: sidecar injection

```yaml
apiVersion: admissionregistration.k8s.io/v1
kind: MutatingWebhookConfiguration
metadata:
  name: sidecar-injector
webhooks:
- name: sidecar.example.com
  clientConfig:
    service:
      name: sidecar-injector
      namespace: sidecar
      path: "/mutate"
  rules:
  - apiGroups: [""]
    apiVersions: ["v1"]
    operations: ["CREATE"]
    resources: ["pods"]
  admissionReviewVersions: ["v1"]
  sideEffects: None
```

### Validating: reject pods without resource limits

```yaml
apiVersion: admissionregistration.k8s.io/v1
kind: ValidatingWebhookConfiguration
metadata:
  name: require-limits
webhooks:
- name: require-limits.example.com
  clientConfig:
    service:
      name: policy
      namespace: policy
      path: "/validate/limits"
  rules:
  - operations: ["CREATE"]
    resources: ["pods"]
```

## Pod Security Admission (PSA)

The **replacement for PodSecurityPolicy** uses an admission controller + a namespace label:
```
pod-security.kubernetes.io/enforce: restricted   # reject
pod-security.kubernetes.io/warn: baseline        # warn-and-allow
```
See [Pod Security Admission](pod-security-admission.md) for details.

## Common Issues

### Webhook timing out / "no endpoints available"
```bash
# The webhook service must be reachable from the API server:
kubectl -n <webhook-ns> get endpoints <webhook-svc>
# Ensure a Pod is running and the Service targets it (label match).
```

### "admission webhook returns 404/500"
```bash
# Check: caBundle is the correct CA for the webhook server cert
# Check: the path and port are correct:
kubectl -n <webhook-ns> get svc <webhook-svc> -o yaml | grep -A2 ports
# Check: the webhook Pod logs:
kubectl -n <webhook-ns> logs <pod>
```

### Webhook blocked by failurePolicy: Fail
```yaml
# If the webhook is down and failurePolicy: Fail, all matching creates are REJECTED.
# Temporarily set failurePolicy: Ignore during rollouts:
failurePolicy: Ignore
```

### "MutatingAdmissionWebhook failed to create pod" (invalid patch)
```bash
# The Mutating webhook returned a patch the API could not apply
# Check: the JSON patch is valid (use a vet tool)
```

### ValidatingWebhook rejecting own pods
```bash
# Exclude the webhook's own namespace:
namespaceSelector:
  matchLabels:
    app: webhook
  matchExpressions:
  - key: app.kubernetes.io/name
    operator: NotIn
    values: ["webhook"]
```

## How to Check Enabled Admission Plugins

```bash
# Describe the kube-apiserver config (kubeadm clusters):
kubectl -n kube-system describe configmap kube-apiserver
# Or check the static pod:
kubectl -n kube-system describe pod kube-apiserver-<node-name>
```

Or on a managed cluster, look for `PodSecurity` (enabled by default on 1.25+).

## Commands

```bash
# List webhook configurations
kubectl get validatingwebhookconfiguration
kubectl get mutatingwebhookconfiguration

# Describe
kubectl describe validatingwebhookconfiguration <name>

# Create / delete
kubectl apply -f webhook.yaml
kubectl delete validatingwebhookconfiguration <name>

# Test (a create that should be rejected):
kubectl apply -f bad-pod.yaml
# Look for "denied by <webhook-name>"
```

## Best Practices

1. **Use failurePolicy: Fail for security-critical validators; Ignore for non-critical**
2. **Scope webhooks by namespaceSelector** — to avoid rejecting system pods (kube-system)
3. **Always set `scope` and `operations` narrowly** — only CREATE / only Pods
4. **Use `sideEffects: None`** — webhooks should be idempotent and side-effect-free
5. **Health check** webhooks must not be blocked by their own rules — use namespaceSelector
6. **Monitor** webhook latency/deny-rate — via API server audit logs
7. **Use `admissionReviewVersions: ["v1"]`** — v1 is stable (v1beta1 was removed in 1.27)
8. **Test in staging** — a broken validating webhook can block cluster operations
9. **Order matters** — mutating webhooks run in the order listed; the final object is what's validated
10. **Keep CA certs updated** — a rotated cert without a matching CA breaks the webhook

## Interview Questions

**Q: What's the difference between a Mutating and a Validating Admission Controller?**
A: A **mutating** controller modifies the request **before** it is stored (e.g., setting defaults, injecting sidecars). A **validating** controller (runs after) accepts or rejects the (possibly mutated) object — it does NOT change it (e.g., enforcing "pods must have labels").

**Q: In what order do admission controllers run?**
A: **Authenticate -> Authorize (RBAC) -> MutatingAdmission -> ValidatingAdmission -> Persistent in etcd**. A mutating webhook runs first and can change the object the subsequent validators see.

**Q: What is Pod Security Admission (PSA)?**
A: It is the **built-in admission controller that enforces the three Kubernetes Pod Security Standards** (privileged, baseline, restricted) — enabled via a namespace label (`pod-security.kubernetes.io/enforce:`). It replaces the removed `PodSecurityPolicy`.

**Q: What happens if a validating webhook returns `allowed: false`?**
A: The API request returns `403 Forbidden` with the webhook's message — the object is rejected and never persisted to etcd.

**Q: What is `failurePolicy`?**
A: Defines what the API server does when a webhook **errors or times out**. `Fail` rejects the request (safe for security webhooks). `Ignore` lets it through (safer for non-critical webhooks).

**Q: What's the difference between a webhook and a built-in controller?**
A: Built-in admission controllers are compiled into the API server. Webhooks delegate to an **external HTTPS service** — more flexible, but you must operate the webhook service (TLS, CA, reliability).

## Related Resources

- [Pod Security Admission](pod-security-admission.md)
- [Kyverno (no-code policy)](kyverno.md)
- [OPA Gatekeeper (rego policy)](opa-gatekeeper.md)
- [RBAC](rbac.md)
- [Pod Security Policy (legacy)](podsecuritypolicy.md)
