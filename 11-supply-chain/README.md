# Supply Chain Security

> Protecting the software supply chain from source code to runtime.

## Overview

Supply chain security in Kubernetes ensures that every artifact — container images, Helm charts, WASM modules — is **verified, signed, and traceable** from build to deployment.

## Topics

| # | Topic | File |
|---|-------|------|
| 1 | Cosign (keyless signing + SBoM) | [cosign.md](cosign.md) |
| 2 | SBOM (Software Bill of Materials) | [sbom.md](sbom.md) |
| 3 | Container Image Scanning | [image-scanning.md](image-scanning.md) |

## Why It Matters

| Threat | Mitigation |
|--------|------------|
| Tampered container images | Image signing (Cosign) + verification at admission |
| Unknown vulnerabilities | Image scanning (Trivy, Grype) in CI/CD |
| Missing provenance | SBOM generation + attestation |
| Supply chain attacks | In-toto attestations, SLSA framework |

## Related

- [Security Overview](../06-security/security.md)
- [Admission Controllers](../06-security/admission-controllers.md)
- [Kyverno](../06-security/kyverno.md)
