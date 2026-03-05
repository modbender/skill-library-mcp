import { describe, expect, it, vi } from "vitest";
import { TickTickOAuth2Client } from "../../src/auth/index.js";
import { TickTickApiError, TickTickApiTimeoutError } from "../../src/api/index.js";
import { createTickTickRuntimeFromEnv, createTickTickUseCases } from "../../src/core/index.js";
import { TickTickDomainError } from "../../src/shared/error-categories.js";

describe("core module", () => {
  it("creates TickTick task payloads from domain input", async () => {
    const post = vi.fn(async (_path: string, body?: unknown) => ({
      id: "task-1",
      projectId: "proj-1",
      title: "Write docs",
      content: (body as { content?: string }).content,
      desc: (body as { desc?: string }).desc,
      status: 0,
    }));

    const useCases = createTickTickUseCases({
      createTask: vi.fn(async (input) => ({
        id: "task-1",
        projectId: input.projectId,
        title: input.title,
        content: input.content,
        description: input.description,
        status: "active",
      })),
    } as any);

    const created = await useCases.createTask.execute({
      projectId: "proj-1",
      title: "Write docs",
      description: "Details",
      content: "Content",
      priority: 3,
    });

    expect(created.title).toBe("Write docs");
  });

  it("updates task through gateway flow", async () => {
    const updateTask = vi.fn(async (input) => ({
      id: input.taskId,
      projectId: "proj-1",
      title: "Refine plan",
      dueDate: input.dueDate,
      priority: input.priority,
      status: "active",
    }));

    const useCases = createTickTickUseCases({ updateTask } as any);

    await useCases.updateTask.execute({
      taskId: "task-2",
      dueDate: "2026-02-20T09:00:00.000Z",
      priority: 5,
    });

    expect(updateTask).toHaveBeenCalled();
  });

  it("maps domain failures to core-level error categories", async () => {
    const useCases = createTickTickUseCases({
      listProjects: vi.fn(async () => {
        throw new TickTickDomainError({
          category: "rate_limit_429",
          message: "Rate limit",
          status: 429,
          retriable: true,
        });
      }),
      createTask: vi.fn(async () => {
        throw new TickTickDomainError({
          category: "network",
          message: "Timeout",
          retriable: true,
        });
      }),
    } as any);

    await expect(useCases.listProjects.execute()).rejects.toMatchObject({
      category: "rate_limit_429",
      retriable: true,
      status: 429,
    });

    await expect(
      useCases.createTask.execute({
        projectId: "proj-1",
        title: "A",
      })
    ).rejects.toMatchObject({
      category: "network",
      retriable: true,
    });
  });

  it("creates full runtime from env source factory", () => {
    const runtime = createTickTickRuntimeFromEnv({
      envSource: {
        TICKTICK_CLIENT_ID: "client-1",
        TICKTICK_CLIENT_SECRET: "secret-1",
        TICKTICK_REDIRECT_URI: "http://localhost:3000/oauth/callback",
        TICKTICK_USER_AGENT: "ticktick-skills-test",
      },
      getAccessToken: () => "access-token-1",
    });

    expect(runtime.oauth2Client).toBeInstanceOf(TickTickOAuth2Client);
    expect(runtime.gateway).toBeDefined();
    expect(runtime.apiClient).toBeDefined();
    expect(runtime.useCases).toBeDefined();
  });
});
