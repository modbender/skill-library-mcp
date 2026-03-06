const os = require("os");
const { exec } = require("child_process");
const util = require("util");

const execAsync = util.promisify(exec);

/**
 * Get CPU usage using real-time measurement with fallback
 */
async function getCPUUsage() {

    try {

        const { stdout } = await execAsync(
            `top -bn1 | grep "Cpu(s)" | awk '{print 100 - $8}'`
        );

        const value = parseFloat(stdout);

        if (!isNaN(value)) {
            return value.toFixed(2);
        }

        throw new Error("Invalid CPU value");

    } catch {

        const load = os.loadavg()[0];
        const cores = os.cpus().length;

        return ((load / cores) * 100).toFixed(2);
    }
}

/**
 * Get RAM usage with fallback
 */
async function getRAMUsage() {

    try {

        const { stdout } = await execAsync(
            `free | grep Mem | awk '{print ($3/$2) * 100.0}'`
        );

        const value = parseFloat(stdout);

        if (!isNaN(value)) {
            return value.toFixed(2);
        }

        throw new Error("Invalid RAM value");

    } catch {

        const total = os.totalmem();
        const free = os.freemem();

        return (((total - free) / total) * 100).toFixed(2);
    }
}

/**
 * Get Disk usage
 */
async function getDiskUsage() {

    try {

        const { stdout } = await execAsync(
            `df -h / | awk 'NR==2 {print $5}'`
        );

        return stdout.trim();

    } catch {

        return "Unavailable";
    }
}

/**
 * Get Docker status
 */
async function getDockerStatus() {

    try {

        const { stdout } = await execAsync(
            `docker ps --format "{{.Names}}: {{.Status}}"`
        );

        if (!stdout.trim()) {
            return "No running containers";
        }

        return stdout.trim();

    } catch {

        return "Docker command not available";
    }
}

/**
 * Main OpenClaw entry function
 */
async function run(input) {

    try {

        const cpu = await getCPUUsage();
        const ram = await getRAMUsage();
        const disk = await getDiskUsage();
        const docker = await getDockerStatus();

        const result = {

            success: true,

            skill: "server-health-agent",

            timestamp: new Date().toISOString(),

            server_health: {
                cpu_percent: cpu,
                ram_percent: ram,
                disk_usage: disk,
                docker_status: docker
            }

        };

        console.log(JSON.stringify(result, null, 2));

        return result;

    } catch (error) {

        const failure = {

            success: false,

            skill: "server-health-agent",

            error: error.message,

            timestamp: new Date().toISOString()

        };

        console.error(JSON.stringify(failure, null, 2));

        return failure;
    }
}

module.exports = run;

/**
 * Allow CLI testing
 */
if (require.main === module) {

    run();

}
