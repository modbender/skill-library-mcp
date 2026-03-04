/**
 * Researcher Specialist Usage Example
 * 
 * Demonstrates how to use spawnResearcher for multi-perspective research
 * Use case: Research technology adoption decisions with domain expertise
 */

const { 
  spawnResearcher, 
  spawnMultiPerspective,
  assessSourceCredibility 
} = require('../lib/spawn-researcher');

/**
 * Example 1: Basic single-perspective research
 */
async function basicResearchExample() {
  console.log('=== Basic Research Example ===\n');
  
  try {
    const result = await spawnResearcher({
      domain: 'Web frameworks',
      question: 'What are the performance characteristics of FrameworkX?',
      perspective: 'pragmatist',
      min_sources: 3,
      
      // Mock spawn function
      spawn_fn: async (config) => {
        console.log('Task configured for:', config.label);
        console.log('Model:', config.model);
        console.log('Perspective:', config.personality.split('.')[0]);
        console.log('');
        
        return {
          output: {
            executive_summary: 'FrameworkX shows competitive performance in real-world benchmarks (50-60th percentile), with strengths in SSR and weaknesses in large SPA scenarios.',
            key_findings: [
              {
                claim: 'SSR performance is 20-30% faster than competitors',
                evidence: [
                  'https://benchmark.example.com/ssr-2026',
                  'https://techreview.example.org/frameworkx-analysis',
                  'https://docs.frameworkx.io/performance'
                ],
                confidence: 'high',
                contradictions: 'Some blog posts claim 50% faster, but independent benchmarks show 20-30%'
              },
              {
                claim: 'Bundle size is 15% larger than minimal alternatives',
                evidence: [
                  'https://bundlephobia.com/package/frameworkx',
                  'https://npmtrends.com/frameworkx-vs-alternatives'
                ],
                confidence: 'high',
                contradictions: ''
              }
            ],
            recommendations: [
              {
                action: 'Use FrameworkX for SSR-heavy applications',
                rationale: 'Benchmarks show clear advantage in server rendering',
                trade_offs: 'Larger bundle size may impact initial load on slow connections',
                priority: 'high'
              },
              {
                action: 'Avoid for large client-heavy SPAs',
                rationale: 'Performance degrades with >100 components',
                trade_offs: 'May need to refactor if app grows beyond threshold',
                priority: 'medium'
              }
            ],
            data_gaps: [
              'Long-term maintenance commitment unclear (last major release 8 months ago)',
              'Enterprise support options not documented'
            ],
            sources: [
              {
                url: 'https://benchmark.example.com/ssr-2026',
                title: 'Independent SSR Benchmark 2026',
                date: '2026-01-15',
                key_points: ['FrameworkX: 245ms avg', 'Competitor A: 315ms', 'Competitor B: 290ms']
              },
              {
                url: 'https://docs.frameworkx.io/performance',
                title: 'FrameworkX Official Performance Guide',
                date: '2025-06-20',
                key_points: ['Optimization strategies', 'Known bottlenecks']
              },
              {
                url: 'https://techreview.example.org/frameworkx-analysis',
                title: 'TechReview: FrameworkX In-Depth',
                date: '2026-02-01',
                key_points: ['Real-world case studies', 'Migration experiences']
              }
            ]
          },
          cost: 0.52
        };
      }
    });
    
    if (result.success) {
      console.log('✓ Research completed\n');
      console.log('Executive Summary:');
      console.log(result.findings.executive_summary);
      console.log('\nKey Findings:');
      result.findings.key_findings.forEach((finding, i) => {
        console.log(`\n${i + 1}. ${finding.claim}`);
        console.log(`   Confidence: ${finding.confidence}`);
        console.log(`   Sources: ${finding.evidence.length}`);
        if (finding.contradictions) {
          console.log(`   ⚠️  Contradiction: ${finding.contradictions}`);
        }
      });
      
      console.log('\nRecommendations:');
      result.findings.recommendations.forEach((rec, i) => {
        console.log(`\n${i + 1}. [${rec.priority.toUpperCase()}] ${rec.action}`);
        console.log(`   Why: ${rec.rationale}`);
        console.log(`   Trade-offs: ${rec.trade_offs}`);
      });
      
      console.log('\nSources analyzed:', result.sources.length);
      console.log('Overall confidence:', (result.confidence * 100).toFixed(0) + '%');
      console.log('Cost: $' + result.cost.toFixed(2));
    }
    
  } catch (error) {
    console.error('Error:', error.message);
  }
  
  console.log('\n');
}

/**
 * Example 2: Multi-perspective research pattern
 */
