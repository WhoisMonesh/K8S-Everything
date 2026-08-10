# Secrets

> **Category:** Security / Sensitive Data

## What It Is

A **Secret** is a Kubernetes object that stores **sensitive data** — passwords, tokens, TLS certs, registry credentials. Secrets are **base64-encoded** (not encrypted) in etcd by default; they are sent over HTTPS only to the API.

Secrets are **namespace-scoped** and consumed by Pods via **env vars** or **mounted volumes**.

## Why It Exists

- Avoid hardcoding secrets in manifests or images
- Decouple secret rotation from application code
- Grant access per-namespace via RBAC
- Keep secrets out of logs (when not printed)

## Secret API

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: my-secret
  namespace: default
type: Opaque                    # Opaque | kubernetes.io/tls | kubernetes.io/dockerconfigjson
stringData:                     # PLAINTEXT (auto-base64-encoded on write) — for human editing
  username: user
  password: pass
  host: localhost
data:                          # base64-encoded (manual) — used when creating via tools
  tls.crt: <base64 cert>
  tls.key: <base64 key>
```

### Secret Types

| Type | Purpose | Fields |
|------|---------|--------|
| `Opaque` | Generic (default) | Any key/value |
| `kubernetes.io/tls` | TLS cert + key | `tls.crt`, `tls.key` |
| `kubernetes.io/dockerconfigjson` | Registry credentials | `.dockerconfigjson` |
| `kubernetes.io/basic-auth` | HTTP basic auth | `username`, `password` |
| `kubernetes.io/token` | Service tokens | `token` |
| `kubernetes.io/service-account-token` | Legacy SA token | `token` |

## Base64 Is NOT Encryption

Secrets are **base64-encoded** (not encrypted) — anyone with `get secret` can decode:

```bash
echo "dXNlcg==" | base64 --decode    # outputs "user"
kubectl get secret my-secret -o jsonpath="{.data.password}" | base64 --decode
```

To **encrypt at rest**, configure etcd encryption (see "Encryption at Rest" below).

### Decoding a secret in-cluster
```bash
# From inside a Pod that can read secrets:
kubectl get secret my-secret -o jsonpath="{.data.password}" | base64 --decode
```

## Encrypting Secrets at Rest (etcd Encryption)

The kube-apiserver **encrypts** certain resources (secrets) before writing to etcd:

`encryption-config.yaml`:
```yaml
apiVersion: apiserver.config.k8s.io/v1
kind: EncryptionConfiguration
resources:
- resources:
  - secrets
  providers:
  - aescbc:                                   # AES-CBC (or: identity, kms)
      keys:
      - name: key1
        secret: <base64 of 32-byte key>
  - identity: {}                               # Fallback (plaintext)
```

Enable via the kube-apiserver flag:
```
--encryption-provider-config /path/to/encryption-config.yaml
```

After enabling:
- New secrets are encrypted
- **Existing secrets** must be re-written (`kubectl delete` + re-create, or `kubectl annotate` to trigger)

### KMS Provider (cloud key management)

| Cloud | Plugin |
|-------|--------|
| AWS | `kms` (AWS KMS key) |
| GCP | `kms` (Cloud KMS key) |
| Azure | `kms` (Key Vault) |

```yaml
providers:
- kms:
    apiVersion: v1.4
    endpoint: "grpc://localhost:8888"   # External KMS plugin
    name: kms-provider
```

## Using Secrets in Pods

### Method 1: Environment variable (single key)
```yaml
env:
  - name: DB_PASSWORD
    valueFrom:
      secretKeyRef:
        name: db-secret
        key: password
```

### Method 2: All keys as env vars (envFrom)
```yaml
envFrom:
  - secretRef:
      name: my-secret
```

### Method 3: Mounted as a volume
```yaml
volumes:
- name: my-secret-vol
  secret:
    secretName: my-secret
    defaultMode: 0400            # file permissions (read by owner only)
    items:                       # Optional: only mount specific keys
    - key: password
      path: db-password
containers:
- volumeMounts:
  - name: my-secret-vol
    mountPath: /etc/secrets
    readOnly: true
```

Now `/etc/secrets/db-password` contains the value.

### Method 4: imagePullSecrets (private registry)
```bash
# Create a registry secret
kubectl create secret docker-registry regcred \
  --docker-server=https://index.docker.io \
  --docker-username=myuser \
  --docker-password=mypass

# Attach it to a ServiceAccount
kubectl patch serviceaccount default -p 'spec: {imagePullSecrets: [{name: regcred}]}'
```

## Commands

```bash
# List / inspect
kubectl get secret
kubectl describe secret my-secret          # Note: does NOT show values (they are base64)

# Decode a value
kubectl get secret my-secret -o jsonpath='{.data.password}' | base64 --decode

# Create from literal (auto-encodes)
kubectl create secret generic my-secret \
  --from-literal=password=pass \
  --from-literal=username=user

# Create from a file
kubectl create secret generic my-tls --from-file=tls.crt=cert.pem --from-file=tls.key=key.pem

# Create from an env file
kubectl create secret generic my-secret --from-env-file=env-file

# Delete / update
kubectl delete secret my-secret
kubectl create secret generic my-secret --dry-run=client -o yaml | kubectl apply -f -  # idempotent upsert
```

## Secret Security

### 1. Encrypt at rest (etcd EncryptionConfiguration)
Critical for compliance — otherwise any node with etcd access can read secrets.

### 2. RBAC
Only grant `get`/`list` on secrets to those who **need** them:
```yaml
rules:
- apiGroups: [""]
  resources: ["secrets"]
  verbs: ["get", "list", "watch"]
