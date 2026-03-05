# FinOps Principles

The 6 FinOps Principles act as a north star, guiding all activities of a FinOps practice. These principles should be taken as a whole and practiced together.

## 1. Teams Need to Collaborate

**Core concept**: Finance, technology, product, and business teams work together in near real-time as the cloud operates on a per-resource, per-second basis.

**Key behaviors**:
- Cross-functional teams meet regularly to review cloud spend
- Engineers understand financial impacts of their decisions
- Finance understands technical constraints and opportunities
- Product teams balance cost with feature velocity
- Teams work together to continuously improve efficiency and innovation

**Anti-patterns**:
- Siloed decision-making about cloud resources
- Finance setting budgets without engineering input
- Engineers deploying without cost awareness
- Blame culture around cost overruns

## 2. Business Value Drives Technology Decisions

**Core concept**: Unit economic and value-based metrics demonstrate business impact better than aggregate spend.

**Key behaviors**:
- Make conscious trade-off decisions among cost, quality, and speed
- Think of cloud as a driver of innovation, not just a cost center
- Measure cost per business outcome (cost per transaction, per user, per revenue dollar)
- Connect cloud spending to business KPIs
- Consider FinOps Scopes as drivers of business value

**Anti-patterns**:
- Focusing solely on reducing spend without considering value
- Treating all cloud costs as expenses to minimize
- Not connecting infrastructure costs to business outcomes
- Over-optimizing at the expense of innovation velocity

## 3. Everyone Takes Ownership for Their Technology Usage

**Core concept**: Accountability of usage and cost is pushed to the edge, with engineers taking ownership of costs from architecture design to ongoing operations.

**Key behaviors**:
- Individual feature and product teams manage their own cloud usage against their budget
- Decentralized decision making around cost-effective architecture and resource usage
- Engineers consider cost as a new efficiency metric from the beginning of the software development lifecycle
- Teams are empowered with visibility and tools to optimize their own spend
- Ownership is clear through proper tagging and allocation

**Anti-patterns**:
- Central IT solely responsible for cloud costs
- Engineers unaware of cost implications
- "Tragedy of the commons" with shared resources
- No accountability for cost overruns at the team level

## 4. FinOps Data Should Be Accessible, Timely, and Accurate

**Core concept**: Real-time visibility autonomously drives better cloud and technology utilization.

**Key behaviors**:
- Process and share cost data as soon as it becomes available
- Fast feedback loops result in more efficient behavior
- Consistent visibility into cloud spend is provided to all levels of the organization
- Create, monitor, and improve real-time financial forecasting and planning
- Trending and variance analysis helps explain why costs increased
- Internal team benchmarking drives best practices and celebrates wins
- Industry peer-level benchmarking assesses company performance

**Anti-patterns**:
- Monthly or quarterly reporting delays
- Data locked in finance systems, inaccessible to engineers
- Inconsistent cost data across different tools/reports
- Inaccurate allocation making data untrustworthy

## 5. FinOps Should Be Enabled Centrally

**Core concept**: A central FinOps team encourages, evangelizes, and enables best practices in a shared accountability model.

**Key behaviors**:
- Central team sets standards and provides tools/training
- Rate, commitment, and discount optimization are centralized to take advantage of economies of scale
- Remove the need for engineers to think about rate negotiations
- Executive buy-in for FinOps and its practices is secured
- Central team doesn't own all costs, but enables cost ownership

**Comparison to security model**:
- Just like security, there's a central team establishing best practices
- Everyone remains responsible for their portion of technology use
- Central team provides expertise, tooling, and governance
- Distributed teams implement and maintain compliance

**Anti-patterns**:
- No central FinOps function or expertise
- Fully decentralized commitment purchasing (leaves money on the table)
- Central team trying to own all cost decisions
- Lack of executive sponsorship

## 6. Take Advantage of the Variable Cost Model of the Cloud

**Core concept**: The variable cost model of the cloud should be viewed as an opportunity to deliver more value, not as a risk.

**Key behaviors**:
- Embrace just-in-time prediction, planning, and purchasing of capacity
- Agile iterative planning is preferred over static long-term plans
- Embrace proactive system design with continuous adjustments in cloud optimization
- Scale resources with demand rather than over-provisioning
- Treat commitments as investments, not guarantees

**Anti-patterns**:
- Treating cloud like a data center with fixed capacity
- Over-committing to reduce variability risk
- Static annual planning without adjustment capability
- Fear of variable spend leading to over-provisioning

## Applying the Principles

When making FinOps decisions, validate against all principles:

| Decision | Principle Check |
|----------|-----------------|
| Buying 3-year RIs | Does it align with variable cost model? Is there business value? |
| New tagging strategy | Will everyone take ownership? Is data accessible? |
| Centralized vs distributed tools | Is FinOps enabled centrally while teams own their usage? |
| Cost reduction target | Does business value drive this? Are teams collaborating? |

## Principle Tensions

Sometimes principles may appear to conflict:

- **Centralized enablement vs. distributed ownership**: Central team enables, distributed teams own
- **Variable cost model vs. commitment discounts**: Commit to stable baseline, keep variability for growth
- **Speed vs. cost optimization**: Make conscious trade-offs, don't sacrifice all value for savings
