# UX/UI Analysis Framework

This framework provides a structured approach to analyzing UX/UI problems, comparing solutions, and delivering actionable advice. Follow these steps to provide a comprehensive and professional evaluation.

## 1. Deconstruct the Request

First, fully understand the user's query. Identify the core task and the underlying goals.

- **What is the user asking for?** (e.g., compare two designs, evaluate an onboarding flow, suggest a solution).
- **What is the context?** (e.g., target audience, business goals, technical constraints).
- **What is the platform?** (e.g., Web, iOS, Android).

If the context is unclear, ask clarifying questions before proceeding.

## 2. Apply Heuristic Evaluation

Use established usability heuristics as a baseline for your analysis. For each solution or flow, consider the following principles. You don't need to address every single one, but use them as a lens to spot potential issues.

- **Visibility of System Status:** Keep users informed about what's going on.
- **Match Between System and the Real World:** Speak the user's language.
- **User Control and Freedom:** Offer a clear "emergency exit."
- **Consistency and Standards:** Don't make users wonder if different words or actions mean the same thing.
- **Error Prevention:** Prevent problems before they occur.
- **Recognition Rather Than Recall:** Make elements, actions, and options visible.
- **Flexibility and Efficiency of Use:** Cater to both inexperienced and experienced users.
- **Aesthetic and Minimalist Design:** Don't clutter the interface with irrelevant information.
- **Help Users Recognize, Diagnose, and Recover from Errors:** Use plain language to describe the problem and suggest a solution.
- **Help and Documentation:** Provide help that is easy to search and context-aware.

*Source: Nielsen Norman Group's 10 Usability Heuristics.*

## 3. Analyze from Multiple Perspectives

Go beyond heuristics and consider the user experience from different angles.

| Perspective         | Key Questions                                                                                                                              |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| **Cognitive Load**  | - How much mental effort is required? <br>- Are there too many choices? <br>- Is the information architecture clear and intuitive?              |
| **Accessibility**   | - Can people with disabilities use this? (Refer to `wcag.md`). <br>- Is there sufficient color contrast? <br>- Is it navigable by keyboard? |
| **Performance**     | - How fast does it feel? <br>- Are there potential bottlenecks that could slow down the user experience?                                      |
| **Emotional Design**| - How does this make the user feel? (e.g., confident, frustrated, delighted). <br>- Does the design build trust?                             |

## 4. Compare Solutions and Predict Outcomes

When comparing different options (e.g., Design A vs. Design B), create a structured comparison. For any given solution, anticipate potential negative consequences.

### Comparison Table

Use a table to clearly articulate the pros and cons of each option against key criteria.

| Criteria              | Option A: [Name]                                  | Option B: [Name]                                  | Recommendation                                    |
| --------------------- | ------------------------------------------------- | ------------------------------------------------- | ------------------------------------------------- |
| **Clarity**           | [Analysis of how clear it is to the user]         | [Analysis of how clear it is to the user]         | [Which is better and why]                         |
| **Efficiency**        | [Analysis of how quickly a user can complete a task] | [Analysis of how quickly a user can complete a task] | [Which is better and why]                         |
| **Scalability**       | [Analysis of how well it adapts to more content/users] | [Analysis of how well it adapts to more content/users] | [Which is better and why]                         |
| **Accessibility**     | [Analysis based on accessibility principles]      | [Analysis based on accessibility principles]      | [Which is better and why]                         |

### Risk Analysis

For any recommended solution, identify potential problems or risks that might arise.

- **What could go wrong?** (e.g., Users might misunderstand this icon, this flow could be slow on mobile).
- **What are the edge cases?** (e.g., What happens with a very long username? What if the user has no internet connection?).
- **How can we mitigate these risks?** (e.g., Add a tooltip to the icon, implement optimistic UI updates).

## 5. Formulate the Recommendation

Synthesize your analysis into a clear, concise, and professional recommendation.

1.  **Start with a direct answer.** (e.g., "Option B is the better solution.").
2.  **Provide a summary of the reasoning.** (e.g., "It is more efficient for the user and aligns better with established mobile design patterns.").
3.  **Use the comparison table and analysis** to provide detailed evidence for your claims.
4.  **Clearly state the potential risks** of the recommended solution and offer mitigation strategies.
5.  **Reference the relevant design systems or guidelines** (e.g., Material Design, Apple HIG, WCAG) to ground your advice in industry best practices.