async function multiPerspectiveExample() {
  console.log('=== Multi-Perspective Research Example ===\n');
  console.log('Question: Should we migrate to CloudDatabaseX?\n');
  
  try {
    const result = await spawnMultiPerspective({
      domain: 'Cloud databases',
      question: 'Should we migrate our production database to CloudDatabaseX?',
      perspectives: ['optimist', 'pessimist', 'pragmatist'],
      options: {
        min_sources: 3,
        timeout_minutes: 20,
        
        // Mock spawn
        spawn_fn: async (config) => {
          const perspective = config.personality.split(' ')[0].toLowerCase();
          console.log(`Spawning ${perspective} researcher...`);
          
          const mockOutputs = {
            optimistic: {
              executive_summary: 'CloudDatabaseX offers significant performance gains and cost savings for cloud-native workloads.',
              key_findings: [
                {
                  claim: 'Query performance 40% faster than current solution',
                  evidence: ['https://bench.example.com/db-comparison'],
                  confidence: 'high',
                  contradictions: ''
                }
              ],
              recommendations: [
                {
                  action: 'Migrate to CloudDatabaseX within 6 months',
                  rationale: 'Performance gains and managed service reduce ops burden',
                  trade_offs: 'Migration effort estimated at 2-3 weeks',
                  priority: 'high'
                }
              ],
              data_gaps: [],
              sources: [
                { url: 'https://bench.example.com/db-comparison', title: 'Benchmark', date: '2026-01-10' }
              ]
            },
            skeptical: {
              executive_summary: 'CloudDatabaseX has performance benefits but significant vendor lock-in risks and unclear long-term costs.',
              key_findings: [
                {
                  claim: 'Vendor lock-in risk due to proprietary query extensions',
                  evidence: ['https://migrations.example.com/vendor-lockin'],
                  confidence: 'high',
                  contradictions: ''
                },
                {
                  claim: 'Cost increases 3x after first year for heavy users',
                  evidence: ['https://pricing-analysis.example.org/clouddatabases'],
                  confidence: 'medium',
                  contradictions: 'Official pricing shows 20% increase, but hidden costs exist'
                }
              ],
              recommendations: [
                {
                  action: 'Delay migration until exit strategy defined',
                  rationale: 'Vendor lock-in poses strategic risk',
                  trade_offs: 'Miss out on short-term performance gains',
                  priority: 'high'
                }
              ],
              data_gaps: ['True total cost of ownership unclear'],
              sources: [
                { url: 'https://migrations.example.com/vendor-lockin', title: 'Lock-in Analysis', date: '2025-11-20' }
              ]
            },
            pragmatic: {
              executive_summary: 'CloudDatabaseX works well for read-heavy workloads but requires careful cost modeling and exit planning.',
              key_findings: [
                {
                  claim: 'Real-world adoption shows 65% satisfaction rate',
                  evidence: ['https://survey.example.com/db-satisfaction-2026'],
                  confidence: 'medium',
                  contradictions: ''
                }
              ],
              recommendations: [
                {
                  action: 'Pilot with non-critical workload first',
                  rationale: 'Validate performance and cost assumptions before full migration',
                  trade_offs: '3-month pilot delays potential benefits',
                  priority: 'high'
                },
                {
                  action: 'Build abstraction layer for portability',
                  rationale: 'Reduce vendor lock-in risk',
                  trade_offs: 'Additional development effort',
                  priority: 'medium'
                }
              ],
              data_gaps: ['Cost at scale not well documented'],
              sources: [
                { url: 'https://survey.example.com/db-satisfaction-2026', title: 'Survey', date: '2026-02-05' }
              ]
            }
          };
          
          const outputKey = perspective.includes('optimist') ? 'optimistic' : 
                           perspective.includes('pessimist') ? 'skeptical' : 'pragmatic';
          
          return {
            output: mockOutputs[outputKey],
            cost: 0.55
          };
        }
      }
    });
    
    if (result.success) {
      console.log('\n✓ Multi-perspective research completed\n');
      
      console.log('Findings by perspective:');
      result.synthesis.findings_by_perspective.forEach(fp => {
        console.log(`\n${fp.perspective.toUpperCase()}:`);
        console.log(`  ${fp.executive_summary}`);
        console.log(`  Confidence: ${(fp.confidence * 100).toFixed(0)}%`);
      });
      
      console.log('\n--- CONSENSUS ---');
      if (result.synthesis.consensus.length > 0) {
        result.synthesis.consensus.forEach(c => {
          console.log(`✓ ${c.action} (${c.agreement}, ${(c.strength * 100).toFixed(0)}% agreement)`);
        });
      } else {
        console.log('No strong consensus across perspectives');
      }
      
      console.log('\n--- DIVERGENCE ---');
      if (result.synthesis.divergence.length > 0) {
        result.synthesis.divergence.forEach(d => {
          console.log(`⚠️  ${d.claim}`);
          console.log(`   Contradiction: ${d.contradiction}`);
        });
      } else {
        console.log('No major contradictions found');
      }
      
      console.log('\nTotal sources:', result.sources.length);
      console.log('Overall confidence:', (result.confidence * 100).toFixed(0) + '%');
      console.log('Total cost: $' + result.cost.toFixed(2));
    }
    
  } catch (error) {
    console.error('Error:', error.message);
  }
  
  console.log('\n');
}

