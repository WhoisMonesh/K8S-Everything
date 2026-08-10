# Debugging Commands

> **Category:** Interview Preparation

Copy-paste commands that prove a resource is correct, in the order you usually need them. `k = kubectl`.

## General verification
```bash
k get <kind> -n <ns> -o name
k get <kind> -n <ns> -o wide
k describe <kind> <name> -n <ns>
k get <kind> <name> -n <ns> -o yaml
k get <kind> <name> -n <ns> -o jsonpath='{.status}'
```

## Workload rollout + observe
```bash
k rollout status deploy/<name> -n <ns>
k rollout history deploy/<name> -n <ns>
k rollout undo deploy/<name> --to-revision=2 -n <ns>
k set image deploy/<name> <c>=<img> -n <ns>
k set resources deploy/<name> -c <c> --requests=cpu=100m,memory=128Mi -n <ns>
```

## Probe / endpoint debugging
```bash
k get endpoints -n <ns> <svc>            # empty -> selector/Probe issue
k get endpoints -n <ns> <svc> -w          # watch it populate
k describe pod <p> -n <ns>              # probe event/failures
```

## RBAC checks (reproduce a 403 as a SA)
```bash
k auth can-i get pods --as=system:serviceaccount:<ns>:<sa>
k auth can-i '*' --as=system:serviceaccount:<ns>:<sa>
k auth can-i list pods --namespace=kube-system
```

## Storage / PVC debugging
```bash
k get pv,pvc -n <ns>
k get sc                          # StorageClasses
k describe pvc <pvc> -n <ns>      # why not binding?
k get pv <pv> -o yaml             # reclaimPolicy, accessModes
```

## Network debugging
```bash
# A Pod with net tools:
k run netshoot --image=nicolaka/netshoot --rm -it -- sh
# inside:
nslookup <svc>.<ns>.svc.cluster.local
curl -v http://<svc>.<ns>.svc.cluster.local/
```

## Node-level (CKA)
```bash
k get nodes -o wide
k describe node <n>
k top node
k get --raw /api/v1/nodes/<n>/proxy/metrics | grep container
```

## Exam shortcuts
```bash
k run web --image=nginx --port=80 --restart=Never --dry-run=client -o yaml > w.yaml
k patch pvc data --type=merge -p '{"spec":{"storageClassName":"fast"}}'
k create secret generic tls --from-file=tls.crt=./tls.crt --from-file=tls.key=./tls.key
```

## Related
- [kubectl Cheatsheet](../cheat-sheets/kubectl.md)
- [Troubleshooting Patterns](../14-troubleshooting/troubleshooting-patterns.md)
