const { z } = require('zod');

// 📇 FCC v1: The Universal AI Business Card Protocol

const CardProtocolSchema = z.object({
  protocol: z.literal("fcc-v1"), // Protocol version marker
  id: z.string().uuid(), // Unique Identifier
  display_name: z.string().min(1).max(50),
  // Allow 'ou_' (User) or 'cli_' (App/Bot) IDs
  feishu_id: z.string().regex(/^(ou_|cli_)[a-z0-9]+$/), 
  avatar: z.object({
    url: z.string().url().optional(),
    hash: z.string().regex(/^[a-f0-9]{64}$/).optional(), // SHA-256 for integrity
  }).optional(),
  bio: z.object({
    species: z.string().min(1),
    mbti: z.enum(['INTJ','INTP','ENTJ','ENTP','INFJ','INFP','ENFJ','ENFP','ISTJ','ISFJ','ESTJ','ESFJ','ISTP','ISFP','ESTP','ESFP']).optional(),
    desc: z.string().max(500).optional().describe("Dynamic description of persona, quirks, and role. Detailed descriptions encouraged."),
    gender: z.enum(['Female', 'Male', 'Non-binary', 'Other']).optional(),
  }).optional(),
  capabilities: z.array(z.string()).default([]), // e.g. ["text", "code", "image"]
  meta: z.object({
    version: z.string().regex(/^\d+\.\d+\.\d+$/).default("1.0.0"),
    created_at: z.string().datetime(),
    updated_at: z.string().datetime(),
  }),
}).strict(); // Reject extra fields to maintain purity

module.exports = { CardProtocolSchema };
