/**
 * 员工管理器 - Employee Manager
 * 功能：管理AI员工的增删改查、角色配置
 */

const fs = require('fs');
const path = require('path');

const CONFIG_DIR = path.join(__dirname, '..', 'config');
const MEMORY_DIR = path.join(__dirname, '..', 'memory');
const EMPLOYEES_FILE = path.join(CONFIG_DIR, 'employees.json');
const TEMPLATES_DIR = path.join(__dirname, '..', 'templates');

class EmployeeManager {
  constructor() {
    this.ensureDirs();
    this.employees = this.loadEmployees();
  }

  ensureDirs() {
    [CONFIG_DIR, MEMORY_DIR, TEMPLATES_DIR].forEach(dir => {
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
      }
    });
  }

  loadEmployees() {
    if (fs.existsSync(EMPLOYEES_FILE)) {
      return JSON.parse(fs.readFileSync(EMPLOYEES_FILE, 'utf8'));
    }
    // 默认配置
    const defaultConfig = {
      company: "AI虚拟公司",
      createdAt: new Date().toISOString(),
      employees: []
    };
    this.saveEmployees(defaultConfig);
    return defaultConfig;
  }

  saveEmployees(data) {
    fs.writeFileSync(EMPLOYEES_FILE, JSON.stringify(data, null, 2), 'utf8');
  }

  /**
   * 招聘新员工
   * @param {Object} config 员工配置
   * @returns {Object} 创建的员工
   */
  hire(config) {
    const { name, role, skills = [], model = 'gpt-4', template } = config;
    
    if (!name || !role) {
      throw new Error('员工名称和角色不能为空');
    }

    const id = `${role.toLowerCase().replace(/\s+/g, '-')}-${Date.now()}`;
    const employee = {
      id,
      name,
      role,
      skills,
      model,
      status: 'idle',
      createdAt: new Date().toISOString(),
      currentTask: null,
      completedTasks: 0,
      memoryPath: `./memory/${id}`
    };

    // 创建记忆目录
    const memDir = path.join(MEMORY_DIR, id);
    if (!fs.existsSync(memDir)) {
      fs.mkdirSync(memDir, { recursive: true });
      // 创建初始记忆文件
      fs.writeFileSync(
        path.join(memDir, 'memory.md'),
        `# ${name} - 记忆存储\n\n创建时间: ${new Date().toISOString()}\n\n## 工作记录\n\n`,
        'utf8'
      );
    }

    // 如果提供了模板，复制模板内容
    if (template) {
      const templatePath = path.join(TEMPLATES_DIR, template);
      if (fs.existsSync(templatePath)) {
        const templateContent = fs.readFileSync(templatePath, 'utf8');
        fs.writeFileSync(
          path.join(memDir, 'workflow.md'),
          templateContent,
          'utf8'
        );
      }
    }

    this.employees.employees.push(employee);
    this.saveEmployees(this.employees);

    console.log(`✅ 已招聘新员工: ${name} (${role})`);
    return employee;
  }

  /**
   * 解雇员工
   * @param {string} id 员工ID
   */
  fire(id) {
    const index = this.employees.employees.findIndex(e => e.id === id);
    if (index === -1) {
      throw new Error(`未找到员工: ${id}`);
    }

    const employee = this.employees.employees[index];
    
    // 检查是否有未完成的任务
    if (employee.status === 'working') {
      throw new Error(`员工 ${employee.name} 正在执行任务，请等待任务完成后再解雇`);
    }

    // 归档记忆
    const memDir = path.join(MEMORY_DIR, id);
    const archiveDir = path.join(MEMORY_DIR, 'archived');
    if (!fs.existsSync(archiveDir)) {
      fs.mkdirSync(archiveDir, { recursive: true });
    }
    if (fs.existsSync(memDir)) {
      fs.renameSync(memDir, path.join(archiveDir, id));
    }

    this.employees.employees.splice(index, 1);
    this.saveEmployees(this.employees);

    console.log(`👋 已解雇员工: ${employee.name}`);
    return employee;
  }

  /**
   * 获取员工信息
   */
  get(id) {
    return this.employees.employees.find(e => e.id === id);
  }

  /**
   * 列出所有员工
   */
  list() {
    return this.employees.employees.map(e => ({
      id: e.id,
      name: e.name,
      role: e.role,
      status: e.status,
      currentTask: e.currentTask,
      completedTasks: e.completedTasks
    }));
  }

  /**
   * 更新员工状态
   */
  updateStatus(id, status, taskId = null) {
    const employee = this.get(id);
    if (!employee) {
      throw new Error(`未找到员工: ${id}`);
    }

    employee.status = status;
    if (taskId) {
      employee.currentTask = taskId;
    }
    if (status === 'idle') {
      employee.currentTask = null;
      employee.completedTasks++;
    }

    this.saveEmployees(this.employees);
    return employee;
  }

  /**
   * 获取团队概览
   */
  getOverview() {
    const employees = this.employees.employees;
    return {
      total: employees.length,
      idle: employees.filter(e => e.status === 'idle').length,
      working: employees.filter(e => e.status === 'working').length,
      offline: employees.filter(e => e.status === 'offline').length,
      totalCompletedTasks: employees.reduce((sum, e) => sum + e.completedTasks, 0)
    };
  }

  /**
   * 按角色查找员工
   */
  findByRole(role) {
    return this.employees.employees.filter(e => 
      e.role.toLowerCase().includes(role.toLowerCase())
    );
  }

  /**
   * 获取空闲员工
   */
  getIdleEmployees() {
    return this.employees.employees.filter(e => e.status === 'idle');
  }

  /**
   * 写入员工记忆
   */
  writeMemory(id, content) {
    const employee = this.get(id);
    if (!employee) {
      throw new Error(`未找到员工: ${id}`);
    }

    const memFile = path.join(MEMORY_DIR, id, 'memory.md');
    const timestamp = new Date().toISOString();
    const entry = `\n## [${timestamp}]\n${content}\n`;
    
    fs.appendFileSync(memFile, entry, 'utf8');
    return true;
  }

  /**
   * 读取员工记忆
   */
  readMemory(id) {
    const memFile = path.join(MEMORY_DIR, id, 'memory.md');
    if (fs.existsSync(memFile)) {
      return fs.readFileSync(memFile, 'utf8');
    }
    return null;
  }
}

// CLI接口
if (require.main === module) {
  const manager = new EmployeeManager();
  const args = process.argv.slice(2);
  const command = args[0];

  switch (command) {
    case 'list':
      console.log('\n📋 员工列表:');
      console.table(manager.list());
      break;
    
    case 'hire':
      const hireConfig = {
        name: args[1],
        role: args[2] || '员工',
        skills: args[3] ? args[3].split(',') : []
      };
      manager.hire(hireConfig);
      break;
    
    case 'fire':
      manager.fire(args[1]);
      break;
    
    case 'status':
      console.log('\n📊 团队概览:');
      console.log(manager.getOverview());
      break;
    
    default:
      console.log(`
用法:
  node employee-manager.js list              列出所有员工
  node employee-manager.js hire <名称> <角色> <技能>  招聘员工
  node employee-manager.js fire <ID>         解雇员工
  node employee-manager.js status             查看团队状态
      `);
  }
}

module.exports = EmployeeManager;