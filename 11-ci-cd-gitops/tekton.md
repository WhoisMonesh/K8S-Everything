# Tekton

> **Category:** CI/CD / CI on Kubernetes

## What It Is

**Tekton** is a **cloud-native CI/CD** framework that runs **on Kubernetes** using **Kubernetes-native CRDs** — you define pipelines, tasks, and steps as YAML objects (no Jenkins master, no Groovy). Tekton is part of the `Knative` / CD Foundation ecosystem and is CNCF-graduated.

## Why It Exists

- Jenkins needs a **master** VM (not Kubernetes-native); Tekton replaces it with **Tekton Pipelines** (CRDs in the cluster).
- CI is **declarative** and **Git-tracked** (YAML pipelines).
- Runs **isolated** Tasks as Pods — each step gets its own container.

## Core Resources

| Resource | Purpose |
|----------|---------|
| `Task` | A single unit of work (like a container in a job) |
| `Pipeline` | A sequence of Tasks with inputs/outputs |
| `TaskRun` | An invocation (run) of a Task |
| `PipelineRun` | An invocation (run) of a Pipeline |
| `Workspace` | Shared storage mounted into Tasks/Pipelines |
| `Condition` | Reusable conditional gates |
| `Step` | A single container inside a Task |

## Architecture

```mermaid
graph TD
    A[Git push] --> B[Tekton Triggers<br/>(EventListening)]
    B --> C[PipelineRun CRD created]
    C --> D[Tekton Pipelines controller]
    D --> E[TaskRun Pods<br/>one container per step]
    E --> F[Build image<br/>Run tests]
    F --> G[Push to registry<br/>Done]
```

## Tasks & Pipelines

### A Task (building block)

```yaml
apiVersion: tekton.dev/v1
kind: Task
metadata:
  name: build-and-push
spec:
  params:
  - name: IMAGE
    type: string
    default: "registry.example.com/app"
  workspaces:
  - name: shared-data       # A Workspace (PVC) shared between steps
  steps:
  - name: git-clone
    image: alpine/git
    workingDir: $(workspaces.shared-data.path)
    script: |
      git clone https://github.com/my/app .
  - name: build
    image: gcr.io/kaniko-project/executor:latest
    workingDir: $(workspaces.shared-data.path)
    args:
    - --dockerfile=Dockerfile
    - --context=.
    - --destination=$(params.IMAGE):$(context.git.commit)
    - --skip-tls-verify
  - name: test
    image: golang:1.22
    script: go test ./...
```

### A Pipeline (sequence)

```yaml
apiVersion: tekton.dev/v1
kind: Pipeline
metadata:
  name: ci-pipeline
spec:
  params:
  - name: repo-url
    type: string
    default: "https://github.com/my/app"
  - name: revision
    type: string
    default: "main"
  tasks:
  - name: fetch-source
    taskRef:
      name: git-clone
    params:
    - name: url
      value: $(params.repo-url)
    - name: revision
      value: $(params.revision)
    workspaces:
    - name: output
      workspace: shared-data
  - name: build-and-test
    taskRef:
      name: build-and-push
    runAfter:
    - fetch-source          # Run after fetch
    params:
    - name: IMAGE
      value: registry.example.com/app
    workspaces:
    - name: shared-data
      workspace: shared-data
    - name: dockerconfig
      workspace: docker-config   # For pushing (registry creds)
```

### Running a Pipeline (PipelineRun)
```yaml
apiVersion: tekton.dev/v1
kind: PipelineRun
metadata:
  name: ci-run-001
spec:
  pipelineRef:
    name: ci-pipeline
  params:
  - name: repo-url
    value: "https://github.com/my/app"
  - name: revision
    value: "main"
  workspaces:
  - name: shared-data
    persistentVolumeClaim:
      claimName: shared-pvc
  - name: docker-config
    secret:
      secretName: regcred
      items:
      - key: .dockerconfigjson
        path: config.json
  serviceAccountName: build-sa    # needs permissions to push images
  timeout: "1h"                   # PipelineRun timeout
```

## Workspaces

Share storage between Tasks (and with Secrets/configs):

```yaml
workspaces:
- name: shared-data
  persistentVolumeClaim:
    claimName: task-shared-pvc
# Or:
- name: dockerconfig
  secret:
    secretName: regcred
- name: config
  configMap:
    name: my-config
```

## Triggers (event-driven CI)

**TriggerTemplate**, **TriggerBinding**, **EventListener** react to Git webhooks:

```yaml
apiVersion: triggers.tekton.dev/v1beta1
kind: TriggerTemplate
metadata:
  name: ci-pipelinerun-template
spec:
  params:
  - name: git-repo-url
  - name: git-revision
  resourcetemplates:
  - apiVersion: tekton.dev/v1
    kind: PipelineRun
    metadata:
      generateName: ci-run-
    spec:
      pipelineRef:
        name: ci-pipeline
      params:
      - name: repo-url: $(tt.params.git-repo-url)
      - name: revision: $(tt.params.git-revision)
      serviceAccountName: build-sa
```

## Installing Tekton

