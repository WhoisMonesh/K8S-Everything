# Exam Day Checklist

> **Category:** Interview Preparation / Certification

The exam env is locked down, so prepare your terminal beforehand and never leave a question stuck.

## 15 minutes before you start
- [ ] Browser tab open on the **only** allowed site: `kubernetes.io/docs` + `github.com/kubernetes/*`.
- [ ] Terminal aliases ready:
  ```bash
  alias k='kubectl'
  export do='--dry-run=client -o yaml'
  source <(kubectl completion bash)
  ```
- [ ] `kubectl config use-context` set to the right cluster.

## During the exam (per question)
1. Read once, note the pass criteria (kind / namespace / labels).
2. Generate YAML with `k create ... --dry-run=client -o yaml` -> redirect to file -> `vi`/`sed`.
3. Apply, then verify: `kubectl get <kind> <name> -o yaml` + `kubectl describe`.
4. Mark it done. **Never leave a question stuck** — come back later if needed.
5. End sweep: `kubectl get pods,svc,deploy,pvc -A -o wide`.

## Gotchas that waste time
- The in-exam `kubectl` may be older; don't use apiVersions introduced in newer releases.
- Tab completion works for resources, not for `--namespace`/`--context` -> type them.
- `kubectl apply -f -` reads from stdin (paste a manifest).
- No internet from the cluster: `kubectl run busybox --image=busybox` only works with a cached image.

## Related
- [CKA](cka.md) · [CKAD](ckad.md) · [CKS](cks.md)
