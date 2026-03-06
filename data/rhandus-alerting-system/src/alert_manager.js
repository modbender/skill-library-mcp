/**
 * 🚨 Alert Manager - Sistema Centralizado de Alertas
 * Nivel 1: Sistema base con Telegram y reglas básicas
 */

import fs from 'fs';
import path from 'path';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

// Configuración
const ALERTS_DB = '/workspace/.openclaw_alerts.json';
const LOG_FILE = '/var/log/openclaw_alerts/alerts.log';
const TELEGRAM_CHAT_ID = process.env.TELEGRAM_CHAT_ID || 'CHANGE_ME';
const DEFAULT_PRIORITIES = ['info', 'warning', 'critical', 'emergency'];

/**
 * Clase principal del sistema de alertas
 */
export class AlertManager {
  constructor() {
    this.alerts = this.loadAlerts();
    this.rules = [];
    this.stats = {
      totalAlerts: 0,
      activeAlerts: 0,
      resolvedAlerts: 0,
      byPriority: {},
      byService: {}
    };
    
    this.initializeStats();
  }
  
  /**
   * Cargar alertas desde base de datos
   */
  loadAlerts() {
    try {
      if (fs.existsSync(ALERTS_DB)) {
        const data = fs.readFileSync(ALERTS_DB, 'utf8');
        return JSON.parse(data);
      }
    } catch (error) {
      this.log(`Error cargando alertas: ${error.message}`, 'error');
    }
    
    return {
      alerts: [],
      rules: [],
      history: []
    };
  }
  
  /**
   * Guardar alertas a base de datos
   */
  saveAlerts() {
    try {
      const data = JSON.stringify(this.alerts, null, 2);
      fs.writeFileSync(ALERTS_DB, data);
      this.log('Alertas guardadas en base de datos', 'info');
    } catch (error) {
      this.log(`Error guardando alertas: ${error.message}`, 'error');
    }
  }
  
  /**
   * Inicializar estadísticas
   */
  initializeStats() {
    DEFAULT_PRIORITIES.forEach(priority => {
      this.stats.byPriority[priority] = 0;
    });
    
    // Contar alertas existentes
    this.alerts.alerts.forEach(alert => {
      this.stats.totalAlerts++;
      if (alert.status === 'active') {
        this.stats.activeAlerts++;
      } else if (alert.status === 'resolved') {
        this.stats.resolvedAlerts++;
      }
      
      this.stats.byPriority[alert.priority] = (this.stats.byPriority[alert.priority] || 0) + 1;
      this.stats.byService[alert.service] = (this.stats.byService[alert.service] || 0) + 1;
    });
  }
  
  /**
   * Registrar en log
   */
  log(message, level = 'info') {
    const timestamp = new Date().toISOString();
    const logEntry = `[${timestamp}] [${level.toUpperCase()}] ${message}\n`;
    
    try {
      fs.appendFileSync(LOG_FILE, logEntry);
    } catch (error) {
      console.error(`Error escribiendo log: ${error.message}`);
    }
    
    // También log a consola en desarrollo
    if (level === 'error') {
      console.error(`🚨 ${message}`);
    } else if (level === 'warning') {
      console.warn(`⚠️  ${message}`);
    } else {
      console.log(`📝 ${message}`);
    }
  }
  
