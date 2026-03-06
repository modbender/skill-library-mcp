# 配置管理指南

## 环境变量管理

### 环境变量文件

- **.env.example**：环境变量示例文件
- **.env.develop**：开发环境配置文件
- **/etc/magicbox-node/env.config.json**：生产/预发环境配置文件

### 环境变量优先级

1. 系统环境变量（最高优先级）
2. 配置文件中的环境变量
3. 默认值（最低优先级）

### 环境变量加载流程

1. 应用启动时加载 `env.config.ts`
2. 根据 `NODE_ENV` 确定加载哪个配置文件
3. 开发环境：加载 `.env.develop` 文件
4. 生产/预发环境：加载 `/etc/magicbox-node/env.config.json` 文件
5. 系统环境变量覆盖配置文件中的值

## 配置文件结构

### .env.develop

```env
# 环境配置
NODE_ENV=development

# 服务器配置
PORT=3000
HOST=localhost

# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_DATABASE=magicbox_dev
DB_USERNAME=root
DB_PASSWORD=

# 其他配置
LOG_LEVEL=debug
```

### env.config.json

```json
{
  "NODE_ENV": "production",
  "PORT": "80",
  "HOST": "0.0.0.0",
  "SERVER_NAME": "magicbox-node-service",
  "DB_HOST": "database-host",
  "DB_PORT": "3306",
  "DB_DATABASE": "magicbox",
  "DB_USERNAME": "username",
  "DB_PASSWORD": "password",
  "LOG_LEVEL": "info",
  "CORS_ORIGIN": "*"
}
```

## 数据库配置

### database.config.ts

```typescript
import { DataSourceOptions } from 'typeorm';
import { loadEnvConfig } from './env.config';
import { Session } from '../models/session.entity';
import { Message } from '../models/message.entity';

// 加载环境配置
loadEnvConfig();

export const databaseConfig: DataSourceOptions = {
  type: 'mysql',
  host: process.env.DB_HOST || 'localhost',
  port: parseInt(process.env.DB_PORT || '3306'),
  username: process.env.DB_USERNAME || 'root',
  password: process.env.DB_PASSWORD || '',
  database: process.env.DB_DATABASE || 'magicbox',
  entities: [Session, Message],
  synchronize: process.env.NODE_ENV === 'development',
  logging: process.env.NODE_ENV === 'development',
  charset: 'utf8mb4',
  timezone: '+08:00'
};
```

## 环境配置

### env.config.ts

```typescript
import fs from 'fs';
import path from 'path';

export function loadEnvConfig(): void {
  const nodeEnv = process.env.NODE_ENV || 'development';
  
  // 开发环境：使用 .env 文件
  if (nodeEnv === 'development') {
    const envFile = '.env.develop';
    const envPath = path.resolve(process.cwd(), envFile);
    
    if (fs.existsSync(envPath)) {
      try {
        const envContent = fs.readFileSync(envPath, 'utf8');
        const envVars = envContent.split('\n');
        
        envVars.forEach(line => {
          const match = line.match(/^([^#=]+)\s*=\s*([^#]+)$/);
          if (match) {
            const [, key, value] = match;
            const trimmedKey = key.trim();
            const trimmedValue = value.trim().replace(/^['"](.*)['"]$/, '$1');
            
            if (!process.env[trimmedKey]) {
              process.env[trimmedKey] = trimmedValue;
            }
          }
        });
        
        console.log(`✅ Loaded configuration from: ${envFile}`);
      } catch (error) {
        console.warn(`⚠️ Failed to load configuration from ${envFile}:`, error);
      }
    } else {
      console.warn(`⚠️ No configuration file found at ${envPath}. Using system environment variables.`);
    }
  } 
  // 生产/预发环境：使用 /etc 目录配置
  else {
    const configPath = `/etc/magicbox-node/env.config.json`;
    
    if (fs.existsSync(configPath)) {
      try {
        const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
        
        Object.keys(config).forEach(key => {
          if (!process.env[key]) {
            process.env[key] = config[key];
          }
        });
        
        console.log(`✅ Loaded configuration from: ${configPath}`);
      } catch (error) {
        console.warn(`⚠️ Failed to load configuration from ${configPath}:`, error);
      }
    } else {
      console.warn(`⚠️ No configuration file found at ${configPath}. Using system environment variables.`);
    }
  }
  
  // 记录当前环境
  console.log(`🌍 Environment: ${nodeEnv}`);
  console.log(`🗄️ Database: ${process.env.DB_HOST}:${process.env.DB_PORT}/${process.env.DB_DATABASE}`);
  console.log(`🌐 Server: ${process.env.HOST}:${process.env.PORT}`);
}
```

## 安全配置

### 敏感信息管理

1. **禁止硬编码**：敏感信息如数据库密码、API 密钥等禁止硬编码
2. **环境变量**：使用环境变量存储敏感信息
3. **配置文件权限**：生产环境配置文件权限设置为 600
4. **版本控制**：敏感配置文件不纳入版本控制

### CORS 配置

```typescript
app.use((req, res, next) => {
  const corsOrigin = process.env.CORS_ORIGIN || '*';
  res.header('Access-Control-Allow-Origin', corsOrigin);
  res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept, Authorization');
  
  if (req.method === 'OPTIONS') {
    res.sendStatus(200);
  } else {
    next();
  }
});
```

## 最佳实践

1. **配置分离**：不同环境使用不同的配置文件
2. **默认值**：为所有配置项设置合理的默认值
3. **验证**：验证必要的配置项是否存在
4. **日志**：记录配置加载过程
5. **安全**：保护敏感配置信息