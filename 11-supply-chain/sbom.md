# Software Bill of Materials (SBOM)

> **Category:** Supply Chain / Security
> An SBOM is a machine-readable inventory of all components, libraries, and dependencies in a container image or application.

## What is an SBOM?

An SBOM lists every package, library, and dependency in a software artifact — like a nutrition label for your container image. It enables:
- **Vulnerability tracking**: know exactly which CVEs affect your image
- **License compliance**: identify GPL/MIT/Apache dependencies
- **Supply chain security**: verify provenance and integrity of components

## SBOM Formats

| Format | Standard | Tool |
|--------|----------|------|
| **SPDX** | Linux Foundation | Syft, Docker SBOM |
| **CycloneDX** | OWASP | Syft, Grype |
| **SWID Tags** | ISO/IEC 19770-2 | Windows-focused |

## Generating SBOMs

### With Syft (recommended)

```bash
# Install Syft
curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s

# Generate SBOM (SPDX format)
syft <image> -o spdx-json > sbom.spdx.json

# Generate SBOM (CycloneDX format)
syft <image> -o cyclonedx-json > sbom.cdx.json

# Generate SBOM from directory/filesystem
syft dir:./my-app -o spdx-json > sbom.spdx.json

# Generate SBOM from OCI registry
syft registry:myrepo/myapp:latest -o spdx-json > sbom.spdx.json
```

### With Docker

```bash
# Docker SBOM (built-in, uses Syft)
docker sbom <image> --format spdx-json > sbom.spdx.json
```

### With Grype (scan SBOM for vulnerabilities)

```bash
# Scan SBOM for vulnerabilities
grype sbom:sbom.spdx.json

# Scan image directly (includes SBOM generation)
grype <image>
```

## Using SBOMs in CI/CD

```yaml
# GitHub Actions example
- name: Generate SBOM
  run: |
    syft $IMAGE -o spdx-json > sbom.spdx.json

- name: Scan SBOM for vulnerabilities
  run: |
    grype sbom:sbom.spdx.json --fail-on high

- name: Sign SBOM with Cosign
  run: |
    cosign sign-blob --yes --output-signature sbom.sig \
      --output-certificate sbom.cert sbom.spdx.json
```

## SBOM in Kubernetes

```yaml
# Attach SBOM to image with Cosign
cosign attach sbom --sbom sbom.spdx.json <image>

# Verify SBOM exists before deployment
cosign verify-attachment <image> --type sbom
```

## Best Practices

1. **Generate SBOM for every build** — automate in CI/CD pipeline
2. **Sign the SBOM** — use Cosign to prevent tampering
3. **Store SBOMs** — attach to images, store in artifact registry
4. **Scan regularly** — re-scan SBOMs when new CVEs are published
5. **Version your SBOMs** — track changes over time

## Related

- [Cosign](../11-supply-chain/cosign.md)
- [Image Scanning](./image-scanning.md)
- [Security](../06-security/security.md)