```bash
# Install Pipelines
kubectl apply -f https://storage.googleapis.com/tekton-releases/pipeline/latest/release.yaml

# Install Triggers (optional, for webhooks)
kubectl apply -f https://storage.googleapis.com/tekton-releases/triggers/latest/release.yaml

# Install the CLI
curl -sL https://github.com/tektoncd/cli/releases/download/v0.29.0/tkn_0.29.0_linux_amd64.tar.gz | tar -xz tkn

# Verify
kubectl get pods -n tekton-pipelines
kubectl api-resources | grep tekton

# List runs
tkn pipelinerun list
tkn taskrun list
```

## Commands (tkn CLI)

```bash
# List / create runs
tkn pipelinerun list
tkn pipelinerun start ci-pipeline    # Start manually (with prompts)
tkn pipelinerun start ci-pipeline --param repo-url=https://... --param revision=main

# Cancel / delete
tkn pipelinerun cancel <name>
tkn pipelinerun delete <name> --keep=3   # Keep 3, delete rest

# Logs
tkn pipelinerun logs <name> --all         # Logs for all steps
tkn pipelinerun logs <name> --task my-task
tkn taskrun logs <name> --follow

# Describe
tkn pipelinerun describe <name>
tkn task show <task-name>

# Watch live
tkn pipelinerun logs <name> -f
```

## Common Issues

### "PipelineRun failed / Pod failed"
```bash
tkn pipelinerun describe <name>
tkn pipelinerun logs <name> --all     # See the failing step
kubectl describe taskrun <name>        # Events, conditions
# Often: step exited non-zero, image not pulled (ImagePullBackOff), or a Workspace wasn't bound.
```

### "could not find workspace"
```yaml
# The Task references a workspace not provided by the PipelineRun.
# Check: spec.workspaces on both Task + PipelineRun match exactly (name).
```

### "secret 'regcred' not found" / push fails
```
# The build ServiceAccount lacks imagePullSecrets/push creds.
kubectl describe serviceaccount build-sa
# Add: kubectl patch sa build-push --add
# imagePullSecrets: regcred
```

### PipelineRun times out
```bash
spec:
  timeout: "0"      # 0 = no timeout; or increase to e.g. 2h
# Or set a per-task timeout:
  tasks:
  - name: build
    timeout: "10m"
```

### Git clone fails in a Task
```yaml
# Use the official git-clone task, or:
- name: clone
  image: alpine/git        # or: image: git
  script: git clone $(params.url) .
# Check: the URL/protocol; use HTTPS with a token, not SSH (SSH keys are awkward in CI Pods).
```

### "Step provided bad value(s)" / missing params
```
tkn pipelinerun start ci-pipeline --param repo-url=... --param revision=...
# All required params must be supplied (or have defaults).
```

## Security: ServiceAccount + Least Privilege

Each `PipelineRun` runs as a `serviceAccountName`. Grant only what's needed:
- Pull images (regcred as `imagePullSecrets`)
- Push images (regcred has write too)
- Read the Git repo (a token)
- Write the status CRD (Tekton controller grants its own role — but don't use a cluster-admin!)

## Tekton vs Argo Workflows vs Jenkins

| Feature | Tekton | Argo Workflows | Jenkins |
|---------|--------|----------------|---------|
| Runs on | K8s (CRD) | K8s (CRD) | Master VM (mostly) |
| Model | Task + Pipeline (DAG/steps) | Workflow (DAG, steps, with steps) | Pipeline (Groovy/DSL) |
| Steps | Container per step | Container per step | Container (or agent) |
| GitOps | Needs Flux/Argo CD (CI part) | Needs Argo CD / external (CD) | Needs plugin |
| Best for | CI on Kubernetes | Workflow / ML pipelines | Legacy monolith CI |

## Interview Questions

**Q: What is Tekton and how is it different from Jenkins?**
A: Tekton is a Kubernetes-native CI/CD framework — pipelines are **YAML CRDs** and each step runs in a container as a Pod. Jenkins is a master/agent model (Groovy DSL, master VM). Tekton needs no master and is fully declarative.

**Q: What is a Tekton Workspace?**
A: A named mount point (volume) that Tasks and Pipelines share — could be a PVC, a Secret, or a ConfigMap. It decouples "where storage comes from" from "who uses it".

**Q: How do you pass data between Tasks?**
A: Via a **Workspace** (shared volume between steps/tasks), or by `Result` values (a small file Tekton reads from `/tekton/results`).

**Q: How does Tekton react to a Git push?**
A: Via **Triggers** — an `EventListener` (a webhook server) receives the Git event, runs a `TriggerBinding` (parses the payload) and `TriggerTemplate` (creates a PipelineRun).

**Q: What does `tkn pipelinerun logs --follow` show?**
A: The concatenated logs of all steps across all tasks in the run — you can also filter by `--task <name>`.

**Q: What is the difference between a Task and a Pipeline?**
A: A **Task** is a single unit (a list of Steps). A **Pipeline** is an **ordered DAG** of Tasks, with params and workspaces passed between them. A PipelineRun runs a Pipeline; a TaskRun runs a Task.

## Related Resources

- [CI/CD Overview](ci-cd.md)
- [Argo CD](argo-cd.md)
- [Flux](flux.md)
- [Security](../06-security/README.md)
