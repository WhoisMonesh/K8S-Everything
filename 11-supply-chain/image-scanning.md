# Container Image Scanning

> **Category:** Supply Chain / Security
> Scan container images for vulnerabilities, malware, and misconfigurations before they reach production.

## Why scan images?

- **Known CVEs** in OS packages (Alpine, Ubuntu, Node.js, Python)
- **Outdated libraries** (Log4j, OpenSSL, lodash)
- **Misconfigurations** (running as root, exposed ports, secrets in layers)
- **License violations** (GPL in proprietary images)

## Scanning Tools

| Tool | Type | Free | Integration |
|------|------|------|-------------|
| **Trivy** | Full scan (CVE + config + secrets) | ✅ | GitHub Actions, K8s, Docker |
| **Grype** | CVE scanner (fast) | ✅ | CI/CD, Docker |
| **Syft** | SBOM generator (pairs with Grype) | ✅ | CI/CD |
| **Snyk** | CVE + license + fix recommendations | Freemium | GitHub, Docker Hub |
| **Docker Scout** | CVE + fix recommendations | Freemium | Docker Desktop |
| **Clair** | CVE scanner (self-hosted) | ✅ | Registry integration |
| **Harbor** | Registry + built-in scanning | ✅ | K8s, Docker |

## Trivy (recommended)

```bash
# Install Trivy
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s

# Scan image for CVEs
trivy image <image>:<tag>

# Scan with severity filter
trivy image --severity HIGH,CRITICAL <image>:<tag>

# Scan and fail on critical
trivy image --exit-code 1 --severity CRITICAL <image>:<tag>

# Scan filesystem (dependencies)
trivy fs --security-checks vuln,secret,misconfig .

# Scan Kubernetes manifests
trivy k8s --report summary cluster
```

## Grype (fast CVE scan)

```bash
# Install Grype
curl -sSfL https://raw.githubusercontent.com/anchore/grype/main/install.sh | sh -s

# Scan image
grype <image>:<tag>

# Scan with output format
grype <image>:<tag> -o json > results.json

# Fail on high/critical
grype <image>:<tag> --fail-on high
```

## CI/CD Integration

### GitHub Actions

```yaml
- name: Run Trivy vulnerability scanner
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: ${{ env.IMAGE }}
    format: table
    exit-code: 1
    severity: CRITICAL,HIGH

- name: Run Grype scanner
  uses: anchore/scan-action@v3
  with:
    image: ${{ env.IMAGE }}
    fail-build: true
    severity-cutoff: high
```

### GitLab CI

```yaml
trivy-scan:
  script:
    - trivy image --exit-code 1 --severity CRITICAL $IMAGE
```

## Kubernetes Integration

### Kyverno Policy (block vulnerable images)

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-image-scan
spec:
  validationFailureAction: enforce
  rules:
    - name: check-vulnerabilities
      match:
        any:
          - resources:
              kinds:
                - Pod
      verifyImages:
        - imageReferences:
            - "*"
      validate:
        message: "Images must not have CRITICAL vulnerabilities"
        deny:
          conditions:
            any:
              - key: "{{request.object.status.conditions[?(@.type=='Ready')].status}}"
                operator: Equals
                value: "False"
```

### OPA/Gatekeeper

```yaml
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sAllowedRepos
metadata:
  name: require-trusted-repos
spec:
  match:
    kinds:
      - apiGroups: [""]
        kinds: ["Pod"]
  parameters:
    repos:
      - "myregistry.azurecr.io/"
      - "ghcr.io/myorg/"
```

## Scanning Schedule

| When | What | Tool |
|------|------|------|
| **CI build** | New image before push | Trivy, Grype |
| **Pre-deploy** | Image before `kubectl apply` | Trivy K8s |
| **Registry scan** | All images in registry | Harbor, Clair |
| **Nightly** | All production images | Trivy (cron) |
| **On CVE publish** | Rescan affected images | Trivy + webhook |

## Remediation Workflow

```
1. Scan → find CVE
2. Check severity (CRITICAL/HIGH → fix now, MEDIUM → next sprint, LOW → track)
3. Update base image: docker build --no-cache
4. Re-scan → verify CVE gone
5. Push → deploy
6. If no fix available: document, apply WAF rule, or accept risk
```

## Related

- [SBOM](./sbom.md)
- [Cosign](./cosign.md)
- [Security](../06-security/security.md)
