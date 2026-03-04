const { execSync } = require('child_process');
const path = require('path');

const skillDir = __dirname;
const scriptPath = path.join(skillDir, 'stealth-browser.js');

function runBrowser(args) {
  try {
    const result = execSync(`node "${scriptPath}" ${args}`, {
      encoding: 'utf-8',
      timeout: 300000, // 5 minutes for parallel operations
      maxBuffer: 100 * 1024 * 1024 // 100MB buffer for multiple pages
    });
    return result;
  } catch (error) {
    throw new Error(`Stealth browser failed: ${error.message}`);
  }
}

module.exports = {
  name: 'stealth-browser',
  description: 'Headless browser with anti-detection capabilities',
  
  commands: {
    'stealth-browser': {
      description: 'Open URL(s) with stealth browser',
      args: ['<action>', '<url>', '[url2]', '[url3]', '...'],
      examples: [
        '/stealth-browser open https://example.com',
        '/stealth-browser screenshot https://example.com',
        '/stealth-browser pdf https://example.com',
        '/stealth-browser parallel https://site1.com https://site2.com https://site3.com'
      ],
      handler: async (args) => {
        if (!args || args.length < 2) {
          return 'Usage: /stealth-browser <open|screenshot|pdf|parallel> <url> [url2] [url3] ...';
        }
        
        const [action, ...urls] = args;
        
        if (!['open', 'screenshot', 'pdf', 'parallel'].includes(action)) {
          return 'Invalid action. Use: open, screenshot, pdf, or parallel';
        }
        
        if (urls.length === 0) {
          return 'Error: No URL(s) provided';
        }
        
        try {
          const urlList = urls.join(' ');
          const result = runBrowser(`${action} ${urlList}`);
          
          if (action === 'parallel') {
            // Return formatted JSON results
            try {
              const data = JSON.parse(result);
              let output = `=== Parallel Fetch Results (${data.length} URLs) ===\n\n`;
              
              data.forEach(item => {
                output += `[${item.index}/${data.length}] ${item.url}\n`;
                output += `Status: ${item.status.toUpperCase()}\n`;
                
                if (item.status === 'success') {
                  output += `Title: ${item.title}\n`;
                  output += `Content preview:\n${item.content.substring(0, 500)}...\n`;
                } else {
                  output += `Error: ${item.error}\n`;
                }
                
                output += '\n---\n\n';
              });
              
              return output;
            } catch (e) {
              return result;
            }
          }
          
          if (action === 'open') {
            return result.substring(0, 10000) + (result.length > 10000 ? '\n... [truncated]' : '');
          }
          
          return result;
        } catch (error) {
          return `Error: ${error.message}`;
        }
      }
    }
  },
  
  async onLoad() {
    const fs = require('fs');
    const nodeModulesPath = path.join(skillDir, 'node_modules');
    
    if (!fs.existsSync(nodeModulesPath)) {
      console.log('Installing stealth-browser dependencies...');
      try {
        execSync('npm install', {
          cwd: skillDir,
          stdio: 'inherit'
        });
        console.log('Dependencies installed successfully');
      } catch (error) {
        console.error('Failed to install dependencies:', error.message);
      }
    }
  }
};