```

### 3. Audit logging
Track who reads secrets:
```yaml
# In kube-apiserver audit policy:
- resources:
  - group: ""
    resources: ["secrets"]
  verbs: ["get", "list", "watch"]
```

### 4. Disable legacy SA token Secrets (K8s 1.24+)
```bash
# Ensure auto-mounting of deprecated secrets is off
# And use bound tokens (TokenRequest) instead
```

### 5. Use external secret stores (advanced)
Don't store secrets in etcd at all — use **external secret** solutions that write the secret into K8s at runtime:

| Tool | Approach |
|------|----------|
| **External Secrets** | Operator syncs secrets from AWS Secrets Manager / Vault → K8s Secret |
| **HashiCorp Vault** (Agent Injector) | Injects secrets as files at Pod startup |
| **Sealed Secrets** | Git-friendly encrypted Secret (`SealedSecret` CR) |
| **SOPS** | Encrypt secrets in YAML before committing to Git |

## Common Issues

### Secret not mounted (empty file)
```bash
kubectl exec <pod> -- cat /etc/secrets/password
# Empty → Pod started before the Secret existed, or typo in name
# Volumes are mounted at Pod START — updating a Secret doesn't update running Pods (need restart / remount)
```

### "Secret not found" / `ImagePullBackOff` with no pull secret
```bash
# Pod can't pull private image — missing imagePullSecrets
kubectl get sa default -o jsonpath='{.imagePullSecrets}'
# Attach the pull secret to the SA:
kubectl patch sa default -p 'spec: {imagePullSecrets: [{name: regcred}]}'
```

### "permission denied" on mounted Secret (wrong mode)
```yaml
volumes:
- name: vol
  secret:
    defaultMode: 0400      # Readable only by owner (app runs as that owner)
```

### Secret value decodes to garbage
```bash
# The Secret was created with wrong encoding
# Re-create from literal:
kubectl create secret generic my-secret --from-literal=token=abc123 --dry-run=client -o yaml | kubectl apply -f -
```

### Secret too large
```bash
# Max secret size is 1 MiB (etcd object limit)
# For larger: mount from an external source (Vault, S3, external secret)
```

## Environment Variables Are Less Secure

If you pass a secret as an env var, it may be:
- Visible in `/proc/<pid>/environ`
- Exposed in process crash dumps
- Dumped to logs if the app logs its own environment

**Preferred:** mount secrets as **read-only files** at a tight path.

## Service Account Tokens (as Secrets)

Legacy SAs had a `default-token-` Secret auto-created:
```yaml
type: kubernetes.io/service-account-token
data:
  token: <jwt>
  ca.crt: <cluster-ca>
  namespace: default
```

**Since 1.24**, bound tokens (`TokenRequest`) replace this — the legacy token Secret is **not** auto-created, and tokens are projected (short-lived) rather than stored.

## Best Practices

1. **Encrypt secrets at rest** (etcd EncryptionConfiguration + KMS) — required for compliance
2. **Mount as files** (volumes, `defaultMode: 0400`), not env vars — safer from leaks
3. **Grant RBAC minimally** — only `get`/`list` secrets where needed
4. **Avoid `latest`/latest-tagged images** — prevents "secret in image" workarounds
5. **Rotate secrets** — regularly, via automation
6. **Use external secret stores** (Vault, External Secrets, Sealed Secrets) for high-sensitivity
7. **Never commit real Secrets** to Git — use SealedSecrets or SOPS
8. **Audit secret access** — track `get`/`list` on `secrets` via audit logs
9. **Watch etcd limits** — max secret size is 1 MiB
10. **Disable auto-mount of legacy SA secrets** (K8s 1.24+: `--service-account-issuer`, bound tokens)

## Interview Questions

**Q: Is a Kubernetes Secret encrypted?**
A: **No, by default** — it is only **base64-encoded**. To encrypt, enable `EncryptionConfiguration` on the kube-apiserver so etcd stores encrypted values. Base64 ≠ encryption — any reader can decode.

**Q: How do you securely inject a database password into a Pod?**
A: Create a `Secret` (or use an external store like Vault), then mount it as a **read-only volume** at a tight path (`defaultMode: 0400`) — NOT as an env var (env vars leak via `/proc/<pid>/environ` and process dumps).

**Q: What is `imagePullSecrets` and why is it a Secret?**
A: It stores **docker registry credentials** (username/password) as a `kubernetes.io/dockerconfigjson` Secret — used by the kubelet to pull images from private registries. Attach via a ServiceAccount.

**Q: What is the maximum size of a Secret?**
A: **1 MiB** (etcd object limit). Larger data should be mounted from external storage (e.g., S3, Vault, an external secret store).

**Q: How do you make a secret available across namespaces?**
A: You can't directly — Secrets are namespace-scoped. Options: (1) create one per namespace (script it), (2) use `external-secrets` / Sealed Secrets synced across namespaces, or (3) run a single controller that distributes them.

**Q: What's the difference between `data` and `stringData`?**
A: `data` is base64-encoded (use for machine-generated or imported values). `stringData` is plaintext (auto-encoded on write) — easier to author/edit but you must not commit it to Git.

## Related Resources

- [RBAC](rbac.md)
- [Service Accounts](service-accounts.md)
- [Ingress TLS Secrets](../04-networking/ingress.md)
- [Admission Controllers](admission-controllers.md)
- [Pod Security Admission](pod-security-admission.md)
