# OPA Gatekeeper vs Kyverno vs Kubewarden

> **Category:** Policy Engines / Comparisons
> Decision guide for Kubernetes policy engines.

## Overview

| Feature | OPA Gatekeeper | Kyverno | Kubewarden |
|---------|---------------|---------|------------|
| **Language** | Rego | YAML/JSON | Rego/WASM |
| **Architecture** | Admission controller | Admission controller | Admission controller |
| **Policy as code** | Yes | Yes | Yes |
| **Audit mode** | Yes | Yes | Yes |
| **Audit findings** | Yes | Yes | Yes |
| **CRDs** | ConstraintTemplate | Policy | ClusterAdmissionPolicy |
| **GUI** | Gatekeeper Policy Admin | Kyverno Policy Reporter | Kubewarden Dashboard |
| **Complexity** | High | Low | Medium |

## When to Use What

### Use OPA Gatekeeper When:

- You need **fine-grained control** with Rego
- You have **complex policy logic**
- You want **enterprise-grade** policy engine
- You need **OPA ecosystem** integration

```yaml
# Example: OPA Gatekeeper constraint template
apiVersion: templates.gatekeeper.sh/v1
kind: ConstraintTemplate
metadata:
  name: k8srequiredlabels
spec:
  crd:
    spec:
      names:
        kind: K8sRequiredLabels
      validation:
        openAPIV3Schema:
          type: object
          properties:
            labels:
              type: array
              items:
                type: string
  targets:
    - target: admission.k8s.gatekeeper.sh
      rego: |
        package k8srequiredlabels
        violation[{"msg": msg}] {
          provided := {label | input.review.object.metadata.labels[label]}
          required := {label | label := input.parameters.labels[_]}
          missing := required - provided
          count(missing) > 0
          msg := sprintf("Missing required labels: %v", [missing])
        }
```

### Use Kyverno When:

- You want **YAML-native** policies
- You need **simple syntax** (no Rego)
- You want **built-in validations** (300+)
- You need **mutating policies**

```yaml
# Example: Kyverno require labels
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-labels
spec:
  validationFailureAction: Enforce
  rules:
  - name: check-for-labels
    match:
      any:
      - resources:
          kinds:
          - Pod
    validate:
      message: "The label 'app' is required."
      pattern:
        metadata:
          labels:
            app: "?*"
```

### Use Kubewarden When:

- You want **WASM policies** (language-agnostic)
- You need **multi-language** support (Rego, Python, Go)
- You want **strong isolation** between policies
- You need **policy distribution** via OCI

```yaml
# Example: Kubewarden policy
apiVersion: policies.kubewarden.io/v1
kind: ClusterAdmissionPolicy
metadata:
  name: require-labels
spec:
  module: registry://ghcr.io/kubewarden/policies/require-labels:v0.1.0
  rules:
  - apiGroups: [""]
    apiVersions: ["v1"]
    resources: ["pods"]
  settings:
    labels:
    - "app"
```

## Comparison Matrix

| Criteria | OPA Gatekeeper | Kyverno | Kubewarden |
|----------|---------------|---------|------------|
| **Learning curve** | High (Rego) | Low (YAML) | Medium |
| **Policy language** | Rego | YAML | Rego/WASM |
| **Policy distribution** | Git | Git | OCI registry |
| **Audit findings** | Yes | Yes | Yes |
| **Mutation support** | Limited | Full | Limited |
| **CEL support** | No | Yes | No |
| **GUI** | Basic | Good | Good |
| **Community** | Large | Large | Growing |

## Decision Tree

```
Do you need fine-grained control with Rego?
├─ Yes → OPA Gatekeeper
└─ No
   ├─ Do you want YAML-native policies?
   │  ├─ Yes → Kyverno
   │  └─ No
   │     ├─ Do you need WASM/multi-language?
   │     │  ├─ Yes → Kubewarden
   │     │  └─ No → Kyverno (default)
```

## Migration Guide

### OPA Gatekeeper to Kyverno

```yaml
# Gatekeeper: Require labels
apiVersion: templates.gatekeeper.sh/v1
kind: ConstraintTemplate
metadata:
  name: k8srequiredlabels
spec:
  crd:
    spec:
      names:
        kind: K8sRequiredLabels
  targets:
    - target: admission.k8s.gatekeeper.sh
      rego: |
        package k8srequiredlabels
        violation[{"msg": msg}] {
          required := {label | label := input.parameters.labels[_]}
          provided := {label | input.review.object.metadata.labels[label]}
          missing := required - provided
          count(missing) > 0
          msg := sprintf("Missing required labels: %v", [missing])
        }

# Kyverno equivalent
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-labels
spec:
  validationFailureAction: Enforce
  rules:
  - name: check-for-labels
    match:
      any:
      - resources:
          kinds:
          - Pod
    validate:
      message: "The label 'app' is required."
      pattern:
        metadata:
          labels:
            app: "?*"
```

### Kyverno to OPA Gatekeeper

```yaml
# Kyverno: Require labels
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-labels
spec:
  validationFailureAction: Enforce
  rules:
  - name: check-for-labels
    match:
      any:
      - resources:
          kinds:
          - Pod
    validate:
      message: "The label 'app' is required."
      pattern:
        metadata:
          labels:
            app: "?*"

# Gatekeeper equivalent
apiVersion: templates.gatekeeper.sh/v1
kind: ConstraintTemplate
metadata:
  name: k8srequiredlabels
spec:
  crd:
    spec:
      names:
        kind: K8sRequiredLabels
  targets:
    - target: admission.k8s.gatekeeper.sh
      rego: |
        package k8srequiredlabels
        violation[{"msg": msg}] {
          required := {label | label := input.parameters.labels[_]}
          provided := {label | input.review.object.metadata.labels[label]}
          missing := required - provided
          count(missing) > 0
          msg := sprintf("Missing required labels: %v", [missing])
        }
```

## Best Practices

| Engine | Practice |
|--------|----------|
| OPA Gatekeeper | Use `audit` mode first, then `enforce` |
| Kyverno | Use `validationFailureAction: Audit` for testing |
| Kubewarden | Use `policyMode: Protect` for enforcement |

## Related

- [OPA Gatekeeper](../06-security/opa-gatekeeper.md)
- [Kyverno](../06-security/kyverno.md)
- [Kubewarden](../06-security/kubewarden.md)
- [Policy as Code](../06-security/policy-as-code.md)
