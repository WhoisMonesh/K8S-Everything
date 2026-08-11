# Security Examples

> RBAC, NetworkPolicy, PSA, egress restriction, and CKS hardening.

## Contents
- `network-policy-egress.yaml` — default-deny ingress/egress + allow egress to Redis + DNS, plus a default-deny-all catch-all.  OK
- `pod-security-baseline.yaml` — namespace labeled for Pod Security Admission `baseline`/`restricted`.  OK
- `pod-security-standards.yaml` — Namespace enforcing the `restricted` tier + a compliant Deployment.  OK
- `rbac-rolebinding.yaml` — least-privilege Role + RoleBinding.  OK
- `restrict-egress.yaml` — deny all egress, allow one namespace/service.  OK
- `cks-hardening.yaml` — restricted namespace + hardened Deployment + Kyverno signed-image policy + least-privilege RBAC.  OK

## Usage

```bash
kubectl apply -R -f .          # deploy all in this directory
kubectl apply -f . --dry-run=client   # validate first
kubectl delete -R -f .            # remove
```
