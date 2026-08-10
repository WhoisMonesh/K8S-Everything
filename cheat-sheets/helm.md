# Helm CLI Cheatsheet

> Quick reference for Helm commands.

## Installation

```bash
# macOS
brew install helm

# Linux
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Verify
helm version
helm env
```

## Repository Management

```bash
# Add a repository
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx

# List repositories
helm repo list

# Update repositories
helm repo update

# Remove a repository
helm repo remove bitnami

# Search for charts
helm search repo nginx
helm search repo nginx --max-collision 3
helm search hub nginx  # Search on Artifact Hub
```

## Chart Operations

```bash
# Install a chart
helm install my-release bitnami/nginx

# Install with custom values
helm install my-release bitnami/nginx -f values.yaml
helm install my-release bitnami/nginx --set replicaCount=3

# Upgrade a release
helm upgrade my-release bitnami/nginx
helm upgrade my-release bitnami/nginx -f new-values.yaml

# Install or upgrade (idempotent)
helm upgrade --install my-release bitnami/nginx

# Rollback
helm rollback my-release 1

# Uninstall
helm uninstall my-release
helm uninstall my-release --keep-history  # Keep history for rollback
```

## Release Management

```bash
# List releases
helm list
helm list --all-namespaces
helm list --all  # Include deleted releases

# Get release status
helm status my-release
helm status my-release --revision 1

# Get release values
helm get values my-release
helm get all my-release  # manifests, values, hooks

# Test a release
helm test my-release

# History (revisions)
helm history my-release
```

## Chart Development

```bash
# Create a new chart
helm create my-chart

# Package a chart
helm package ./my-chart

# Lint a chart
helm lint ./my-chart

# Render templates locally
helm template ./my-chart
helm template my-release ./my-chart
helm template -f values.yaml ./my-chart

# Dependency management
helm dependency update ./my-chart
helm dependency build ./my-chart
helm dependency list ./my-chart
```

## Useful Flags

```bash
# Set namespace
helm install --namespace production --create-namespace

# Wait for resources
helm install --wait --timeout 5m

# Atomic (rollback on failure)
helm install --atomic

# Dry run
helm install --dry-run --debug my-release ./my-chart

# Skip CRD installation
helm install --skip-crds

# Generate name (random)
helm install --generate-name ./my-chart

# Set values from file (key=value file)
helm install --values my-values.txt
--set-string key=value    # Force string
--set-json key='{"a":1}'  # Set JSON value
--set-file key=@filename  # Set value from file
```

---

## Related Resources

- [Helm Documentation](../10-package-management/helm.md)
- [kubectl Cheatsheet](kubectl.md)
