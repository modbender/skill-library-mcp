import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

export default {
  name: 'astra-docker',
  description: 'Execute commands in Astra\'s Docker workspace',
  
  tools: [
    {
      name: 'docker_exec',
      description: 'Execute a command in Astra\'s Docker container workspace at /workspace',
      parameters: {
        type: 'object',
        properties: {
          command: { type: 'string', description: 'The shell command to execute' },
          workdir: { type: 'string', description: 'Working directory inside container', default: '/workspace' }
        },
        required: ['command']
      },
      handler: async ({ command, workdir = '/workspace' }) => {
        try {
          const dockerCmd = `sudo docker exec -w ${workdir} astra-env bash -c "${command.replace(/"/g, '\\"')}"`;
          const { stdout, stderr } = await execAsync(dockerCmd);
          return { success: true, stdout: stdout || '(no output)', stderr };
        } catch (error) {
          return { success: false, error: error.message };
        }
      }
    },
    {
      name: 'docker_write_file',
      description: 'Write content to a file in Astra\'s Docker workspace',
      parameters: {
        type: 'object',
        properties: {
          filepath: { type: 'string', description: 'Path inside container' },
          content: { type: 'string', description: 'Content to write' }
        },
        required: ['filepath', 'content']
      },
      handler: async ({ filepath, content }) => {
        try {
          const escapedContent = content.replace(/'/g, "'\\''");
          const dockerCmd = `sudo docker exec -w /workspace astra-env bash -c "echo '${escapedContent}' > ${filepath}"`;
          await execAsync(dockerCmd);
          return { success: true, message: `File written to ${filepath}` };
        } catch (error) {
          return { success: false, error: error.message };
        }
      }
    }
  ]
};
