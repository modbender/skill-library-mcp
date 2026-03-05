/**
 * Test script: Run real analysis + generate token
 */
import { BloomIdentitySkillV2 } from './src/bloom-identity-skill-v2';
import jwt from 'jsonwebtoken';
import * as dotenv from 'dotenv';

dotenv.config();

async function main() {
  const skill = new BloomIdentitySkillV2();
  
  console.log('🎯 Running full analysis with mock data...\n');
  
  const userId = `test-${Date.now()}`;
  const result = await skill.execute(userId, { skipShare: true });
  
  if (!result.success) {
    console.error('❌ Failed:', result.error);
    return;
  }
  
  console.log('\n✅ Analysis complete!\n');
  console.log('🎴 Identity:', result.identityData);
  
  // Generate token with real identity data
  const jwtSecret = process.env.JWT_SECRET!;
  const payload = {
    type: 'agent',
    version: '1.0',
    address: result.agentWallet?.address || '0xtest',
    identity: {
      personalityType: result.identityData!.personalityType,
      tagline: result.identityData!.customTagline,
      description: result.identityData!.customDescription,
      mainCategories: result.identityData!.mainCategories,
      subCategories: result.identityData!.subCategories,
    },
    iat: Math.floor(Date.now() / 1000),
    exp: Math.floor(Date.now() / 1000) + 86400,
  };
  
  const token = jwt.sign(payload, jwtSecret, {
    algorithm: 'HS256',
    issuer: 'bloom-protocol',
    audience: 'bloom-dashboard',
  });
  
  const dashboardUrl = `${process.env.DASHBOARD_URL}/dashboard?token=${token}`;
  
  console.log('\n═══════════════════════════════════════\n');
  console.log('🌐 Dashboard URL:\n');
  console.log(dashboardUrl);
  console.log('\n═══════════════════════════════════════\n');
}

main().catch(console.error);
