# kubectl Debugging

> **Category:** Operations / Debugging

This doc covers the `kubectl` toolkit for debugging: `describe`, events, logs, port-forward, and the **ephemeral container** escape hatch for "I can't get a shell".

## The Usual Commands

```bash
kubectl get pods -n <ns> -o wide            # which node? externalIP?
kubectl describe pod <pod>                  # the EVENTS at the bottom — the "why"
kubectl logs <pod>                          # current container
kubectl logs -p <pod>                       # PREVIOUS container (after a restart)
kubectl logs -f <pod>                       # tail
kubectl logs <pod> -c <container>           # specific container (multi-container)
kubectl top pod <pod> -n <ns>               # live CPU/Mem (needs Metrics Server)
```

## Events (`kubectl describe` is the answer)

The bottom of `kubectl describe pod ...` shows recent **Events** (a.k.a. "the reason K8s did what it did"):

```text
Events:
  Type     Reason     Age   From               Message
  ----     ------     ----  ----               -------
  Warning  FailedScheduling  5s    default-scheduler  0/3 nodes are available
  Warning  FailedAttachVolume  4s  attachdetach-controller  ...
```

You can also ask for **only recent events** across the cluster:

```bash
kubectl get events -A --sort-by='.lastTimestamp' | tail -30
# or filter by a time window (Kubernetes 1.27+):
kubectl get events -A --field-selector 'lastTimestamp>2024-01-01T00:00:00Z'
```

## Logs: current vs. previous

If a Pod is `CrashLoopBackOff`, the **current** container has just restarted — `kubectl logs <pod>` shows the (brief) startup, then it dies. You want the **previous** instance:

```bash
kubectl logs --previous <pod>     # alias: -p
```

### `kubectl logs` tips

```bash
kubectl logs -f <pod> --since=1h    # last hour
kubectl logs -f <pod> --tail=100    # last 100 lines
kubectl logs -f <pod> --timestamps  # prefix with wall-clock
kubectl logs <pod> -c app           # one container in a multi-container Pod
# Stream from a ReplicaSet (all current Pods):
kubectl logs -l app=webapp --all-containers=true
# From a remote Node (debugging a kubelet):
kubectl debug node/<node> -n kube-system --image=busybox -- chroot /host ...
```

## Port-Forward (the "the network is fine" test)

`kubectl port-forward` lets you bypass Services + Ingress entirely and talk to the Pod **directly**:

```bash
kubectl port-forward svc/myapp 8080:80     # through the Service
kubectl port-forward pod/myapp-xyz 8080:80 # straight to the Pod
# Now: curl http://localhost:8080
```

If `port-forward` works but `curl myapp.default.svc.cluster.local` doesn't → it's **DNS or Service**, not the app.

## The Pod that won't give you a shell

If `kubectl exec myapp -it -- sh` fails (e.g., `no matching process`, or the container image is minimal/scratch), you need an **ephemeral container** — a second container injected into the running Pod for debugging.

### Ephemeral containers (debug containers)

```bash
kubectl debug myapp-pod-xyz \
  -it --image=busybox --target=app-container \
  -- sh
# Flags:
#  -it                          interactive shell
#  --image=busybox             debug image (has sh/ps/curl)
#  --target=app-container      share the app's namespaces (PID/IPC)
#  -- sh                       command to run in the debug container
```

This spawns a `busybox` container *inside* the existing Pod with shared PID, network, and IPC namespaces — so you can see the app's process tree and network state even if the app container is a scratch `FROM scratch` image.

**Note:** ephemeral containers require the `--enable-unsafe-output` gate on the API server (default on in modern clusters) and add a container you must remove later; the temporary Pod spec is not saved.

### Debug a Node's Pod from a Node

Two patterns for "I can't get in":

1. **From a fresh Pod on the same network** — replicate the source IP / service to test connectivity.
2. **Node-level debugging** — `kubectl debug node/<node> --image=busybox` gives a `hostNetwork: true` Pod with `/` chrooted into the host filesystem at `/host`, so you can inspect kubelet, the CNI, iptables, etc.

