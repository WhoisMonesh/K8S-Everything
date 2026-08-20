# CIS Benchmarks for Kubernetes

> **Category:** Security / Compliance

## What It Is

The **CIS Kubernetes Benchmark** is a set of security best practices published by the Center for Internet Security. It provides prescriptive guidance for hardening Kubernetes clusters, and is a key reference for CKS certification.

## Why It Exists

| Problem | Without CIS | With CIS |
|---------|-------------|----------|
| Security posture | Ad-hoc hardening | Standardized checklist |
| Audit | Manual review | Automated scanning (kube-bench) |
| Compliance | No evidence | Published benchmark |
| Exam prep | Guessing what to study | Clear domain list |

## Benchmark Sections

| Section | Description | Weight |
|---------|-------------|--------|
| 1. Control Plane | API server, etcd, scheduler, controller-manager | 25% |
| 2. etcd | Data encryption, authentication, peer communication | 15% |
| 3. Control Plane Configuration | Audit logging, admission plugins | 10% |
| 4. Worker Nodes | kubelet configuration, kube-proxy | 20% |
| 5. Policies | RBAC, Pod Security, Network Policies | 30% |

## Install kube-bench

```bash
# Run as a Pod (recommended)
kubectl apply -f https://raw.githubusercontent.com/aquasecurity/kube-bench/main/job.yaml

# Run locally
curl -L https://github.com/aquasecurity/kube-bench/releases/download/v0.8.1/kube-bench_0.8.1_linux_amd64.tar.gz | tar -xz
./kube-bench

# Docker
docker run --pid=host -v /etc:/node/etc:ro -v /var:/node/var:ro -ti aquasec/kube-bench
```

## Key Checks

### Control Plane

| Check | Description | Fix |
|-------|-------------|-----|
| 1.1.1 | Ensure API server audit logging is enabled | `--audit-log-path` and `--audit-log-maxage` |
| 1.1.2 | Ensure API server audit log maxage is set | `--audit-log-maxage=30` |
| 1.1.3 | Ensure API server audit log maxbackup is set | `--audit-log-maxbackup=10` |
| 1.1.4 | Ensure API server audit log maxsize is set | `--audit-log-maxsize=100` |
| 1.1.5 | Ensure API server --authorization-mode not set to AlwaysAllow | Set to `Node,RBAC` |
| 1.1.6 | Ensure API server --anonymous-auth is disabled | `--anonymous-auth=false` |
| 1.1.7 | Ensure API server --basic-auth-file is not set | Remove basic auth |
| 1.1.8 | Ensure API server --token-auth-file is not set | Remove token auth |
| 1.1.9 | Ensure API server --kubelet-https-certificate-authority is set | Configure CA |
| 1.1.10 | Ensure API server --kubelet-client-certificate and --kubelet-client-key are set | Configure client cert |

### etcd

| Check | Description | Fix |
|-------|-------------|-----|
| 2.1 | Ensure that the --cert-file and --key-file arguments are set as appropriate | Configure TLS |
| 2.2 | Ensure that the --client-cert-auth argument is set to true | `--client-cert-auth=true` |
| 2.3 | Ensure that the --auto-tls argument is not set to true | Disable auto-TLS |
| 2.4 | Ensure that the --peer-cert-file and --peer-key-file arguments are set as appropriate | Configure peer TLS |
| 2.5 | Ensure that the --peer-client-cert-auth argument is set to true | `--peer-client-cert-auth=true` |
| 2.6 | Ensure that the --peer-auto-tls argument is not set to true | Disable peer auto-TLS |
| 2.7 | Ensure that a unique Certificate Authority is used for etcd | Separate CA for etcd |

### Worker Nodes

| Check | Description | Fix |
|-------|-------------|-----|
| 4.1.1 | Ensure that the kubelet service file permissions are set to 644 or more restrictive | `chmod 644` |
| 4.1.2 | Ensure that the kubelet service file ownership is set to root:root | `chown root:root` |
| 4.1.3 | Ensure that the proxy arguments are set as appropriate | Configure kube-proxy |
| 4.1.4 | Ensure that the --cert-file and --key-file arguments are set as appropriate | Configure kubelet TLS |
| 4.1.5 | Ensure that the --client-cert-auth argument is set to true | `--client-cert-auth=true` |

### Policies

| Check | Description | Fix |
|-------|-------------|-----|
| 5.1.1 | Ensure that the cluster-admin role is only used where required | Use least privilege |
| 5.1.2 | Minimize access to secrets | Restrict secret access |
| 5.1.3 | Minimize wildcard use in ClusterRoles and ClusterRoleBindings | Avoid `*` in rules |
| 5.1.4 | Ensure that default service accounts are not actively used | Disable automount |
| 5.1.5 | Ensure that Service Account Tokens are not mounted automatically | Set `automountServiceAccountToken: false` |
| 5.2.1 | Ensure that the Pod Security Standards are applied to pods | Use PSA |
| 5.2.2 | Minimize the admission of privileged containers | Restrict privileged |
| 5.2.3 | Minimize the admission of containers wishing to share the host process ID namespace | Restrict hostPID |
| 5.2.4 | Minimize the admission of containers wishing to share the host IPC namespace | Restrict hostIPC |
| 5.2.5 | Minimize the admission of containers wishing to share the host network namespace | Restrict hostNetwork |
| 5.2.6 | Minimize the admission of containers with allowPrivilegeEscalation | Restrict escalation |
| 5.2.7 | Minimize the admission of root containers | Run as non-root |
| 5.2.8 | Minimize the admission of containers with added capabilities | Drop ALL capabilities |
| 5.2.9 | Minimize the admission of containers with the NET_RAW capability | Drop NET_RAW |
| 5.2.10 | Minimize the admission of containers with the SYS_ADMIN capability | Drop SYS_ADMIN |
| 5.4.1 | Prefer using Secrets as files over environment variables | Mount secrets as files |
| 5.4.2 | Consider external secret storage | Use External Secrets Operator |

## Commands

```bash
# Run kube-bench on all nodes
kubectl apply -f https://raw.githubusercontent.com/aquasecurity/kube-bench/main/job.yaml
kubectl logs -l app=kube-bench

# Run on specific node
kubectl describe node <node-name>  # Get node name
kubectl logs job/kube-bench --grep=<node-name>

# View results as JSON
kube-bench --json

# View specific section
kube-bench run --targets master
kube-bench run --targets node
```

## Best Practices

1. **Run regularly** — integrate into CI/CD or schedule daily
2. **Fix critical findings first** — focus on severity HIGH/MEDIUM
3. **Document exceptions** — some checks may not apply
4. **Automate remediation** — use scripts for common fixes
5. **Track progress** — compare results over time

## Related

- [Security Overview](../06-security/security.md)
- [Security Hardening Guide](security-hardening-guide.md)
- [RBAC](../06-security/rbac.md)
- [Pod Security Admission](../06-security/pod-security-admission.md)
- [CKS Certification](../16-interview-prep/cks.md)
