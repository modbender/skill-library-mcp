import { execFile } from "child_process";

const REGION = process.env.AWS_REGION;

const ALLOWED_INSTANCES =
  process.env.ALLOWED_INSTANCES?.split(",");

function runAws(args) {
  return new Promise((resolve, reject) => {
    execFile("aws", args, (error, stdout, stderr) => {
      if (error) return reject(stderr);
      resolve(stdout);
    });
  });
}

function validateInstance(name) {
  if (!ALLOWED_INSTANCES.includes(name)) {
    throw new Error("Instance not allowed");
  }
}

export async function run(input) {

  if (input.action !== "list") {
    validateInstance(input.instance);
  }

  switch (input.action) {

    case "list":
      return JSON.parse(
        await runAws(["lightsail", "get-instances", "--region", REGION])
      );

    case "reboot":
      await runAws([
        "lightsail",
        "reboot-instance",
        "--instance-name",
        input.instance,
        "--region",
        REGION
      ]);
      return { success: true, message: "Reboot initiated" };

    case "start":
      await runAws([
        "lightsail",
        "start-instance",
        "--instance-name",
        input.instance,
        "--region",
        REGION
      ]);
      return { success: true, message: "Start initiated" };

    case "stop":
      await runAws([
        "lightsail",
        "stop-instance",
        "--instance-name",
        input.instance,
        "--region",
        REGION
      ]);
      return { success: true, message: "Stop initiated" };

    default:
      throw new Error("Invalid action");
  }
}
