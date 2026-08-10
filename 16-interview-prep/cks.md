# CKS — Certified Kubernetes Security Specialist

> **Category:** Certification

## Exam At-a-Glance

| Item | Value |
|------|-------|
| Provider | CNCF |
| Duration | 75 minutes |
| Questions | ~10–12 performance-based tasks |
| Passing score | 66% |
| Prerequisite | **CKA earned first** (CNCF enforces this) |
| Allowed docs | `kubernetes.io/docs`, `kubernetes.io/blog`, `github.com/kubernetes/*` |
| Result time | ~72 hours |

## Domain Breakdown

| Domain | Weight | What it covers |
|--------|--------|----------------|
| **Cluster Architecture, Installation & Configuration** | 18% | Secure control-plane install, CIS Benchmarks, kubeadm hardening |
| **Cluster Domain & Endpoint Security** | 15% | Ingress/Egress NetworkPolicies, kube-bench, service accounts, RBAC |
| **Cluster Hardening** | 21% | Restrict kube-system access, PodSecurityAdmission, least-privilege RBAC, seccomp/AppArmor, removing AlwaysAllow |
| **Network Security** | 7% | Egress deny-by-default, NetworkPolicies with egress |
| **Security & Supply Chain** | 11% | ImagePolicyWebhook, image signing (cosign/notation), SBOM, registry auth |
| **Security Monitoring & Runtime Security** | 13% | Audit logging, Falco, runtime policies |

21% hardening + 13% runtime = the biggest chunks. These require writing **deny-by-default** policies, not allow rules.

## Secure Cluster Install (kubeadm, CKS-style)

### 1. CIS Benchmark profile
```bash
kubeadm config images pull
sudo kubeadm init \
  --pod-network-cidr=10.244.0.0/16 \
  --apiserver-cert-extra-sans=$(hostname -i) \
  --cri-socket=/var/run/containerd/containerd.sock
# Then label namespaces for PodSecurityAdmission.
```

### 2. Lock down the API server
In `/etc/kubernetes/manifests/kube-apiserver.yaml`:
```yaml
spec:
  containers:
  - command:
    - kube-apiserver
    - --authorization-mode=Node,RBAC
    - --anonymous-auth=false
    - --audit-log-path=/var/log/apiserver-audit.log
    - --audit-policy-file=/etc/kubernetes/audit-policy.yaml
    - --service-account-issuer=https://kubernetes.default.svc
    - --service-account-key-file=/etc/kubernetes/pki/sa.pub
    - --service-account-signing-key-file=/etc/kubernetes/pki/sa.key
```

### 3. PodSecurityAdmission — deny privileged by default
```bash
kubectl label namespace kube-system pod-security.kubernetes.io/enforce=baseline
kubectl label namespace kube-system pod-security.kubernetes.io/enforce-version=latest
```

## NetworkPolicies (the CKS bread-and-butter)

The classic task: **deny all egress, allow only to one service in another namespace.**

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all-egress
  namespace: my-app
spec:
  podSelector: {}                 # every Pod in this namespace
  policyTypes:
  - Egress                       # only egress is denied
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-api-egress
  namespace: my-app
spec:
  podSelector: {}
  policyTypes:
  - Egress
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: infra
    - podSelector:
        matchLabels:
          app: payment-api
    ports:
    - protocol: TCP
      port: 443
```

NetworkPolicies can't match DNS names. For external egress, use an `ipBlock` with a resolved CIDR, or rely on a CNI that supports DNS-based policies (Cilium).

### Debugging a silent NetworkPolicy drop
```bash
kubectl get networkpolicy -A
kubectl describe networkpolicy <np> -n <ns>
kubectl describe pod <p> | grep Policy    # which policies select this pod
```

## RBAC Hardening

Grant the fewest verbs, scoped to a namespace when possible:
```yaml
kind: Role                      # NOT ClusterRole, unless necessary
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  namespace: my-app
  name: pod-reader
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list", "watch"]     # least privilege
---
kind: RoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: read-pods
  namespace: my-app
subjects:
- kind: ServiceAccount
  name: my-sa
  namespace: my-app
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io

## Container Security & Image Signing

### seccomp + AppArmor (runtime hardening)
```yaml
securityContext:
  seccompProfile:
    type: RuntimeDefault          # blocks dangerous syscalls
  runAsNonRoot: true
  runAsUser: 10001                # do NOT be root
  readOnlyRootFilesystem: true
```
Apply cluster-wide via PodSecurityAdmission (`baseline` enables `RuntimeDefault` automatically).

### Image signature / verification
Use **cosign** or **notation** + a policy controller. The CNCF `policy-controller` (Kyverno) or Harbor's admission chart rejects unsigned images:
```bash
cosign sign --key cosign.key ghcr.io/myorg/app:v1.2.3
cosign verify --key cosign.pub ghcr.io/myorg/app:v1.2.3
```

### SBOM + image scanning (supply chain)
```bash
# Generate a Software Bill of Materials:
syft <image>:tag -o spdx-json > sbom.json
# Scan for CVEs:
grype sbom:./sbom.json
# Or scan the image directly:
grype <image>:tag
```

## Audit Logging

