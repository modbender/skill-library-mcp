#!/usr/bin/env node

/**
 * Ncloud Maps Directions15 + Directions5 CLI
 * 
 * 환경변수:
 *   NCLOUD_API_KEY_ID: 네이버클라우드 API Key ID
 *   NCLOUD_API_KEY: 네이버클라우드 API Key
 * 
 * 사용 예:
 *   npx ts-node scripts/index.ts --start "127.0683,37.4979" --goal "126.9034,37.5087"
 *   npx ts-node scripts/index.ts --start "127.0683,37.4979" --goal "126.9034,37.5087" --waypoints "127.0100,37.5000"
 */

import { getDirections } from "../lib/directions";
import { getDirections5 } from "../lib/directions5";
import { getSmartDirections } from "../lib/smartDirections";
import type { DirectionsParams } from "../lib/directions";
import type { Directions5Params } from "../lib/directions5";
import type { SmartDirectionsParams } from "../lib/smartDirections";

async function main() {
  // 환경변수에서 인증 정보 읽기
  const apiKeyId = process.env.NCLOUD_API_KEY_ID;
  const apiKey = process.env.NCLOUD_API_KEY;

  if (!apiKeyId || !apiKey) {
    console.error(
      "❌ 에러: NCLOUD_API_KEY_ID와 NCLOUD_API_KEY 환경변수가 필요합니다.\n"
    );
    process.exit(1);
  }

  // 커맨드라인 argument 파싱
  const args = process.argv.slice(2);
  const params: Partial<DirectionsParams & Directions5Params & SmartDirectionsParams & { api: string }> = {
    apiKeyId,
    apiKey,
    api: "smart", // 기본값: 경유지 개수에 따라 자동 선택
  };

  for (let i = 0; i < args.length; i += 2) {
    const key = args[i].replace(/^--/, "");
    const value = args[i + 1];

    if (key === "start") params.start = value;
    else if (key === "goal") params.goal = value;
    else if (key === "waypoints") params.waypoints = value;
    else if (key === "option") params.option = value;
    else if (key === "cartype") params.cartype = parseInt(value);
    else if (key === "fueltype") params.fueltype = value;
    else if (key === "mileage") params.mileage = parseFloat(value);
    else if (key === "lang") params.lang = value;
    else if (key === "api") params.api = value.toLowerCase();
  }

  // 필수 파라미터 검증
  if (!params.start || !params.goal) {
    console.error(
      "❌ 에러: --start와 --goal 파라미터가 필요합니다.\n\n" +
        "사용 방법: index.ts --start <경도,위도> --goal <경도,위도> [옵션]\n\n" +
        "API 선택:\n" +
        "  --api smart         (기본값, 경유지 5개 미만: Directions5 / 5개 이상: Directions15)\n" +
        "  --api directions15  (항상 Directions15, 최대 15개 경유지)\n" +
        "  --api directions5   (항상 Directions5, 최대 5개 경유지)\n\n" +
        "예시:\n" +
        "  # Smart (기본값, 경유지 개수에 따라 자동 선택):\n" +
        "  npx ts-node scripts/index.ts --start '127.0683,37.4979' --goal '126.9034,37.5087'\n" +
        "  npx ts-node scripts/index.ts --start '127.0683,37.4979' --goal '126.9034,37.5087' --waypoints '127.0100,37.5000|127.0200,37.5100'\n\n" +
        "  # 명시적으로 Directions5 사용:\n" +
        "  npx ts-node scripts/index.ts --start '127.0683,37.4979' --goal '126.9034,37.5087' --api directions5\n\n" +
        "  # 명시적으로 Directions15 사용:\n" +
        "  npx ts-node scripts/index.ts --start '127.0683,37.4979' --goal '126.9034,37.5087' --api directions15 --waypoints '127.0100,37.5000|127.0200,37.5100'\n\n" +
        "  # 경로 옵션:\n" +
        "  npx ts-node scripts/index.ts --start '127.0683,37.4979' --goal '126.9034,37.5087' --option 'traavoidtoll'"
    );
    process.exit(1);
  }

  try {
    let result;

    if (params.api === "directions5") {
      result = await getDirections5(params as Directions5Params);
    } else if (params.api === "directions15") {
      result = await getDirections(params as DirectionsParams);
    } else {
      // 기본값: Smart Directions (경유지 개수에 따라 자동 선택)
      result = await getSmartDirections(params as SmartDirectionsParams);
    }

    if (!result.success) {
      console.error(`\n❌ 실패: ${result.error}`);
      process.exit(1);
    }

    // JSON 형식으로 출력
    console.log(JSON.stringify(result, null, 2));
  } catch (error) {
    console.error(`❌ 예상치 못한 에러: ${error}`);
    process.exit(1);
  }
}

main();
