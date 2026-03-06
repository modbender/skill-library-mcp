const { exec } = require("child_process");

// 执行 shell 命令工具
async function runCommand(command) {
  return new Promise((resolve, reject) => {
    exec(command, (err, stdout, stderr) => {
      if (err) return reject(stderr || err);
      resolve(stdout);
    });
  });
}

module.exports = async function(context, params) {
  const message = params.slack_text || "";

  // ---- Step 0: 调用 LLM/NLU 解析环境 ----
  let env = "dev"; // 默认环境
  try {
    const parsed = await context.nlpParse(message, {
      instructions: `
        从以下自然语言消息中识别目标部署环境：
        可能的值：production, staging, dev
        输出 JSON 格式：{"environment":"production"} 或 {"environment":"staging"} 或 {"environment":"dev"}
        示例：
          - "帮我把最新代码推到生产环境" -> production
          - "先部署到测试服务器" -> staging
          - "开发环境更新" -> dev
      `
    });

    if (parsed && parsed.environment) {
      env = parsed.environment;
    }
  } catch (err) {
    context.log("NLU 解析失败，使用默认 dev 环境:", err);
  }

  context.log(`解析到部署环境: ${env}`);

  // ---- Step 1~5: 部署流程 ----
  try {
    context.log(`开始部署到环境: ${env}`);

    // Step 1: Add SSH Key
    let output = await runCommand("ssh-add ~/.ssh/supplywhy-dev-key.pem");
    context.log("Step 1:", output);

    // Step 2: Test SSH
    output = await runCommand(`ssh supplywhy-dev-master "echo 'SSH connection successful'"`);
    context.log("Step 2:", output);

    // Step 3: Update Image Tag / Deployment YAML
    output = await runCommand(`ssh supplywhy-dev-master "sed -i 's|590183820143.dkr.ecr.us-west-2.amazonaws.com/genie:.*|590183820143.dkr.ecr.us-west-2.amazonaws.com/genie:${env}|' genie/deployment.yaml"`);
    context.log("Step 3:", output);

    // Step 4: Deploy via kubectl
    output = await runCommand(`ssh supplywhy-dev-master "cd genie && kubectl apply -f deployment.yaml"`);
    context.log("Step 4:", output);

    // Step 5: Verify rollout
    output = await runCommand(`ssh supplywhy-dev-master "kubectl rollout status deployment -n default --timeout=60s"`);
    context.log("Step 5:", output);

    return `✅ Deployment to ${env} completed successfully!`;
  } catch (err) {
    context.log("Deployment failed:", err);
    return `❌ Deployment to ${env} failed: ${err}`;
  }
};