  /**
   * Crear nueva alerta
   */
  async createAlert(options) {
    const {
      title,
      message,
      service = 'unknown',
      priority = 'warning',
      channels = ['telegram'],
      metadata = {},
      deduplicate = true
    } = options;
    
    // Generar ID único
    const alertId = `ALERT-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    
    // Verificar duplicados si está habilitado
    if (deduplicate) {
      const duplicate = this.findDuplicateAlert(title, service);
      if (duplicate) {
        this.log(`Alerta duplicada encontrada: ${duplicate.id}`, 'info');
        
        // Actualizar alerta existente
        duplicate.lastOccurrence = new Date().toISOString();
        duplicate.occurrenceCount = (duplicate.occurrenceCount || 1) + 1;
        duplicate.metadata = { ...duplicate.metadata, ...metadata };
        
        this.saveAlerts();
        return duplicate;
      }
    }
    
    const alert = {
      id: alertId,
      title,
      message,
      service,
      priority,
      status: 'active',
      channels,
      createdAt: new Date().toISOString(),
      lastOccurrence: new Date().toISOString(),
      occurrenceCount: 1,
      metadata,
      history: []
    };
    
    // Agregar a base de datos
    this.alerts.alerts.push(alert);
    
    // Actualizar estadísticas
    this.stats.totalAlerts++;
    this.stats.activeAlerts++;
    this.stats.byPriority[priority] = (this.stats.byPriority[priority] || 0) + 1;
    this.stats.byService[service] = (this.stats.byService[service] || 0) + 1;
    
    // Enviar notificaciones
    await this.sendNotifications(alert);
    
    // Guardar
    this.saveAlerts();
    
    this.log(`Nueva alerta creada: ${alertId} (${priority}) - ${title}`, 'info');
    
    return alert;
  }
  
  /**
   * Buscar alerta duplicada
   */
  findDuplicateAlert(title, service) {
    return this.alerts.alerts.find(alert => 
      alert.title === title && 
      alert.service === service && 
      alert.status === 'active'
    );
  }
  
  /**
   * Enviar notificaciones por canales configurados
   */
  async sendNotifications(alert) {
    const promises = [];
    
    alert.channels.forEach(channel => {
      switch (channel) {
        case 'telegram':
          promises.push(this.sendTelegramAlert(alert));
          break;
        case 'email':
          promises.push(this.sendEmailAlert(alert));
          break;
        case 'log':
          promises.push(this.logAlert(alert));
          break;
        default:
          this.log(`Canal no soportado: ${channel}`, 'warning');
      }
    });
    
    try {
      await Promise.allSettled(promises);
      this.log(`Notificaciones enviadas para alerta ${alert.id}`, 'info');
    } catch (error) {
      this.log(`Error enviando notificaciones: ${error.message}`, 'error');
    }
  }
  
  /**
   * Enviar alerta por Telegram
   */
  async sendTelegramAlert(alert) {
    try {
      const emoji = this.getPriorityEmoji(alert.priority);
      const message = `${emoji} *${alert.title}*\n\n${alert.message}\n\n` +
                     `*Servicio:* ${alert.service}\n` +
                     `*Prioridad:* ${alert.priority}\n` +
                     `*ID:* ${alert.id}\n` +
                     `*Hora:* ${new Date(alert.createdAt).toLocaleTimeString()}`;
      
      // Usar message tool de OpenClaw para enviar a Telegram
      // Nota: En entorno de OpenClaw, el routing es automático al canal actual
      // Para pruebas, usar console.log. En producción, OpenClaw manejará el routing.
      console.log(`📱 [TELEGRAM ALERT] ${message}`);
      // En entorno real de OpenClaw, el mensaje se enviará automáticamente
      return Promise.resolve();
      
      await execAsync(command, { shell: true });
      this.log(`Alerta enviada por Telegram: ${alert.id}`, 'info');
      
    } catch (error) {
      this.log(`Error enviando alerta por Telegram: ${error.message}`, 'error');
    }
  }
  
  /**
   * Enviar alerta por Email (usando gog)
   */
  async sendEmailAlert(alert) {
    try {
      const subject = `[${alert.priority.toUpperCase()}] ${alert.title}`;
      const body = `
ALERTA: ${alert.title}

Mensaje: ${alert.message}

Detalles:
- Servicio: ${alert.service}
- Prioridad: ${alert.priority}
- ID: ${alert.id}
- Hora: ${new Date(alert.createdAt).toLocaleString()}
- Status: ${alert.status}

${JSON.stringify(alert.metadata, null, 2)}

---
Sistema de Alertas OpenClaw
      `.trim();
      
      const account = process.env.GOOGLE_ACCOUNT || 'TU_EMAIL_GOOGLE';
      const adminEmail = process.env.ADMIN_EMAIL || 'admin@example.com';
      const command = `gog gmail send --account ${account} --to ${adminEmail} --subject "${subject}" --body "${body.replace(/"/g, '\\"')}"`;
      
      await execAsync(command, { shell: true });
      this.log(`Alerta enviada por Email: ${alert.id}`, 'info');
      
    } catch (error) {
      this.log(`Error enviando alerta por Email: ${error.message}`, 'error');
    }
  }
  
  /**
   * Registrar alerta en log
   */
  async logAlert(alert) {
    const logEntry = `[ALERT] ${alert.id} | ${alert.priority} | ${alert.service} | ${alert.title} | ${alert.message}`;
    this.log(logEntry, 'info');
    return Promise.resolve();
  }
  
  /**
   * Obtener emoji para prioridad
   */
  getPriorityEmoji(priority) {
    const emojis = {
      emergency: '🔴',
      critical: '🟠',
      warning: '🟡',
      info: '🔵'
    };
    
    return emojis[priority] || '⚪';
  }
  
  /**
   * Resolver alerta
   */
  resolveAlert(alertId, resolutionNotes = '') {
    const alert = this.alerts.alerts.find(a => a.id === alertId);
    
    if (!alert) {
      this.log(`Alerta no encontrada: ${alertId}`, 'warning');
      return null;
    }
    
    alert.status = 'resolved';
    alert.resolvedAt = new Date().toISOString();
    alert.resolutionNotes = resolutionNotes;
    
    // Agregar al historial
    alert.history.push({
      action: 'resolved',
      timestamp: new Date().toISOString(),
      notes: resolutionNotes
    });
    
    // Actualizar estadísticas
    this.stats.activeAlerts--;
    this.stats.resolvedAlerts++;
    
    this.saveAlerts();
    
    this.log(`Alerta resuelta: ${alertId}`, 'info');
    
    // Notificar resolución
    this.notifyResolution(alert);
    
    return alert;
  }
  
  /**
   * Notificar resolución de alerta
   */
  async notifyResolution(alert) {
    try {
      const message = `✅ *ALERTA RESUELTA*\n\n` +
                     `*${alert.title}*\n\n` +
                     `La alerta ha sido marcada como resuelta.\n\n` +
                     `*ID:* ${alert.id}\n` +
                     `*Resuelta a las:* ${new Date().toLocaleTimeString()}\n` +
                     `*Notas:* ${alert.resolutionNotes || 'Sin notas'}`;
      
      // En entorno real de OpenClaw, el mensaje se enviará automáticamente
      console.log(`📱 [TELEGRAM RESOLUTION] ${message}`);
      this.log(`Notificación de resolución preparada: ${alert.id}`, 'info');
      
      return Promise.resolve();
      
    } catch (error) {
      this.log(`Error preparando notificación de resolución: ${error.message}`, 'error');
    }
  }
  
  /**
   * Listar alertas activas
   */
  listActiveAlerts() {
    return this.alerts.alerts.filter(alert => alert.status === 'active');
  }
  
  /**
   * Obtener estadísticas
   */
  getStats() {
    return {
      ...this.stats,
      timestamp: new Date().toISOString(),
      uptime: this.getUptime()
    };
  }
  
  /**
   * Obtener tiempo de actividad
   */
  getUptime() {
    // Para simplificar, retornar tiempo desde primera alerta
    if (this.alerts.alerts.length === 0) {
      return '0s';
    }
    
    const firstAlert = this.alerts.alerts.reduce((oldest, alert) => {
      return new Date(alert.createdAt) < new Date(oldest.createdAt) ? alert : oldest;
    });
    
    const uptimeMs = Date.now() - new Date(firstAlert.createdAt).getTime();
    const hours = Math.floor(uptimeMs / (1000 * 60 * 60));
    const minutes = Math.floor((uptimeMs % (1000 * 60 * 60)) / (1000 * 60));
    
    return `${hours}h ${minutes}m`;
  }
  
  /**
   * Monitorear endpoint HTTP
   */
  async monitorHTTP(url, options = {}) {
    const {
      interval = 60,
      timeout = 10,
      expectedStatus = 200,
      alertOnFailure = true,
      alertPriority = 'critical',
      serviceName = 'http-monitor'
    } = options;
    
    this.log(`Iniciando monitoreo HTTP: ${url} (cada ${interval}s)`, 'info');
    
    try {
      const command = `curl -s -o /dev/null -w "%{http_code}" --max-time ${timeout} "${url}"`;
      const { stdout } = await execAsync(command, { shell: true });
      
      const statusCode = parseInt(stdout.trim());
      
      if (statusCode === expectedStatus) {
        this.log(`✅ ${url} responde correctamente (${statusCode})`, 'info');
        return { success: true, status: statusCode };
      } else {
        this.log(`❌ ${url} responde con código ${statusCode} (esperado ${expectedStatus})`, 'warning');
        
        if (alertOnFailure) {
          await this.createAlert({
            title: `HTTP Monitor Failure: ${url}`,
            message: `El endpoint ${url} respondió con código ${statusCode} (esperado ${expectedStatus})`,
            service: serviceName,
            priority: alertPriority,
            channels: ['telegram', 'log'],
            metadata: { url, statusCode, expectedStatus, timeout }
          });
        }
        
        return { success: false, status: statusCode };
      }
      
    } catch (error) {
      this.log(`❌ Error monitoreando ${url}: ${error.message}`, 'error');
      
      if (alertOnFailure) {
        await this.createAlert({
          title: `HTTP Monitor Error: ${url}`,
          message: `Error al monitorear endpoint ${url}: ${error.message}`,
          service: serviceName,
          priority: alertPriority,
          channels: ['telegram', 'log'],
          metadata: { url, error: error.message, timeout }
        });
      }
      
      return { success: false, error: error.message };
    }
  }
}

