# CKS Mock Exam

> **Category:** Interview Prep / Certification
> Simulated CKS exam scenarios with solutions.

## Exam Format

| Detail | Value |
|--------|-------|
| Duration | 2 hours |
| Questions | 15-20 |
| Pass score | 67% |
| Prerequisite | CKA certification |
| Format | Performance-based (hands-on) |
| Resources | Kubernetes docs allowed |

---

## Mock Exam 1: Cluster Setup (10%)

### Task 1: CIS Benchmark Remediation

**Question:** The cluster has failed CIS benchmark check 4.2.1. Ensure the kubelet is configured with `--anonymous-auth=false`.

```bash
# Solution
# Edit kubelet config
sudo vi /var/lib/kubelet/config.yaml

# Add or modify:
authentication:
  anonymous:
    enabled: false

# Or via flag
sudo vi /etc/systemd/system/kubelet.service.d/10-kubeadm.conf
# Add: --anonymous-auth=false

# Restart kubelet
sudo systemctl daemon-reload
sudo systemctl restart kubelet
```

### Task 2: Audit Logging

**Question:** Enable audit logging with a policy that logs metadata for all requests in the `production` namespace.

```bash
# Solution
cat <<EOF | sudo tee /etc/kubernetes/audit-policy.yaml
apiVersion: audit.k8s.io/v1
kind: Policy
rules:
- level: Metadata
  resources:
  - group: ""
    resources: ["*"]
  namespaces: ["production"]
- level: None
  resources:
  - group: ""
    resources: ["events"]
EOF

# Add to API server args
sudo vi /etc/kubernetes/manifests/kube-apiserver.yaml
# Add: --audit-policy-file=/etc/kubernetes/audit-policy.yaml
# Add: --audit-log-path=/var/log/kubernetes/audit.log
# Add: --audit-log-maxage=30
# Add: --audit-log-maxbackup=10
# Add: --audit-log-maxsize=100
```

---

## Mock Exam 2: Cluster Hardening (15%)

### Task 3: RBAC Restriction

**Question:** Create a Role `pod-reader` that allows only `get`, `list`, `watch` on pods in namespace `production`. Bind it to service account `app-sa`.

```bash
# Solution
cat <<EOF | kubectl apply -f -
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: pod-reader
  namespace: production
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: pod-reader-binding
  namespace: production
subjects:
- kind: ServiceAccount
  name: app-sa
  namespace: production
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
EOF
```

### Task 4: Pod Security Admission

**Question:** Enforce restricted Pod Security Standards on namespace `secure-apps`.

```bash
# Solution
kubectl label namespace secure-apps \
  pod-security.kubernetes.io/enforce=restricted \
  pod-security.kubernetes.io/audit=restricted \
  pod-security.kubernetes.io/warn=restricted

# Verify
kubectl get namespace secure-apps --show-labels
```

### Task 5: ServiceAccount Hardening

**Question:** Create a service account `restricted-sa` with automount of API credentials disabled.

```bash
# Solution
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: ServiceAccount
metadata:
  name: restricted-sa
automountServiceAccountToken: false
EOF
```

---

## Mock Exam 3: System Hardening (15%)

### Task 6: Container Runtime

**Question:** Configure the container runtime to use seccomp profile `RuntimeDefault`.

```bash
# Solution
# Edit containerd config
sudo vi /etc/containerd/config.toml

# Add under [plugins."io.containerd.grpc.v1.cri"]:
#   [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runc.options]
#     SystemdCgroup = true

# Or configure at pod level
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: secure-pod
spec:
  securityContext:
    seccompProfile:
      type: RuntimeDefault
  containers:
  - name: app
    image: nginx:1.25
EOF
```

### Task 7: Node Security

**Question:** Ensure kubelet is configured with `--protect-kernel-defaults=true`.

```bash
# Solution
sudo vi /var/lib/kubelet/config.yaml

# Add:
protectKernelDefaults: true

# Restart kubelet
sudo systemctl restart kubelet
```

---

## Mock Exam 4: Microservice Vulnerabilities (15%)

### Task 8: Image Scanning

**Question:** Scan the image `nginx:1.25` for HIGH and CRITICAL vulnerabilities.

```bash
# Solution
# Using Trivy
trivy image --severity HIGH,CRITICAL nginx:1.25

# Using Grype
grype nginx:1.25 --only-fixed --fail-on high
```

### Task 9: Image Verification

