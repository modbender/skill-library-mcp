# MindGraph 18 Tools API Reference

All tools are accessible via the `mindgraph-client.js` library.

## 1. Reality Layer

### `mg.ingest(label, content, action, opts)`
- **action**: `'source'`, `'snippet'`, `'observation'`
- **opts**: `{ sourceUid, medium, url, timestamp, confidence, salience }`

### `mg.manageEntity(opts)`
- **action**: `'create'`, `'alias'`, `'resolve'`, `'fuzzy_resolve'`, `'merge'`
- **opts**: `{ label, entityType, text, canonicalUid, aliasScore, keepUid, mergeUid, limit }`

## 2. Epistemic Layer

### `mg.addArgument(opts)`
- **opts**: `{ claim: {label, content}, evidence: [{label, description}], warrant: {label, principle}, argument: {label, summary} }`

### `mg.addInquiry(label, content, action, opts)`
- **action**: `'hypothesis'`, `'theory'`, `'paradigm'`, `'anomaly'`, `'assumption'`, `'question'`, `'open_question'`
- **opts**: `{ status, anomalousToUid, assumesUid, testsUid, addressesUid, confidence, salience }`

### `mg.addStructure(label, content, action, opts)`
- **action**: `'concept'`, `'pattern'`, `'mechanism'`, `'model'`, `'analogy'`, `'theorem'`, `'equation'`
- **opts**: `{ summary, analogousToUid, transfersToUid, evaluatesUid, outperformsUid, chainSteps, derivedFromUid, provenByUid }`

## 3. Intent Layer

### `mg.addCommitment(label, description, action, opts)`
- **action**: `'goal'`, `'project'`, `'milestone'`
- **opts**: `{ priority, status, parentUid, dueDate, motivatedByUid }`

### `mg.deliberate(opts)`
- **action**: `'open_decision'`, `'add_option'`, `'add_constraint'`, `'resolve'`
- **opts**: `{ label, description, decisionUid, chosenOptionUid, resolutionRationale, constraintType, blocksUid }`

## 4. Action Layer

### `mg.procedure(opts)`
- **action**: `'create_flow'`, `'add_step'`, `'add_affordance'`, `'add_control'`
- **opts**: `{ label, description, flowUid, stepOrder, previousStepUid, affordanceType, controlType, goalUid }`

### `mg.risk(opts)`
- **action**: `'assess'`, `'get_assessments'`
- **opts**: `{ label, description, assessedUid, severity, likelihood, mitigations, residualRisk }`

## 5. Memory Layer

### `mg.sessionOp(opts)`
- **action**: `'open'`, `'trace'`, `'close'`
- **opts**: `{ label, focus, sessionUid, traceContent, traceType, relevantNodeUids }`

### `mg.distill(label, content, opts)`
- **opts**: `{ sessionUid, summarizesUids, importance }`

### `mg.memoryConfig(opts)`
- **action**: `'set_preference'`, `'set_policy'`, `'get_preferences'`, `'get_policies'`
- **opts**: `{ type, label, key, value, policyContent }`

## 6. Agent Layer

### `mg.plan(opts)`
- **action**: `'create_task'`, `'create_plan'`, `'add_step'`, `'update_status'`
- **opts**: `{ label, description, goalUid, taskUid, planUid, stepOrder, targetUid, status }`

### `mg.governance(opts)`
- **action**: `'create_policy'`, `'set_budget'`, `'request_approval'`, `'resolve_approval'`
- **opts**: `{ label, policyContent, budgetType, budgetLimit, governedUid, approvalUid, approved, resolutionNote }`

### `mg.execution(opts)`
- **action**: `'start'`, `'complete'`, `'fail'`, `'register_agent'`
- **opts**: `{ label, planUid, executorUid, executionUid, outcome, producesNodeUid, errorDescription, agentName, agentRole }`

## 7. Connective Tissue

### `mg.retrieve(action, opts)`
- **action**: `'text'`, `'semantic'`, `'active_goals'`, `'open_questions'`, `'weak_claims'`, `'pending_approvals'`, `'layer'`, `'recent'`
- **opts**: `{ query, k, threshold, layer, nodeTypes, limit, offset }`

### `mg.traverse(mode, startUid, opts)`
- **mode**: `'chain'`, `'neighborhood'`, `'path'`, `'subgraph'`
- **opts**: `{ endUid, maxDepth, direction, edgeTypes, weightThreshold }`

### `mg.evolve(action, uid, opts)`
- **action**: `'update'`, `'tombstone'`, `'restore'`, `'decay'`, `'history'`, `'snapshot'`
- **opts**: `{ label, summary, confidence, propsPatch, reason, cascade, halfLifeSecs, minSalience, version }`
