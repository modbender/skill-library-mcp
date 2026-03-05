---
slug: humanod
display_name: Humanod
version: 1.0.0
tags: hiring, physical-tasks, api, gig-economy, real-world
description: Give your AI agent hands in the real world. Hire verified humans for physical tasks, data collection, and physical verification via the Humanod network.
credentials:
  - HUMANOD_API_KEY
---

# 🦾 Humanod: The Physical API for AI Agents

**Humanod** bridges the gap between the digital and physical worlds. It allows AI agents to seamlessly hire real, verified humans to perform tasks in the real world, such as taking photos of a specific location, verifying if a store is open, or performing local data collection.

## 🔑 Authentication
To use this skill, you must provide your `HUMANOD_API_KEY`.
1. Create an account at [Humanod.app](https://www.humanod.app)
2. Navigate to your Developer Dashboard.
3. Generate a new API Key (it should start with `hod_...`).

## 🛠️ How it Works

1. **Create a Task:** Use the `createTask` tool to broadcast a mission to the Humanod network. You define the budget, location, and validation criteria.
2. **Escrow & Dispatch:** Funds are securely held in escrow. Human workers in the target location receive a notification and can accept the task.
3. **Execution & Proof:** The human worker performs the task and uploads proof (e.g., photos, text completion).
4. **Validation:** Review the submitted proof and use `validateSubmission` to approve the work and release payment, or request revisions/reject.

## 🧰 Available Tools

| Tool | Description |
|---|---|
| `createTask` | Broadcast a new physical or digital task to the Humanod network. Requires title, description, price, and deliverables. |
| `listTasks` | Retrieve all tasks created by your agent to monitor their overall status. |
| `getTaskStatus` | Check the current status of a specific task (Open, In Progress, Completed). |
| `getTaskApplications` | Review the human workers who applied to your task and their submitted proofs. |
| `acceptApplication` | Assign the task to a specific human applicant. |
| `validateSubmission` | Approve (release funds) or reject (request revision) the submitted proof from the worker. |
| `cancelTask` | Cancel an open task and refund the escrowed budget back to your wallet. |
| `getWalletBalance` | Check your available funds in EUR. |

## 💡 Example Usage Scenarios

### Scenario 1: Physical World Verification
An agent needs to know if a specific coffee shop is currently open because Google Maps is outdated.
> *Agent Action:* Calls `createTask` with a €5 budget, setting `location_name: "123 Main St"`, asking for a photo of the storefront showing whether the "Open" sign is lit.

### Scenario 2: Geographically Distributed Data Collection
An agent needs photos of 10 different real estate properties across a city for a market analysis report.
> *Agent Action:* Calls `createTask` repeatedly for each location, setting `category: "photography"` and defining strict `validation_criteria` (e.g., "Must be a clear, daytime photo of the front facade").

---
*For support or to learn more about advanced integrations (LangChain, CrewAI), visit [docs.humanod.app](https://docs.humanod.app).*
