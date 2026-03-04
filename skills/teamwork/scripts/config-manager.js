#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const init = require('./init.js');

function addProvider(config, providerInfo) {
  const provider = {
    name: providerInfo.name,
    api_key: providerInfo.api_key || `\${${providerInfo.name.toUpperCase()}_API_KEY}`,
    base_url: providerInfo.base_url || '',
    models: []
  };

  config.providers.push(provider);
  config.last_updated = new Date().toISOString();
  return config;
}

function addModel(config, providerName, modelInfo) {
  const provider = config.providers.find(p => p.name === providerName);
  if (!provider) {
    throw new Error(`Provider ${providerName} not found`);
  }

  const model = {
    name: modelInfo.name,
    pricing_model: modelInfo.pricing_model,
    context_window: modelInfo.context_window || 4096,
    capabilities: modelInfo.capabilities || [],
    max_concurrent_tasks: modelInfo.max_concurrent_tasks || 1
  };

  if (modelInfo.pricing_model === 'subscription') {
    model.subscription_cost = modelInfo.subscription_cost;
    model.valid_from = modelInfo.valid_from;
    model.valid_until = modelInfo.valid_until;
    model.status = 'active';
  } else if (modelInfo.pricing_model === 'tiered_usage') {
    model.daily_quota = modelInfo.daily_quota;
    model.monthly_quota = modelInfo.monthly_quota;
    model.daily_used = 0;
    model.monthly_used = 0;
    model.overage_rate = modelInfo.overage_rate || 0;
  } else if (modelInfo.pricing_model === 'pay_per_use') {
    model.input_cost_per_1k = modelInfo.input_cost_per_1k;
    model.output_cost_per_1k = modelInfo.output_cost_per_1k;
    model.total_spent = 0;
  }

  provider.models.push(model);
  config.last_updated = new Date().toISOString();
  return config;
}

function removeModel(config, providerName, modelName) {
  const provider = config.providers.find(p => p.name === providerName);
  if (!provider) {
    throw new Error(`Provider ${providerName} not found`);
  }

  provider.models = provider.models.filter(m => m.name !== modelName);
  config.last_updated = new Date().toISOString();
  return config;
}

function removeProvider(config, providerName) {
  config.providers = config.providers.filter(p => p.name !== providerName);
  config.last_updated = new Date().toISOString();
  return config;
}

function updateModelPricing(config, providerName, modelName, pricingInfo) {
  const provider = config.providers.find(p => p.name === providerName);
  if (!provider) {
    throw new Error(`Provider ${providerName} not found`);
  }

  const model = provider.models.find(m => m.name === modelName);
  if (!model) {
    throw new Error(`Model ${modelName} not found`);
  }

  model.pricing_model = pricingInfo.pricing_model;
  
  delete model.subscription_cost;
  delete model.valid_from;
  delete model.valid_until;
  delete model.status;
  delete model.daily_quota;
  delete model.monthly_quota;
  delete model.daily_used;
  delete model.monthly_used;
  delete model.overage_rate;
  delete model.input_cost_per_1k;
  delete model.output_cost_per_1k;
  delete model.total_spent;

  if (pricingInfo.pricing_model === 'subscription') {
    model.subscription_cost = pricingInfo.subscription_cost;
    model.valid_from = pricingInfo.valid_from;
    model.valid_until = pricingInfo.valid_until;
    model.status = 'active';
  } else if (pricingInfo.pricing_model === 'tiered_usage') {
    model.daily_quota = pricingInfo.daily_quota;
    model.monthly_quota = pricingInfo.monthly_quota;
    model.daily_used = 0;
    model.monthly_used = 0;
    model.overage_rate = pricingInfo.overage_rate || 0;
  } else if (pricingInfo.pricing_model === 'pay_per_use') {
    model.input_cost_per_1k = pricingInfo.input_cost_per_1k;
    model.output_cost_per_1k = pricingInfo.output_cost_per_1k;
    model.total_spent = 0;
  }

  config.last_updated = new Date().toISOString();
  return config;
}

function setHostModel(config, providerName, modelName) {
  const provider = config.providers.find(p => p.name === providerName);
  if (!provider) {
    throw new Error(`Provider ${providerName} not found`);
  }

  const model = provider.models.find(m => m.name === modelName);
  if (!model) {
    throw new Error(`Model ${modelName} not found in provider ${providerName}`);
  }

  config.host_model = {
    provider: providerName,
    model: modelName
  };
  config.last_updated = new Date().toISOString();
  return config;
}

function setBudget(config, budgetInfo) {
  config.budget = {
    max_monthly_cost: budgetInfo.max_monthly_cost || 0,
    currency: budgetInfo.currency || 'USD',
    alert_threshold: budgetInfo.alert_threshold || 0.8,
    current_month_spent: config.budget?.current_month_spent || 0
  };
  config.last_updated = new Date().toISOString();
  return config;
}

function getAvailableModels(config) {
  const models = [];
  config.providers.forEach(provider => {
    provider.models.forEach(model => {
      models.push({
        provider: provider.name,
        model: model.name,
        capabilities: model.capabilities,
        pricing_model: model.pricing_model,
        status: getModelStatus(model)
      });
    });
  });
  return models;
}

function getModelStatus(model) {
  if (model.pricing_model === 'subscription') {
    const now = new Date();
    const validUntil = new Date(model.valid_until);
    if (now > validUntil) return 'expired';
    return model.status || 'active';
  }
  
  if (model.pricing_model === 'tiered_usage') {
    if (model.daily_used >= model.daily_quota) return 'quota_exceeded';
    if (model.monthly_used >= model.monthly_quota) return 'quota_exceeded';
    return 'available';
  }
  
  return 'available';
}

function displayConfiguration(config) {
  console.log('\n=== Teamwork Skill Configuration ===\n');
  console.log(`Version: ${config.version}`);
  console.log(`Last Updated: ${config.last_updated}`);
  console.log(`\nHost Model: ${config.host_model.provider}/${config.host_model.model}`);
  console.log(`\nBudget: $${config.budget.max_monthly_cost} ${config.budget.currency}`);
  console.log(`Alert Threshold: ${(config.budget.alert_threshold * 100).toFixed(0)}%`);
  console.log(`Current Month Spent: $${config.budget.current_month_spent.toFixed(2)}`);
  
  console.log('\n--- Providers ---\n');
  config.providers.forEach(provider => {
    console.log(`Provider: ${provider.name}`);
    console.log(`  Base URL: ${provider.base_url || 'default'}`);
    console.log(`  Models:`);
    provider.models.forEach(model => {
      console.log(`    - ${model.name}`);
      console.log(`      Pricing: ${model.pricing_model}`);
      console.log(`      Capabilities: ${model.capabilities.join(', ')}`);
      console.log(`      Status: ${getModelStatus(model)}`);
    });
    console.log('');
  });
}

module.exports = {
  addProvider,
  addModel,
  removeModel,
  removeProvider,
  updateModelPricing,
  setHostModel,
  setBudget,
  getAvailableModels,
  getModelStatus,
  displayConfiguration
};
