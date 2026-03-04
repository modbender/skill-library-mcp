// Cold email sequence — customize for your ICP
// Lead variables available: {{firstName}}, {{companyName}}

module.exports = {

  email1: {
    subject: "your store is leaving hours on the table every week",
    body: (lead) => `Hi {{firstName}},

I looked at {{companyName}} — you're running a real store, which means someone on your team is probably spending 3-5 hours a day on things that should be automatic: order routing, supplier submissions, tracking updates, stock alerts.

We fix that. [Your Company] builds e-commerce automation systems that take those exact workflows off your plate in under 30 days.

Worth a 30-min call to see if your store has the same wins available?

→ [YOUR BOOKING LINK]

— [Your Name]
[Your Company]
`,
  },

  email2: {
    subject: "Re: your store is leaving hours on the table every week",
    delayDays: 3,
    body: (lead) => `Hi {{firstName}},

Just following up — wanted to make sure this didn't get buried.

Quick question: what's the most manual, repetitive task your team deals with right now? Order processing? Inventory? Supplier coordination?

Happy to share how we've handled it in a 30-min call.

→ [YOUR BOOKING LINK]

— [Your Name]
`,
  },

  email3: {
    subject: "last one from me",
    delayDays: 5,
    body: (lead) => `Hi {{firstName}},

Won't keep following up after this — I know your inbox is busy.

But if {{companyName}} ever hits a point where the manual ops are slowing growth, we're the team to call.

The free audit link stays open: [YOUR BOOKING LINK]

Good luck.

— [Your Name]
`,
  },

};