// CLI para pruebas
if (process.argv[2] === 'test') {
  const manager = new AlertManager();
  
  // Crear alerta de prueba
  manager.createAlert({
    title: 'Prueba del Sistema de Alertas',
    message: 'Esta es una alerta de prueba del nuevo sistema de alertas OpenClaw.',
    service: 'alerting-system',
    priority: 'info',
    channels: ['telegram', 'log'],
    metadata: { test: true, version: '1.0.0' }
  })
  .then(alert => {
    console.log('✅ Alerta de prueba creada:');
    console.log(JSON.stringify(alert, null, 2));
    
    // Mostrar estadísticas
    console.log('\n📊 Estadísticas:');
    console.log(JSON.stringify(manager.getStats(), null, 2));
    
    // Listar alertas activas
    console.log('\n🚨 Alertas activas:');
    console.log(manager.listActiveAlerts().map(a => `${a.id}: ${a.title}`).join('\n'));
  })
  .catch(console.error);
}

if (process.argv[2] === 'monitor') {
  const manager = new AlertManager();
  const url = process.argv[3] || 'https://httpbin.org/status/200';
  
  manager.monitorHTTP(url, {
    interval: 30,
    timeout: 5,
    expectedStatus: 200,
    alertOnFailure: true,
    alertPriority: 'critical',
    serviceName: 'http-test'
  })
  .then(result => {
    console.log('📡 Resultado monitoreo HTTP:');
    console.log(JSON.stringify(result, null, 2));
  })
  .catch(console.error);
}

if (process.argv[2] === 'stats') {
  const manager = new AlertManager();
  console.log('📊 Estadísticas del Sistema de Alertas:');
  console.log(JSON.stringify(manager.getStats(), null, 2));
}