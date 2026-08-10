# Architecture

> [Back to Index](../README.md)

## Overview

Kubernetes components, how the control plane interacts with workers, and the underlying runtime layer.

## Component Files

| Component | File |
|---------|------|
| [Kubernetes Architecture](architecture.md) | Full architecture overview |
| [kube-apiserver](kube-apiserver.md) | API server and authentication |
| [etcd](etcd.md) | State storage |
| [kube-scheduler](kube-scheduler.md) | Pod placement |
| [kube-controller-manager](kube-controller-manager.md) | Controllers |
| [cloud-controller-manager](cloud-controller-manager.md) | Cloud integrations |
| [kubelet](kubelet.md) | Node agent |
| [kube-proxy](kube-proxy.md) | Network proxy |
| [Container Runtimes](container-runtimes.md) | Runtime comparison |
| [CNCF Landscape](cncf-landscape.md) | Ecosystem overview |

## Quick Reference

| Component | Type | Runs On | Purpose |
|-----------|------|---------|---------|
| kube-apiserver | Control plane | Master | API entry point |
| etcd | Control plane | Master | State store |
| kube-scheduler | Control plane | Master | Scheduling |
| kube-controller-manager | Control plane | Master | Controllers |
| cloud-controller-manager | Control plane | Master | Cloud provider |
| kubelet | Worker | Node | Node agent |
| kube-proxy | Worker | Node | Network rules |
| Container runtime | Worker | Node | Container lifecycle |

[Back to Index](../README.md)
