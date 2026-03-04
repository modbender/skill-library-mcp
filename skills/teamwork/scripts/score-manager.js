#!/usr/bin/env node

const path = require('path');
const init = require('./init.js');
const configManager = require('./config-manager.js');

const SCORES_FILE = init.SCORES_FILE;

function initializeModelScore(scores, modelName, provider) {
  if (!scores.scores[modelName]) {
    scores.scores[modelName] = {
      provider: provider,
      dimensions: {
        response_speed: 5.0,
        response_frequency: 5.0,
        thinking_depth: 5.0,
        multi_threading: 5.0,
        code_quality: 5.0,
        creativity: 5.0,
        reliability: 5.0,
        context_understanding: 5.0
      },
      overall_score: 5.0,
      evaluation_count: 0,
      role_fit_history: {},
      last_evaluated: null
    };
  }
  return scores;
}

function updateModelScore(scores, modelName, dimension, newScore, evaluatorModel) {
  if (!scores.scores[modelName]) {
    throw new Error(`Model ${modelName} not found in scores database`);
  }

  const modelScore = scores.scores[modelName];
  const currentScore = modelScore.dimensions[dimension];
  const decayFactor = scores.score_decay_factor;
  
  const weightedNewScore = (currentScore * decayFactor) + (newScore * (1 - decayFactor));
  modelScore.dimensions[dimension] = weightedNewScore;
  
  modelScore.evaluation_count++;
  modelScore.last_evaluated = new Date().toISOString();
  
  modelScore.overall_score = calculateOverallScore(modelScore.dimensions, scores.dimension_weights);
  
  scores.last_updated = new Date().toISOString();
  return scores;
}

function calculateOverallScore(dimensions, weights) {
  let totalScore = 0;
  let totalWeight = 0;
  
  for (const [dimension, score] of Object.entries(dimensions)) {
    const weight = weights[dimension] || 0.1;
    totalScore += score * weight;
    totalWeight += weight;
  }
  
  return totalWeight > 0 ? totalScore / totalWeight : 0;
}

function updateRoleFit(scores, modelName, roleName, fitScore) {
  if (!scores.scores[modelName]) {
    throw new Error(`Model ${modelName} not found in scores database`);
  }

  const modelScore = scores.scores[modelName];
  
  if (!modelScore.role_fit_history[roleName]) {
    modelScore.role_fit_history[roleName] = {
      total_score: 0,
      count: 0,
      average: 0
    };
  }
  
  const history = modelScore.role_fit_history[roleName];
  history.total_score += fitScore;
  history.count++;
  history.average = history.total_score / history.count;
  
  scores.last_updated = new Date().toISOString();
  return scores;
}

function getTopModelsForRole(scores, roleName, topN = 3) {
  const models = [];
  
  for (const [modelName, modelData] of Object.entries(scores.scores)) {
    const roleFit = modelData.role_fit_history[roleName];
    models.push({
      model: modelName,
      provider: modelData.provider,
      overall_score: modelData.overall_score,
      role_fit: roleFit ? roleFit.average : modelData.overall_score,
      evaluation_count: modelData.evaluation_count
    });
  }
  
  models.sort((a, b) => b.role_fit - a.role_fit);
  return models.slice(0, topN);
}

function getModelsByCapability(scores, capability, minScore = 7.0) {
  const models = [];
  
  for (const [modelName, modelData] of Object.entries(scores.scores)) {
    const dimensionScore = modelData.dimensions[capability] || 0;
    if (dimensionScore >= minScore) {
      models.push({
        model: modelName,
        provider: modelData.provider,
        score: dimensionScore,
        overall_score: modelData.overall_score
      });
    }
  }
  
  models.sort((a, b) => b.score - a.score);
  return models;
}

function recordEvaluation(scores, evaluation) {
  const { evaluator, evaluatee, task_id, role_played, scores: evalScores, role_fit } = evaluation;
  
  if (!scores.scores[evaluatee]) {
    scores = initializeModelScore(scores, evaluatee, evaluation.provider || 'unknown');
  }
  
  for (const [dimension, score] of Object.entries(evalScores)) {
    scores = updateModelScore(scores, evaluatee, dimension, score, evaluator);
  }
  
  if (role_fit && role_played) {
    const fitScore = Object.values(evalScores).reduce((a, b) => a + b, 0) / Object.values(evalScores).length;
    scores = updateRoleFit(scores, evaluatee, role_played, fitScore);
  }
  
  return scores;
}

function displayScores(scores) {
  console.log('\n=== Model Performance Scores ===\n');
  console.log(`Last Updated: ${scores.last_updated}`);
  console.log(`Evaluation Interval: ${scores.evaluation_interval_seconds}s`);
  console.log(`Score Decay Factor: ${scores.score_decay_factor}`);
  
  console.log('\n--- Model Scores ---\n');
  
  const sortedModels = Object.entries(scores.scores)
    .sort((a, b) => b[1].overall_score - a[1].overall_score);
  
  for (const [modelName, modelData] of sortedModels) {
    console.log(`Model: ${modelName} (${modelData.provider})`);
    console.log(`  Overall Score: ${modelData.overall_score.toFixed(2)}/10`);
    console.log(`  Evaluations: ${modelData.evaluation_count}`);
    console.log(`  Dimensions:`);
    for (const [dim, score] of Object.entries(modelData.dimensions)) {
      console.log(`    - ${dim}: ${score.toFixed(2)}`);
    }
    if (Object.keys(modelData.role_fit_history).length > 0) {
      console.log(`  Role Fit History:`);
      for (const [role, fit] of Object.entries(modelData.role_fit_history)) {
        console.log(`    - ${role}: ${fit.average.toFixed(2)}`);
      }
    }
    console.log('');
  }
}

module.exports = {
  initializeModelScore,
  updateModelScore,
  calculateOverallScore,
  updateRoleFit,
  getTopModelsForRole,
  getModelsByCapability,
  recordEvaluation,
  displayScores
};
