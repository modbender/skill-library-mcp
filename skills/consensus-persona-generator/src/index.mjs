import crypto from 'node:crypto';
import { generatePersonas } from './llm.mjs';
import { validateInput } from './validate.mjs';
import { getLatestPersonaSet, readBoardPolicy, writeArtifact, resolveStatePath } from 'consensus-guard-core';

const MAX_PERSONAS = 9;

function okReuse(existing, input) {
  if (!existing) return false;
  const sameN = existing.personas?.length === input.n_personas;
  const samePack = (existing.meta?.persona_pack || '') === (input.persona_pack || '');
  const sameDomain = (existing.meta?.domain || '') === (input.task_context?.domain || '');
  return sameN && samePack && sameDomain;
}

function err(board_id, code, message, details = {}) {
  return { board_id, error: { code, message, details } };
}

export async function handler(input, opts = {}) {
  const board_id = input?.board_id;
  const statePath = resolveStatePath(opts);

  try {
    const validationError = validateInput(input);
    if (validationError) return err(board_id || '', 'INVALID_INPUT', validationError);
    const n_personas = Math.min(MAX_PERSONAS, Math.max(1, Number(input.n_personas || 5)));
    const persona_pack = input.persona_pack || 'founder';

    await readBoardPolicy(board_id, statePath); // loaded for parity, defaults handled in caller skill
    const latest = await getLatestPersonaSet(board_id, statePath);
    if (!input.force_regenerate && okReuse(latest, { n_personas, persona_pack, task_context: input.task_context || {} })) {
      return {
        board_id,
        persona_set_id: latest.persona_set_id,
        created_at: latest.created_at,
        personas: latest.personas,
        board_write: { success: true, artifact_ref: latest.artifact_ref || 'reused' }
      };
    }

    const personas = await generatePersonas({
      task_context: input.task_context || {},
      n_personas,
      persona_pack
    });

    const persona_set_id = crypto.randomUUID();
    const created_at = new Date().toISOString();
    const payload = {
      board_id,
      persona_set_id,
      created_at,
      personas,
      meta: {
        persona_pack,
        n_personas,
        domain: input.task_context?.domain || ''
      }
    };

    const write = await writeArtifact(board_id, 'persona_set', payload, statePath);
    return {
      board_id,
      persona_set_id,
      created_at,
      personas,
      board_write: {
        success: true,
        artifact_ref: write.artifact_ref
      }
    };
  } catch (e) {
    return err(board_id || '', 'PERSONA_GENERATOR_FAILED', e.message || 'unknown error');
  }
}

export async function invoke(input, opts = {}) {
  return handler(input, opts);
}
