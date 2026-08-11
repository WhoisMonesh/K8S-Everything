# Pod Security Context — Running Pods Safer

> **Category:** Security / Pod Hardening

The **`securityContext`** (pod-level + container-level) is the knob that controls **which user a container runs as, what Linux capabilities it has, whether it can escalate privileges, which SELinux/AppArmor/seccomp profile it uses, and whether its root filesystem is read-only**. Pod Security Admission (`15-advanced-patterns/pod-patterns`... no, `pod-security-admission.md`) is the *namespace-wide policy* layer on top; `securityContext` is the per-Pod opt-in.

> `PodSecurityAdmission` says "no privileged Pods in `prod`". `securityContext` is how a Pod *opts out of defaults* (e.g. drops `ALL` capabilities) or *opts in safely* (runs as non-root).

## Pod-level vs Container-level

- **`spec.securityContext`** (pod) applies to **all** containers + pods fields (`fsGroup`, `runAsUser`, `fsGroupChangePolicy`, `runAsGroup`, `seLinuxOptions`, `seccompProfile`, `windowsOptions`, `supplementalGroups`, `sysctfs`).
- **`spec.containers[].securityContext`** (container) applies per container and **overrides** only itself (`allowPrivilegeEscalation`, `privileged`, `procMount`, `readOnlyRootFilesystem`, `runAs...`, `seLinuxOptions`, `seccompProfile`, `apparmorProfile`, capabilities).

## Core fields

| Field | Scope | Notes |
|-------|-------|-------|
| `runAsNonRoot: true` | pod/cont | fails to start if the image's `USER` is `root`. |
| `runAsUser` / `runAsGroup` / `fsGroup` | pod | explicit UID/GID (e.g. `1000` / `3000` / `2000`). |
| `fsGroupChangePolicy` | pod | `OnRootMismatch` (default) vs `Recursive` — perf of `chcon` on big volumes. |
| `allowPrivilegeEscalation: false` | container | the strongest single hardening bit — blocks `setuid` + `CAP_NET_RAW` abuse. |
| `privileged: false` | container | must be false (never default-true); enables host device access. |
| `readOnlyRootFilesystem: true` | container | root FS immutable; only writable paths are explicit `emptyDir`/`volumeMounts`. |
| `capabilities.add/drop` | container | add `NET_BIND_SERVICE`; drop `ALL` to start minimal. |
| `seccompProfile.type` | pod/cont | `RuntimeDefault`, `Localhost` (needs path), `LocalhostProfile`, `Unconfined` (never). |
| `apparmorProfile.type` | pod/cont | `runtime/default`, `localhost/myprofile`, `unconfined`. |
| `procMount: Default` | container | `Unmasked` is a risk — leaves `/proc/{pid}/` host-visible. |

## A locked-down container, step by step

```yaml
apiVersion: v1
kind: Pod
metadata: { name: app-locked }
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    runAsGroup: 3000
    fsGroup: 2000
    seccompProfile:
      type: RuntimeDefault
  containers:
  - name: app
    image: my/app:1.2
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop: ["ALL"]          # start from nothing
        add: ["NET_BIND_SERVICE"]   # only what you need
    volumeMounts:
    - name: tmp
      mountPath: /tmp
  volumes:
  - name: tmp
    emptyDir: {}
```

## Seccomp

- `type: RuntimeDefault` = the container runtime's default profile (blocks `keyctl`, `ptrace`, `mount`, etc.) — **use it almost always**.
- `type: Localhost` with `localhostProfile: profiles/audit.json` = a custom syscall profile. The profile file is placed in the kubelet's `/var/lib/kubelet/seccomp/` (or via the `runtime/default` seccomp of the CRI).
- `: true` is **unconfined** — effectively off. Never use in prod.

```bash
# Inspect a pod's current seccomp/apparmor:
kubectl get pod app -o jsonpath='{.spec.securityContext.seccompProfile}'
kubectl get pod app -o jsonpath='{.spec.containers[0].securityContext}'
```

## AppArmor

- `runtime/default` = the runtime default (most secure; Docker's default profile).
- `localhost/name` loads a profile from the node's `/etc/apparmor.d/`. Requires the kubelet `--allowed-unsafe-sysctls`... no: the node must have the profile installed and the API server must allow it.
- Profiles are applied via **annotations** on older API and via `securityContext.apparmorProfile` on modern K8s.

## Sysctls

Two classes:
- **Namespaced** (safe): `net.ipv4.ip_local_port_range`, `fs.inotify.max_user_watches`, `kernel.shm_rmid_forced`, `net.core.somaxconn` — set via `pod.spec.sysctfs`.
- **Node-wide** (unsafe): `kernel.modules`, `net.ipv4.ip_forward` — requires opt-in on the API server (`--allowed-unsafe-sysctfs`) + kubelet.

```yaml
sysctfs:
- name: net.core.somaxconn
  value: "4096"
- name: fs.file-max
  value: "100000"
```

## Common Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| `container must not be privileged` | `privileged: true` with PSP/PSA `restricted` | remove it; use capabilities only |
| `must run as non-root` / container exits | `runAsNonRoot` true but image `USER root` | set `USER 1000` in the image or `runAsUser` |
| Seccomp syscall denied | `RuntimeDefault` blocks a needed syscall (e.g. some Java/JVM) | switch to `LocalhostProfile` with a tailored profile, or narrow the image |
| AppArmor `profile not found` | profile not installed on the node | install in `/etc/apparmor.d/`, restart kubelet |
| Sysctl `not allowed` | node-wide unsafe sysctl | add to API-server `--allowed-unsafe-sysctls` (rare) |
| Volume permission denied | `fsGroup` mismatch with the app | set `fsGroup` to the volume's expected GID, or `fsGroupChangePolicy: OnRootMismatch` |

## Interview Questions

**Q: What single field is the strongest pod hardening?**
A: `allowPrivilegeEscalation: false` at the container level — it blocks `setuid` binaries and CAP_NET_RAW-based privilege escalation, which is how most container escapes work. Pair with `runAsNonRoot: true`, `readOnlyRootFilesystem: true`, and `capabilities.drop: ["ALL"]`.

**Q: What's the difference between a seccomp profile of `RuntimeDefault` and `Unconfined`?**
A: `RuntimeDefault` applies the container runtime's default syscall allowlist (blocks `ptrace`, `mount`, `keyctl`, etc.) — a strong baseline. `Unconfined` disables seccomp entirely (same as no profile) — only for debugging; never in prod.

**Q: How does Pod Security Admission interact with `securityContext`?**
A: PSA (`privileged`/`baseline`/`restricted` at the namespace) is the **default deny** policy. `securityContext` is the **explicit opt-in** per Pod/container. A `restricted` namespace + a Pod with `runAsNonRoot` + `RuntimeDefault` seccomp + dropped capabilities = defense in depth.

## Related Resources
- [Pod Security Admission](pod-security-admission.md)
- [Pod Security Policies (legacy)](podsecuritypolicy.md)
- [Admission Controllers](admission-controllers.md)
- [Secrets](secrets.md)
- [Pod Patterns](../15-advanced-patterns/pod-patterns.md)
