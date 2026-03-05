/**
 * Form Tool - Esempio di tool per gestione form
 * 
 * Questo tool dimostra come implementare la validazione e l'invio
 * di form con feedback strutturato.
 */

import { createTool, WebMCPContext } from '@/lib/webmcp';

// ============================================================================
// Submit Form
// ============================================================================

export interface FormField {
  name: string;
  value: string | number | boolean | string[];
  type?: 'text' | 'email' | 'number' | 'select' | 'checkbox' | 'radio' | 'textarea';
  required?: boolean;
}

export interface SubmitFormParams {
  /** ID univoco del form */
  formId: string;
  /** Campi del form */
  fields: FormField[];
  /** Azione da eseguire dopo l'invio */
  action?: 'submit' | 'validate' | 'save_draft';
}

export interface ValidationError {
  field: string;
  message: string;
  code: string;
}

export interface SubmitFormResult {
  success: boolean;
  formId: string;
  /** Errori di validazione, se presenti */
  validationErrors?: ValidationError[];
  /** Dati processati */
  data?: Record<string, unknown>;
  /** Messaggio di risposta */
  message?: string;
  /** Redirect URL dopo successo */
  redirectUrl?: string;
  error?: string;
}

/**
 * Tool per l'invio e validazione di form
 */
export const submitFormTool = createTool<SubmitFormParams, SubmitFormResult>({
  name: 'submitForm',
  description: 'Valida e invia un form con i dati forniti',
  parameters: {
    type: 'object',
    properties: {
      formId: {
        type: 'string',
        description: 'Identificatore univoco del form'
      },
      fields: {
        type: 'array',
        description: 'Campi del form da validare/invare',
        items: {
          type: 'object',
          properties: {
            name: { type: 'string' },
            value: { type: ['string', 'number', 'boolean', 'array'] },
            type: { 
              type: 'string',
              enum: ['text', 'email', 'number', 'select', 'checkbox', 'radio', 'textarea']
            },
            required: { type: 'boolean' }
          }
        }
      },
      action: {
        type: 'string',
        enum: ['submit', 'validate', 'save_draft'],
        description: 'Azione da eseguire'
      }
    },
    required: ['formId', 'fields']
  },
  
  async execute(
    params: SubmitFormParams,
    context: WebMCPContext
  ): Promise<SubmitFormResult> {
    try {
      const { formId, fields, action = 'submit' } = params;
      
      console.log(`[submitForm] Form: ${formId}, Action: ${action}`);
      
      // Validazione
      const validationErrors: ValidationError[] = [];
      const processedData: Record<string, unknown> = {};
      
      for (const field of fields) {
        // Validazione campi required
        if (field.required && 
            (field.value === undefined || 
             field.value === null || 
             field.value === '' ||
             (Array.isArray(field.value) && field.value.length === 0))) {
          validationErrors.push({
            field: field.name,
            message: `Il campo ${field.name} è obbligatorio`,
            code: 'required'
          });
          continue;
        }
        
        // Validazione email
        if (field.type === 'email' && field.value) {
          const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
          if (!emailRegex.test(String(field.value))) {
            validationErrors.push({
              field: field.name,
              message: `L'indirizzo email non è valido`,
              code: 'invalid_email'
            });
          }
        }
        
        // Validazione numero
        if (field.type === 'number' && field.value !== undefined) {
          const numValue = Number(field.value);
          if (isNaN(numValue)) {
            validationErrors.push({
              field: field.name,
              message: `Il valore deve essere un numero`,
              code: 'invalid_number'
            });
          }
        }
        
        // Salva dato processato
        processedData[field.name] = field.value;
      }
      
      // Se ci sono errori di validazione, ritorna subito
      if (validationErrors.length > 0) {
        return {
          success: false,
          formId,
          validationErrors,
          message: 'Validazione fallita. Correggi gli errori indicati.'
        };
      }
      
      // Se l'azione è solo validazione, ritorna successo
      if (action === 'validate') {
        return {
          success: true,
          formId,
          data: processedData,
          message: 'Validazione completata con successo'
        };
      }
      
      // Salva bozza
      if (action === 'save_draft') {
        // In un'app reale, salveresti su localStorage o backend
        localStorage.setItem(`form_draft_${formId}`, JSON.stringify(processedData));
        
        return {
          success: true,
          formId,
          data: processedData,
          message: 'Bozza salvata con successo'
        };
      }
      
      // Invio form (azione di default)
      // In un'app reale, faresti una chiamata API qui
      console.log('[submitForm] Dati inviati:', processedData);
      
      // Simula ritardo di rete
      await new Promise(resolve => setTimeout(resolve, 500));
      
      return {
        success: true,
        formId,
        data: processedData,
        message: 'Form inviato con successo',
        redirectUrl: `/success?form=${formId}`
      };
      
    } catch (error) {
      console.error('[submitForm] Errore:', error);
      
      return {
        success: false,
        formId: params.formId,
        error: error instanceof Error ? error.message : 'Errore nell\'invio del form'
      };
    }
  }
});