## Topology: where did my Pod go?

When you can't reach a Pod, rule out placement:

```bash
kubectl get pod $POD -o wide
# NAME           READY   STATUS    RESTARTS   AGE   IP           NODE     NOMINADO ...
kubectl get node $(kubectl get pod $POD -o jsonpath='{.spec.nodeName}')
kubectl describe node <node> | grep -A2 "Allocated resources"
```

## `kubectl auth can-i` (RBAC 403s)

```bash
# Can my ServiceAccount do X?
kubectl auth can-i get pods -n default \
  --as=system:serviceaccount:default:my-sa
# Equivalent to a 403 from the API for that SA.
```

A 403 from an in-cluster client is almost always a missing Role/RoleBinding or a typo in the ServiceAccount name.

## `kubectl explain` (the API for the API)

Can't remember whether the field is `image.repository` or `imageName`?

```bash
kubectl explain deployment.spec.template.spec.containers.image
# returns the exact field + description + "parent"
kubectl explain pod.spec --recursive | less
```

## Quick Diagnostics Checklist

```bash
NAME=<pod>; NS=<ns>
kubectl get pod $NAME -n $NS -o wide        # node + IP
kubectl describe pod $NAME -n $NS           # events → reason
kubectl logs $NAME -n $NS                  # current
kubectl logs -p $NAME -n $NS               # previous (crash)
kubectl top pod $NAME -n $NS               # CPU/Mem
kubectl get rs,deploy,svc -n $NS           # parent objects
kubectl get endpoints -n $NS               # Service → Pods?
kubectl run debug --image=busybox --rm -it --restart=Never -- sh
# Inside the debug Pod:
#   nslookup <svc>.<ns>.svc.cluster.local  → DNS
#   curl http://<svc>.<ns>.svc.cluster.local     → Service
#   ping <pod_ip>                              → Pod direct
```

## Interview Questions

**Q: A Pod is `Running` but unresponsive. Which `kubectl` command do you reach for first?**
A: `kubectl describe pod <pod>` — not `logs`, because a responsive-but-stuck Pod likely won't be logging. `describe` shows the recent Events (OOMKilled, evicted, liveness probe failures, node pressure) that explain the transition. If that's clean, `kubectl logs` (and `--previous`) reveal app errors, and `kubectl top pod` reveals CPU throttling or memory pressure.

**Q: What's the difference between `kubectl logs` and `kubectl logs -p`?**
A: Without `-p`, you get the **current** container instance's logs. With `-p` (or `--previous`), you get the logs from the **prior** container instance — i.e., the crashed one that emitted the failure. For `CrashLoopBackOff`, `-p` is usually the only way to see the actual error.

**Q: When would you use `kubectl port-forward` vs `kubectl exec`?**
A: `port-forward` exposes a Pod/Service locally so you can run `curl`/a browser from **outside** — great for testing reachability bypassing the Service (network troubleshooting). `exec` runs a command **inside** the Pod — great for `ps`, `netstat`, `cat /etc/hosts`, `sh` when the app image has a shell.

**Q: What is an ephemeral container and when do you need it?**
A: A debug container **injected into a running Pod** (shared PID/Network/IPC namespaces) so you can inspect a Pod whose image has no shell (e.g., `FROM scratch`). Use `kubectl debug <pod> -it --image=busybox --target=<app-container> -- sh`. It exists for the case `kubectl exec` returns `executable file not found` but the app is still running.

**Q: How do you confirm whether a ServiceAccount is properly bound to a Role?**
A: `kubectl auth can-i <verb> <resource> -n <ns> --as=system:serviceaccount:<ns>:<sa>` — it returns yes/no and is the fastest way to reproduce the 403 the in-cluster client saw.

## Related Resources

- [Troubleshooting Patterns](troubleshooting-patterns.md)
- [Cluster Operations](../08-cluster-operations/README.md)
- [Security](../06-security/README.md)
