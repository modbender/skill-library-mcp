# Theoretical Foundations

## 1. Compression Progress (Schmidhuber, 2008)

**Core idea:** Curiosity = reward from learning speed.

An agent's intrinsic reward is proportional to the improvement in its ability to compress
(predict) its experience. Formally:

```
reward(t) = L(t-1) - L(t)
```

where L is the agent's prediction loss.

**Implications for inference-time curiosity:**
- Pursue topics where you learn the most per unit effort
- Already-known topics → boring (no compression gain)
- Purely random/noisy topics → also boring (incompressible)
- "Sweet spot" = topics at the edge of your knowledge

**Operationalization:** In the OODA-C loop, Protocol A (Self-Ask) targets this by generating
questions ranked by expected information gain. The question most likely to change your answer
is the one with highest compression progress potential.

## 2. Free Energy Principle & Active Inference (Friston, 2010)

**Core idea:** Self-organizing systems minimize variational free energy (prediction error).

But pure minimization leads to "dark room problem" — hide from all stimulation.
Active Inference resolves this: agents don't just update beliefs passively, they
**act to sample information** that reduces expected future uncertainty.

```
G = E_q[log q(s) - log p(o,s)] = Complexity - Accuracy
```

**Two types of action:**
1. Pragmatic: achieve goals (exploit)
2. Epistemic: reduce uncertainty (explore) ← this is curiosity

**Expected Information Gain (EIG):**
```
EIG = KL[p(s|o,a) || p(s|a)] = expected reduction in uncertainty from action a
```

**Operationalization:** Protocol C (Gap Map) identifies ❌ UNKNOWN items.
The ACT step then selects actions (tool calls) that maximize EIG —
prioritizing gaps where filling them would most change the response.

## 3. Bayesian Surprise (Itti & Baldi, 2005)

**Core idea:** Surprise = magnitude of belief update.

```
Surprise = KL[p(model|data) || p(model)]  (posterior vs prior)
```

Not the same as Shannon surprise (unexpectedness of data).
Bayesian surprise measures how much your **worldview changed**.

**Key distinction:**
- Shannon surprise: "I didn't expect that data point" (measures data)
- Bayesian surprise: "That data changed my beliefs" (measures model update)

A rare but irrelevant event has high Shannon surprise but low Bayesian surprise.
A common-seeming fact that overturns an assumption has low Shannon but high Bayesian surprise.

**Operationalization:** The Surprise Detector behavior triggers on information that
changes the agent's hypothesis (= high Bayesian surprise), not just unusual facts.
Protocol B (Devil's Advocate) generates alternative models, making belief updates
more likely by creating competing hypotheses.

## 4. Information Gap Theory (Loewenstein, 1994)

**Core idea:** Curiosity is a form of cognitively-induced deprivation.

It arises when you become aware of a gap between what you know and what you want to know.
The gap creates an aversive feeling that motivates information-seeking behavior.

**Key properties:**
- Curiosity increases with existing knowledge (you need to know enough to know what you don't know)
- Small gaps are more motivating than large ones (achievable resolution)
- Curiosity is involuntary once the gap is perceived

**Operationalization:** Protocol C (Gap Map) makes information gaps explicit and visible.
The categorization of KNOWN/ASSUMED/UNKNOWN forces awareness of gaps.
The "One More Step Rule" maintains curiosity pressure even when the agent is ready to stop.

## 5. Empowerment (Klyubin et al., 2005)

**Core idea:** Intrinsic motivation = maximizing channel capacity between actions and future states.

```
Empowerment = max I(A; S') = max mutual information between action and future state
```

An empowered agent seeks states where it has the most options and influence.

**Relevance to curiosity:** Curious exploration leads to knowledge, which leads to
more effective future actions (= higher empowerment). An agent that explores builds
a better world model, giving it more capacity to achieve arbitrary future goals.

**Operationalization:** The Open Thread Tracker preserves curiosity seeds across sessions,
maintaining future exploration options. This is a form of empowerment — keeping the
possibility space open rather than collapsing it prematurely.

## Unified View

All five theories converge on the same computational principle:

**Curiosity = seeking information that maximally updates your model of the world.**

The differences are in framing:
- Schmidhuber: frames it as compression/learning speed
- Friston: frames it as free energy minimization via epistemic action
- Itti/Baldi: frames it as posterior-prior divergence
- Loewenstein: frames it as gap-induced motivation
- Klyubin: frames it as future option maximization

For inference-time implementation, the practical result is the same:
1. Detect what you don't know (gap detection)
2. Estimate which gaps matter most (information gain)
3. Act to fill them (tool use)
4. Notice when your beliefs change (surprise detection)
5. Generate new questions (open threads)

This is exactly what the OODA-C loop implements.
