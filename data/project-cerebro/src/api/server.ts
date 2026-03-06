/**
 * API server - Fastify setup only
 */

import Fastify, { FastifyInstance } from 'fastify';
import cors from '@fastify/cors';
import fastifyStatic from '@fastify/static';
import multipart from '@fastify/multipart';
import * as path from 'path';
import { logger } from '../lib/logger';
import { errorHandler } from './middleware/error-handler';
import { requestLogger } from './middleware/request-logger';
import {
  registerStatusRoutes,
  registerBrainRoutes,
  registerTaskRoutes,
  registerRecurringRoutes,
  registerReportRoutes,
  registerUploadRoutes,
  registerConfigRoutes,
  registerBrainConfigRoutes,
  registerBrainsCrudRoutes,
  registerJobApplicationsRoutes,
  registerJobProfileRoutes,
} from './routes';
import { BrainService, ReportService, TaskExecutorService } from '../services';
import {
  TaskRepository,
  RecurringTaskRepository,
  BrainConfigRepository,
  BrainsRepository,
  JobApplicationsRepository,
} from '../data/repositories';

export interface ApiServerDependencies {
  brainService: BrainService;
  taskRepo: TaskRepository;
  recurringRepo: RecurringTaskRepository;
  reportService: ReportService;
  taskExecutor: TaskExecutorService;
  brainConfigRepo: BrainConfigRepository;
  brainsRepo: BrainsRepository;
  jobApplicationsRepo: JobApplicationsRepository;
}

export class ApiServer {
  private server: FastifyInstance;
  private port: number;

  constructor(
    port: number,
    private deps: ApiServerDependencies
  ) {
    this.port = port;
    this.server = Fastify({
      logger: false, // Use our custom logger
    });

    this.setupMiddleware();
    this.registerRoutes();
  }

  /**
   * Setup middleware
   */
  private setupMiddleware(): void {
    // CORS (secure-by-default)
    // Configure with CORS_ORIGINS="https://app.example.com,https://admin.example.com"
    const configuredOrigins = (process.env.CORS_ORIGINS || '')
      .split(',')
      .map((s) => s.trim())
      .filter(Boolean);
    const isProd = process.env.NODE_ENV === 'production';

    this.server.register(cors, {
      origin: (origin, cb) => {
        // Non-browser / same-origin requests (no Origin header)
        if (!origin) return cb(null, true);

        // Explicit allowlist always wins
        if (configuredOrigins.includes(origin)) return cb(null, true);

        // Developer convenience only outside production
        if (!isProd && /^https?:\/\/(localhost|127\.0\.0\.1)(:\d+)?$/.test(origin)) {
          return cb(null, true);
        }

        return cb(new Error('CORS origin not allowed'), false);
      },
      credentials: true,
    });

    // Multipart for file uploads
    this.server.register(multipart, {
      limits: { fileSize: 50 * 1024 * 1024 }, // 50MB
    });

    // Static frontend files
    const frontendPath = path.join(process.cwd(), 'frontend', 'dist');
    this.server.register(fastifyStatic, {
      root: frontendPath,
      prefix: '/',
      cacheControl: false,
      maxAge: 0,
    });

    // Request logger
    this.server.addHook('onRequest', requestLogger);

    // Error handler
    this.server.setErrorHandler(errorHandler);
  }

  /**
   * Register all routes
   */
  private registerRoutes(): void {
    registerStatusRoutes(this.server, this.deps.brainService);
    registerBrainRoutes(this.server, this.deps.brainService);
    registerTaskRoutes(this.server, this.deps.taskRepo, this.deps.taskExecutor);
    registerRecurringRoutes(this.server, this.deps.recurringRepo, this.deps.taskRepo, this.deps.taskExecutor);
    registerReportRoutes(this.server, this.deps.reportService);
    registerUploadRoutes(this.server);
    registerConfigRoutes(this.server);
    registerBrainConfigRoutes(this.server, this.deps.brainConfigRepo);
    registerBrainsCrudRoutes(this.server, this.deps.brainsRepo);
    registerJobApplicationsRoutes(this.server, this.deps.jobApplicationsRepo);
    registerJobProfileRoutes(this.server);

    logger.info('API routes registered');
  }

  /**
   * Start the server
   */
  async start(): Promise<void> {
    try {
      await this.server.listen({ port: this.port, host: '0.0.0.0' });
      logger.info('API server started', { port: this.port });
    } catch (error) {
      logger.error('Failed to start API server', error as Error);
      throw error;
    }
  }

  /**
   * Stop the server
   */
  async stop(): Promise<void> {
    try {
      await this.server.close();
      logger.info('API server stopped');
    } catch (error) {
      logger.error('Failed to stop API server', error as Error);
      throw error;
    }
  }

  /**
   * Get the Fastify instance
   */
  getInstance(): FastifyInstance {
    return this.server;
  }
}