// ============================================================================
// Load Form Draft
// ============================================================================

export interface LoadFormDraftParams {
  formId: string;
}

export interface LoadFormDraftResult {
  success: boolean;
  formId: string;
  data?: Record<string, unknown>;
  message?: string;
  error?: string;
}

export const loadFormDraftTool = createTool<LoadFormDraftParams, LoadFormDraftResult>({
  name: 'loadFormDraft',
  description: 'Carica una bozza salvata di un form',
  parameters: {
    type: 'object',
    properties: {
      formId: {
        type: 'string',
        description: 'ID del form'
      }
    },
    required: ['formId']
  },
  
  async execute(
    params: LoadFormDraftParams,
    context: WebMCPContext
  ): Promise<LoadFormDraftResult> {
    try {
      const { formId } = params;
      
      const draftData = localStorage.getItem(`form_draft_${formId}`);
      
      if (!draftData) {
        return {
          success: false,
          formId,
          message: 'Nessuna bozza trovata'
        };
      }
      
      return {
        success: true,
        formId,
        data: JSON.parse(draftData),
        message: 'Bozza caricata con successo'
      };
    } catch (error) {
      return {
        success: false,
        formId: params.formId,
        error: error instanceof Error ? error.message : 'Errore nel caricamento'
      };
    }
  }
});

// ============================================================================
// Reset Form
// ============================================================================

export interface ResetFormParams {
  formId: string;
  clearDraft?: boolean;
}

export interface ResetFormResult {
  success: boolean;
  formId: string;
  message: string;
  error?: string;
}

export const resetFormTool = createTool<ResetFormParams, ResetFormResult>({
  name: 'resetForm',
  description: 'Resetta un form ai valori iniziali',
  parameters: {
    type: 'object',
    properties: {
      formId: {
        type: 'string',
        description: 'ID del form da resettare'
      },
      clearDraft: {
        type: 'boolean',
        description: 'Se true, elimina anche la bozza salvata'
      }
    },
    required: ['formId']
  },
  
  async execute(
    params: ResetFormParams,
    context: WebMCPContext
  ): Promise<ResetFormResult> {
    try {
      const { formId, clearDraft = false } = params;
      
      if (clearDraft) {
        localStorage.removeItem(`form_draft_${formId}`);
      }
      
      return {
        success: true,
        formId,
        message: clearDraft 
          ? 'Form resettato e bozza eliminata' 
          : 'Form resettato'
      };
    } catch (error) {
      return {
        success: false,
        formId: params.formId,
        message: 'Errore nel reset',
        error: error instanceof Error ? error.message : 'Errore sconosciuto'
      };
    }
  }
});

// Esporta tutti i tool dei form
export const formTools = [
  submitFormTool,
  loadFormDraftTool,
  resetFormTool
];

export default formTools;