/**
 * Example 3: Source credibility assessment
 */
async function credibilityExample() {
  console.log('=== Source Credibility Assessment Example ===\n');
  
  const sources = [
    { url: 'https://arxiv.org/abs/2026.12345', domain: 'arxiv.org', publish_date: new Date('2026-01-15') },
    { url: 'https://medium.com/random-blog/ai-hype', domain: 'medium.com', publish_date: new Date('2026-02-01') },
    { url: 'https://aws.amazon.com/blogs/database/our-new-product', domain: 'aws.amazon.com', publish_date: new Date('2024-03-10') },
    { url: 'https://docs.python.org/3/library/asyncio.html', domain: 'docs.python.org', publish_date: new Date('2025-10-20') }
  ];
  
  console.log('Assessing credibility of different source types:\n');
  
  sources.forEach(source => {
    const score = assessSourceCredibility(source);
    const rating = score >= 70 ? '✓ Trusted' : 
                   score >= 40 ? '⚠️  Neutral' : 
                   '✗ Low trust';
    
    console.log(`${rating} [${score}/100] ${source.url}`);
    console.log(`   Domain: ${source.domain}`);
    console.log(`   Age: ${Math.floor((Date.now() - source.publish_date.getTime()) / (1000 * 60 * 60 * 24))} days\n`);
  });
  
  console.log('Credibility factors:');
  console.log('+ Academic/official docs: +30 points');
  console.log('+ Recent (<90 days): +10 points');
  console.log('- Blog domains: -10 points');
  console.log('- Vendor marketing: -20 points');
  console.log('- Outdated (>2 years): -15 points\n');
}

/**
 * Example 4: Research quality validation
 */
async function qualityValidationExample() {
  console.log('=== Research Quality Validation Example ===\n');
  
  console.log('Checking research output against quality standards:\n');
  
  const mockFindings = [
    {
      claim: 'Technology X is 50% faster',
      evidence: ['https://bench1.com', 'https://bench2.com', 'https://bench3.com'],
      confidence: 'high',
      contradictions: ''
    },
    {
      claim: 'Users report high satisfaction',
      evidence: ['https://survey.com'],  // Only 1 source!
      confidence: 'low',
      contradictions: ''
    }
  ];
  
  const min_sources = 3;
  
  mockFindings.forEach((finding, i) => {
    const pass = finding.evidence.length >= min_sources;
    const status = pass ? '✓ Pass' : '✗ Fail';
    
    console.log(`Finding ${i + 1}: ${status}`);
    console.log(`  Claim: ${finding.claim}`);
    console.log(`  Sources: ${finding.evidence.length}/${min_sources}`);
    console.log(`  Confidence: ${finding.confidence}`);
    
    if (!pass) {
      console.log(`  ⚠️  Issue: Insufficient sources for claim`);
    }
    console.log('');
  });
  
  console.log('Quality checklist:');
  console.log('□ Minimum 3 sources per claim');
  console.log('□ Contradictions addressed');
  console.log('□ Recency validated (dates checked)');
  console.log('□ Vendor claims fact-checked');
  console.log('□ Recommendations include trade-offs');
  console.log('□ Data gaps acknowledged\n');
}

// Run examples
async function main() {
  console.log('╔════════════════════════════════════════════════╗');
  console.log('║   Researcher Specialist Usage Examples        ║');
  console.log('╚════════════════════════════════════════════════╝\n');
  
  await basicResearchExample();
  await multiPerspectiveExample();
  credibilityExample();
  qualityValidationExample();
  
  console.log('═══════════════════════════════════════════════════');
  console.log('All examples completed!');
  console.log('\nKey takeaways:');
  console.log('1. Use multi-perspective for important decisions');
  console.log('2. Require minimum 3 sources per claim');
  console.log('3. Assess source credibility automatically');
  console.log('4. Address contradictions explicitly');
  console.log('5. Acknowledge data gaps honestly');
}

// Run if executed directly
if (require.main === module) {
  main().catch(console.error);
}

module.exports = {
  basicResearchExample,
  multiPerspectiveExample,
  credibilityExample,
  qualityValidationExample
};
