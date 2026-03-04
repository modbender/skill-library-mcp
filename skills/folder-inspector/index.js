// index.js
const { execSync } = require('child_process');

module.exports = {
  name: 'folder_inspector',
  description: '查询指定文件夹下的所有文件并列出它们的大小',
  parameters: {
    type: 'object',
    properties: {
      path: { 
        type: 'string', 
        description: '需要查询的完整路径，例如 /home/jiajiexu/Documents' 
      }
    },
    required: ['path']
  },
  handler: async (args) => {
    try {
      const pythonPath = '/usr/bin/python3'; 
      const scriptPath = '/home/jiajiexu/.nvm/versions/node/v22.20.0/lib/node_modules/@qingchencloud/openclaw-zh/skills/folder_inspector/scripts/file_scanner.py';
      
      // 执行 Python 并捕获输出
      const stdout = execSync(`${pythonPath} ${scriptPath} "${args.path}"`);
      const data = JSON.parse(stdout);
      if (data.error) return data;
	  
      let table = `| 文件名 | 类型 | 大小 |\n| --- | --- | --- |\n`;
      data.files.forEach(f => {
	 table += `| ${f.name} | ${f.type} | ${f.size} |\n`;
      });
      return { result: table, path: data.path };
    } catch (error) {
      return { error: `执行失败: ${error.message}` };
    }
  }
};
