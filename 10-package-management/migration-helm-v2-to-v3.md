# Migration Guide: Helm v2 to Helm v3

> **Category:** Package Management / Migration
> Step-by-step guide for migrating from Helm v2 to Helm v3.

## Overview

```mermaid
graph LR
    A[Helm v2] --> B[Install Helm 3]
    B --> C[Migrate Charts]
    C --> D[Update CI/CD]
    D --> E[Test]
    E --> F[Cleanup]
```

## Key Changes

| Feature | Helm v2 | Helm v3 |
|---------|---------|---------|
| **Tiller** | Required | Removed |
| **Storage** | Secret in kube-system | Secret in release namespace |
| **RBAC** | Complex (Tiller) | Simple (kubeconfig) |
| **Chart format** | `.tgz` only | `.tgz` and OCI |
| **Uninstall** | `helm delete --purge` | `helm uninstall` |
| **Rollback** | `helm rollback` | `helm rollback` |
| **Hooks** | `pre-install`, `post-install` | `pre-install`, `post-install` |
| **Tests** | `helm test` | `helm test` |

## Phase 1: Install Helm 3

```bash
# Install Helm 3
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Verify installation
helm version
```

## Phase 2: Migrate Releases

### List v2 Releases

```bash
# List Helm v2 releases
helm2 list --all-namespaces
```

### Migrate Single Release

```bash
# Migrate a single release
helm2to3 convert <release-name> --skip-schema-validation

# Verify migration
helm list -n <namespace>
```

### Migrate All Releases

```bash
# Migrate all releases
for release in $(helm2 list --all-namespaces -q); do
  helm2to3 convert "$release" --skip-schema-validation
done
```

## Phase 3: Update CI/CD

### Update Scripts

```bash
# Before (Helm v2)
helm delete --purge my-release
helm install --name my-release ./my-chart
helm upgrade --install --name my-release ./my-chart

# After (Helm v3)
helm uninstall my-release
helm install my-release ./my-chart
helm upgrade --install my-release ./my-chart
```

### Update GitHub Actions

```yaml
# Before
- name: Deploy with Helm
  run: |
    helm delete --purge my-release
    helm install --name my-release ./my-chart

# After
- name: Deploy with Helm
  run: |
    helm uninstall my-release
    helm install my-release ./my-chart
```

## Phase 4: Test

### Validation Checklist

| Check | Command |
|-------|---------|
| Releases migrated | `helm list -A` |
| Charts working | `helm test <release>` |
| Rollbacks working | `helm rollback <release> 1` |
| Uninstalls working | `helm uninstall <release>` |

### Test Rollback

```bash
# Upgrade release
helm upgrade my-release ./my-chart --set image.tag=v2

# Rollback
helm rollback my-release 1

# Verify
helm history my-release
```

## Phase 5: Cleanup

### Remove Tiller

```bash
# Delete Tiller namespace
kubectl delete namespace kube-system

# Delete Tiller CRDs
kubectl delete crd -l owner=helm
```

### Remove Helm v2

```bash
# Remove Helm v2 binary
rm $(which helm2)

# Remove Helm v2 config
rm -rf ~/.helm2
```

## Common Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| Release not found | Different storage | Use `--all-namespaces` |
| RBAC errors | Tiller removed | Update kubeconfig |
| Chart format issues | v2 format | Update Chart.yaml |
| Hook failures | Changed behavior | Update hook definitions |

## Best Practices

| Phase | Practice |
|-------|----------|
| Pre-migration | Backup releases: `helm2 get all <release>` |
| Migration | Migrate one release at a time |
| Post-migration | Test all releases thoroughly |
| Cleanup | Remove Tiller after all releases migrated |

## Related

- [Helm](../10-package-management/helm.md)
- [Helm Best Practices](../10-package-management/helm-best-practices.md)
- [Helm Chart Development](../10-package-management/helm-chart-development.md)
