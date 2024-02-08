# Job Execution System - Master Node Subsystem

The master node in the Job Execution System accepts benchmark jobs from the Data Management System. Once a new job
arrives, the scheduler in the master node estimates the resource requirements and then assigns the job to an available
host in the cluster of worker nodes.

We assign jobs to workers using a **greedy algorithm**: starting from the job with the largest memory requirement,
we send it to the worker with the largest available memory which is also larger than the required amount.

## Prerequisites

This system requires **Java Runtime Environment(JRE)** or **Java Development Kit(JDK)** (version == `1.8` or `1.11`).

## Run

Please use the following command to run the system with the pre-built JAR package.

```bash
java -jar deployment/mgmt-api-1.0.0-RELEASE.jar 
```

## Build From Source

See [build.md](build.md) for instructions on building the package from source.
