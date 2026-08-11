# Advanced Examples

> Multi-container pod patterns, init containers, StatefulSets, and DaemonSets.

## Contents
- `daemonset.yaml` — node-exporter DaemonSet with hostNetwork + control-plane tolerations.
- `init-container.yaml` — a Pod that runs a setup task (init container) before the app starts.
- `sidecar-proxy.yaml` — an app + a sidecar sharing an emptyDir.
- `statefulset.yaml` — StatefulSet + headless Service + volumeClaimTemplates.

## Usage

```bash
kubectl apply -R -f .          # deploy all in this directory
kubectl apply -f . --dry-run=client   # validate first
kubectl delete -R -f .            # remove
```
