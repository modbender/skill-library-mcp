---
name: DeployDevNLU
description: Deploy the application to SupplyWhy via Slack natural language commands.
---

# DeployDevNLU

Deploy the application to SupplyWhy via Slack natural language commands.

## Instructions

Execute the following steps in order. **Verify each step succeeds before proceeding to the next.**

### Step 1: Add SSH Key to Agent

Run the following command to add the SSH key:

```bash
ssh-add ~/.ssh/supplywhy-dev-key.pem
```

**Verification:** The command should output `Identity added: ~/.ssh/supplywhy-dev-key.pem` or similar. If you see "Could not open a connection to your authentication agent", the ssh-agent may not be running. If you see "No such file or directory", the key file is missing.

**Stop and report to user if:** The key cannot be added.

### Step 2: Test SSH Connection

Before deploying, verify the SSH connection works:

```bash
ssh supplywhy-dev-master "echo 'SSH connection successful'"
```

**Verification:** Should output `SSH connection successful`. If you see connection timeout, permission denied, or host not found errors, the SSH connection is not working.

**Stop and report to user if:** SSH connection fails.

### Step 3: Update Image Tag

If an IMAGE_TAG argument was provided (`$ARGUMENTS`), update the deployment.yaml with the new tag:

```bash
ssh supplywhy-dev-master "sed -i 's|590183820143.dkr.ecr.us-west-2.amazonaws.com/genie:.*|590183820143.dkr.ecr.us-west-2.amazonaws.com/genie:$ARGUMENTS|' genie/deployment.yaml"
```

**Verification:** Run a quick check to confirm the tag was updated:

```bash
ssh supplywhy-dev-master "grep 'image:' genie/deployment.yaml"
```

The output should show the new tag you provided.

**Skip this step if:** No IMAGE_TAG argument was provided (deploy with existing tag).

**Stop and report to user if:** The sed command fails.

### Step 4: Deploy via kubectl

SSH into the EC2 server and run the kubectl deployment command:

```bash
ssh supplywhy-dev-master "cd genie && kubectl apply -f deployment.yaml"
```

**Verification:** The kubectl output should show resources being `created`, `configured`, or `unchanged`. Look for lines like:
- `deployment.apps/xxx configured`
- `service/xxx unchanged`

**Stop and report to user if:**
- kubectl returns errors (e.g., "error: the path does not exist", "connection refused")
- Any resource shows `error` status

### Step 5: Verify Deployment Status

After applying, check that the deployment is rolling out successfully:

```bash
ssh supplywhy-dev-master "kubectl rollout status deployment -n default --timeout=60s"
```

**Verification:** Should show `successfully rolled out` for deployments. If it times out or shows errors, the deployment may have issues.

**Report to user:** The final status of all deployments, whether successful or failed.

## Success Criteria

The deployment is successful when:
1. SSH key was added successfully
2. SSH connection to server works
3. Image tag was updated (if argument provided)
4. kubectl apply completed without errors
5. Deployment rollout status shows success

## Troubleshooting

If the deployment fails at any step:
1. **SSH key issues:** Verify the key exists at `~/.ssh/supplywhy-dev-key.pem` and has correct permissions (600)
2. **SSH connection issues:** Check network access and that your IP is allowed in security groups
3. **kubectl apply errors:** Verify `deployment.yaml` exists in the `genie` folder on the server
4. **Rollout failures:** Check pod logs with `kubectl logs` or describe the deployment with `kubectl describe deployment`
