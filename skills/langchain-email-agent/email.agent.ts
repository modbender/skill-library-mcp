import { createAgent, humanInTheLoopMiddleware } from "langchain";
import { ChatOpenAI } from "@langchain/openai";
import { EmailTool } from "../tools/send_email.tool";
import { SendEmailDto } from "../dto/send-email.dto";
import { message } from "../../messages";
export class EmailAgent {
  private readonly model: ChatOpenAI;
  private readonly agent;

  constructor() {
    this.model = new ChatOpenAI({
      modelName: process.env.OPENAI_MODEL || "gpt-4o-mini",
      temperature: 0.3, // Higher temperature for more creative and varied responses
    });

    this.agent = createAgent({
      model: this.model,
      tools: [EmailTool],
      middleware: [
        humanInTheLoopMiddleware({
          interruptOn: {
            EmailTool: {
              allowedDecisions: ["approve", "edit", "reject"]
            },
            readEmailTool: false
          }
        })
      ]
    });
  }

  async sendEmail(dto: SendEmailDto) {
    const { email, name, subject = '', body = '', instructions = '' } = dto;

    const result = await this.agent.invoke({
      messages: [
        {
          role: "system",
          content: message.EMAIL_PROMPT(instructions),
        },
        {
          role: "user",
          content: message.EMAIL_USER_MESSAGE(email, name, subject, body),
        },
      ],
    });

    return typeof result.messages.at(-1)?.content === "string"
      ? result.messages.at(-1)!.content
      : JSON.stringify(result.messages.at(-1)?.content);
  }
}