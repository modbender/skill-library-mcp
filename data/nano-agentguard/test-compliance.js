// Test compliance reporting
const AgentGuard = require('./src/index');

async function testCompliance() {
  const guard = new AgentGuard({
    masterPassword: 'nano-test-password'
  });

  await guard.init();

  console.log('\n🧪 Testing Compliance Reporting\n');

  // Simulate data processing activities
  console.log('1. Simulating data processing activities...');

  // GDPR-related activities
  await guard.audit.log('nano', 'operation_executed', {
    operation: 'send_email',
    success: true,
    userId: 'user-001',
    purpose: 'newsletter',
    legalBasis: 'consent',
    consent: true
  });

  await guard.audit.log('nano', 'credential_accessed', {
    key: 'USER_DATA',
    userId: 'user-001',
    dataType: 'personal'
  });

  await guard.audit.log('nano', 'operation_executed', {
    operation: 'api_call',
    success: true,
    userId: 'user-002',
    purpose: 'analytics',
    legalBasis: 'legitimate'
  });

  await guard.audit.log('nano', 'consent_given', {
    userId: 'user-001',
    purpose: 'newsletter',
    consent: true
  });

  await guard.audit.log('nano', 'subject_access_request', {
    userId: 'user-002',
    fulfilled: true
  });

  // CCPA-related activities
  await guard.audit.log('nano', 'operation_executed', {
    operation: 'data_export',
    userId: 'user-003',
    sale: false
  });

  await guard.audit.log('nano', 'consumer_request', {
    requestType: 'deletion',
    userId: 'user-003',
    responseTime: 15,
    fulfilled: true
  });

  console.log('   ✓ 5 GDPR activities logged');
  console.log('   ✓ 2 CCPA activities logged');

  // Generate GDPR report
  console.log('\n2. Generating GDPR report...');
  const gdprReport = await guard.getGDPRReport('nano', { days: 1 });

  console.log(`\n   Compliance Score: ${gdprReport.summary.complianceScore}/100`);
  console.log(`   Data Processing Activities: ${gdprReport.summary.totalProcessingActivities}`);
  console.log(`   Unique Data Subjects: ${gdprReport.summary.uniqueDataSubjects}`);
  console.log(`   Consent Coverage: ${gdprReport.consent.coverage}%`);

  if (gdprReport.risks.length > 0) {
    console.log('\n   Risks:');
    for (const risk of gdprReport.risks) {
      console.log(`     [${risk.level.toUpperCase()}] ${risk.description}`);
    }
  }

  // Generate CCPA report
  console.log('\n3. Generating CCPA report...');
  const ccpaReport = await guard.getCCPAReport('nano', { days: 1 });

  console.log(`\n   Compliance Score: ${ccpaReport.summary.complianceScore}/100`);
  console.log(`   Consumer Requests: ${ccpaReport.summary.consumerRequests}`);
  console.log(`   Data Sales: ${ccpaReport.summary.dataSales}`);

  if (ccpaReport.consumerRights.fulfillment) {
    console.log(`   Fulfillment Rate: ${ccpaReport.consumerRights.fulfillment.rate}%`);
  }

  // Generate full report
  console.log('\n4. Generating full compliance report...');
  const fullReport = await guard.getFullComplianceReport('nano', { days: 1 });

  console.log(`\n   Overall Score: ${fullReport.overallScore}/100`);
  console.log(`   GDPR Score: ${fullReport.gdpr.summary.complianceScore}/100`);
  console.log(`   CCPA Score: ${fullReport.ccpa.summary.complianceScore}/100`);

  if (fullReport.allRecommendations.length > 0) {
    console.log('\n   Top Recommendations:');
    for (const rec of fullReport.allRecommendations.slice(0, 3)) {
      console.log(`     [${rec.priority.toUpperCase()}] ${rec.action}`);
    }
  }

  console.log('\n✅ Compliance Reporting Test Complete!\n');
}

testCompliance().catch(console.error);
