# Storage Examples

> PV/PVC, StorageClass, and VolumeSnapshot patterns.

## Contents
- `pvc-deployment.yaml` — StorageClass + PVC + Deployment mounting the PVC.
- `storage-class-nfs.yaml` — NFS-backed StorageClass.
- `storage-class-wait.yaml` — WaitForConsumer binding + volume expansion toggle.
- `volume-snapshot.yaml` — VolumeSnapshot + restore into a new PVC.

## Usage

```bash
kubectl apply -R -f .          # deploy all in this directory
kubectl apply -f . --dry-run=client   # validate first
kubectl delete -R -f .            # remove
```