Write a policy to `/etc/kubernetes/audit-policy.yaml`:
```yaml
apiVersion: audit.k8s.io/v1
kind: Policy
rules:
- level: Metadata                       # log request + response metadata only
  resources:
  - group: ""
    resources: ["secrets", "configmaps"]
- level: RequestResponse
  users: ["system:serviceaccount:kube-system:token-controller"]
```
Then in the API server manifest:
- `--audit-policy-file=/etc/kubernetes/audit-policy.yaml`
- `--audit-log-path=/var/log/apiserver-audit.log`
- `--audit-log-maxage=10` `--audit-log-maxbackup=3` `--audit-log-maxsize=100`

## Runtime Security (Falco)

Falco watches the kernel (via eBPF or ptrace) for **anomalous behavior**: exec in a container, outbound over non-standard ports, file writes to `/etc/shadow`. Install it as a DaemonSet; configure rules to alert to SIEM/webhook.

### CKS exam tip: audit vs. runtime
- **Audit logging** = *who* called the API and *what* object. (API plane.)
- **Falco / Kyverno** = *what the container process actually did*. (Node plane.)

## Common Issues

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `kubectl auth can-i` returns `yes` as admin but a workload still 403s | The workload's SA lacks the RoleBinding | `kubectl auth can-i X --as=system:serviceaccount:ns:sa` |
| NetworkPolicy denies legit traffic | A *deny-all* policy was added, flipping the default to deny | Add an allow rule (or a `0.0.0.0/0` egress if egress is intended) |
| Image pull fails with `401` | Missing/mis-typed `imagePullSecret`, or `docker-registry` secret of the wrong type | Re-create as `kubernetes.io/dockerconfigjson` |
| Pod stays `Pending: cannot find` `RuntimeClass` | The feature gate or the RuntimeClass wasn't defined | `kubectl get runtimeclass` / add it before deploying |

## Exam Tactics

1. **NetworkPolicy tasks** almost always need two objects — a deny-all, then a narrow allow. Order matters; create the allow *before* the deny to avoid a race where you lock yourself out.
2. **RBAC tasks** need a Subject (SA/User/Group) + Role/ClusterRole + RoleBinding/ClusterRoleBinding. Double-check the Subject's `namespace`.
3. **Image signing / policy** — you usually only need `kubectl apply -f` the policy; you rarely have cosign installed. Prefer YAML-based admission (Kyverno) over runtime CLI.
4. **Time** — RBAC + NetworkPolicy + image policy are ~3 quick wins; use them to bank points early.

## Interview Questions (CKS-flavored)

**Q: How does Kubernetes RBAC prevent a Pod from `get`ing secrets?**
A: First, the API server authenticates the caller (via the Pod's ServiceAccount token). Then it checks RBAC: does a Role/ClusterRole with `get` on `secrets` exist, bound (via RoleBinding/ClusterRoleBinding) to that SA in that namespace? If not, the request is denied — even if the image runs as root. You can verify with `kubectl auth can-i get secrets --as=system:serviceaccount:ns:sa`.

**Q: What does a `NetworkPolicy` with `policyTypes: [Egress]` and an empty `egress:` list do?**
A: It **denies all egress** from Pods matching `podSelector` (default-deny egress). That's the CKS "lock it down first, then allow specific traffic" pattern.

**Q: What is the difference between a Secret and the etcd encryption at rest?**
A: A Secret is **base64-encoded** (that's encoding, not encryption — anyone with cluster read access can decode it). etcd **encryption at rest** (`EncryptionConfiguration` + `--encryption-provider-config` on the API server) encrypts the *stored* value of Secrets (and others) under a KMS key, so even a stolen etcd backup stays encrypted. You enable it via the `EncryptionConfiguration` file referenced by the API server.

**Q: How does a container end up with a seccomp profile of `RuntimeDefault`?**
A: The Pod/Container `securityContext.seccompProfile.type = RuntimeDefault`, **or** the PodSecurityAdmission `baseline` policy which sets it for you automatically. The runtime then applies its pre-defined profile (drops `ptrace`, `mounts`, etc.) without you specifying the profile path.

**Q: Walk how image provenance protects a cluster.**
A: You sign (`cosign sign`) and verify (`cosign verify`) images against a key. An admission controller (`policy-controller`/`notation-controller`) rejects any Pod whose image isn't signed by an approved key, so a compromised registry or CI pipeline can't push a trojan image and have it run. You can also pin images to a digest (`image: repo/app@sha256:...`) so only a vetted hash is ever pulled.

**Q: What is `--authorization-mode=AlwaysAllow` and why does CKS care?**
A: It means **every request is allowed** (no RBAC enforced) — the default on some bootstrapped clusters. CKS wants you to set `Node,RBAC` so ServiceAccounts can only read/write what you explicitly grant, which is the foundation of zero-trust.

## Related Resources

- [RBAC](../06-security/rbac.md)
- [Network Policies](../04-networking/network-policies.md)
- [Pod Security Admission](../06-security/pod-security-admission.md)
- [Secrets](../06-security/secrets.md)
- [Certificates](../06-security/certificates.md)
- [Image Scanning](../06-security/README.md)
- [Upgrades](../08-cluster-operations/upgrades.md)