**Question:** Verify that the image `myregistry.com/app:v1` is signed using cosign.

```bash
# Solution
cosign verify --key cosign.pub myregistry.com/app:v1
```

### Task 10: Admission Control

**Question:** Create a ValidatingAdmissionPolicy that rejects pods with images from untrusted registries.

```bash
# Solution
cat <<EOF | kubectl apply -f -
apiVersion: admissionregistration.k8s.io/v1
kind: ValidatingAdmissionPolicy
metadata:
  name: require-trusted-images
spec:
  failurePolicy: Fail
  matchConstraints:
    resourceRules:
    - apiGroups: [""]
      apiVersions: ["v1"]
      operations: ["CREATE", "UPDATE"]
      resources: ["pods"]
  validations:
  - expression: "all(object.spec.containers, c, c.image.startsWith('myregistry.com/') || c.image.startsWith('docker.io/library/'))"
    message: "Images must come from trusted registries"
EOF
```

---

## Mock Exam 5: Supply Chain Security (20%)

### Task 11: SBOM Generation

**Question:** Generate an SBOM for the image `nginx:1.25` in SPDX format.

```bash
# Solution
syft nginx:1.25 -o spdx-json > nginx-sbom.spdx.json
```

### Task 12: Sealed Secrets

**Question:** Encrypt a secret `db-password` using Sealed Secrets so it can be stored in Git.

```bash
# Solution
# Create the secret
kubectl create secret generic db-password \
  --from-literal=password=mysecretpassword \
  --dry-run=client -o yaml > secret.yaml

# Seal it
kubeseal --format yaml < secret.yaml > sealed-secret.yaml

# Now safe to commit sealed-secret.yaml
```

### Task 13: External Secrets

**Question:** Configure External Secrets Operator to sync a secret from AWS Secrets Manager.

```bash
# Solution
cat <<EOF | kubectl apply -f -
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: aws-store
spec:
  provider:
    aws:
      service: SecretsManager
      region: us-east-1
      auth:
        secretRef:
          accessKeyIDSecretRef:
            name: aws-credentials
            key: access-key-id
          secretAccessKeySecretRef:
            name: aws-credentials
            key: secret-access-key
---
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: db-credentials
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aws-store
    kind: SecretStore
  target:
    name: db-credentials
  data:
  - secretKey: password
    remoteRef:
      key: prod/db/password
EOF
```

---

## Mock Exam 6: Logging, Monitoring & Runtime Security (20%)

### Task 14: Falco Rule

**Question:** Create a Falco rule that detects when a container runs `curl` to an external IP.

```yaml
# Solution
- rule: Detect Curl to External IP
  desc: Detect curl commands to external IPs
  condition: >
    spawned_process and container and
    proc.name = "curl" and
    not proc.args contains "internal"
  output: >
    Curl to external IP detected
    (user=%user.name container=%container.name proc=%proc.args)
  priority: WARNING
  tags: [network, mitre_exfiltration]
```

### Task 15: Audit Policy

**Question:** Create an audit policy that logs all requests to secrets at RequestResponse level.

```yaml
# Solution
apiVersion: audit.k8s.io/v1
kind: Policy
rules:
- level: RequestResponse
  resources:
  - group: ""
    resources: ["secrets"]
- level: Metadata
  resources:
  - group: ""
    resources: ["pods", "services"]
```

---

## Time Management

| Section | Time | Focus |
|---------|------|-------|
| Cluster Setup | 15 min | Quick wins |
| Cluster Hardening | 25 min | RBAC, PSA, service accounts |
| System Hardening | 20 min | Runtime, seccomp |
| Vulnerabilities | 20 min | Scanning, admission |
| Supply Chain | 25 min | SBOM, sealed secrets |
| Monitoring | 15 min | Falco, audit |

## Key Commands

```bash
# Scan images
trivy image --severity HIGH,CRITICAL <image>

# Verify signatures
cosign verify --key cosign.pub <image>

# Check CIS benchmarks
kube-bench run

# Test network policies
kubectl exec -it <pod> -- wget -qO- http://<service>

# Check PSA labels
kubectl get namespace <ns> --show-labels
```

## Related

- [CKS Certification](cks.md)
- [CKA Mock Exam](cka-mock-exam.md)
- [CKAD Mock Exam](ckad-mock-exam.md)
- [Security Hardening Guide](../../docs/security-hardening-guide.md)
- [CIS Benchmarks](../../docs/cis-benchmarks.md)
