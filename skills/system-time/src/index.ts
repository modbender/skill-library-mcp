#!/usr/bin/env node

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';

const server = new Server(
  {
    name: 'system-time',
    version: '0.1.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// 格式化时间的辅助函数
function formatDateTime(date: Date, format: string): string {
  const pad = (n: number) => n.toString().padStart(2, '0');
  
  const year = date.getFullYear();
  const month = pad(date.getMonth() + 1);
  const day = pad(date.getDate());
  const hours = pad(date.getHours());
  const minutes = pad(date.getMinutes());
  const seconds = pad(date.getSeconds());
  const milliseconds = date.getMilliseconds().toString().padStart(3, '0');
  
  const weekdays = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六'];
  const weekday = weekdays[date.getDay()];
  
  switch (format) {
    case 'iso':
      return date.toISOString();
    case 'date':
      return `${year}-${month}-${day}`;
    case 'time':
      return `${hours}:${minutes}:${seconds}`;
    case 'datetime':
      return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
    case 'full':
      return `${year}年${month}月${day}日 ${weekday} ${hours}:${minutes}:${seconds}`;
    case 'timestamp':
      return date.getTime().toString();
    case 'detailed':
      return `${year}年${month}月${day}日 ${weekday} ${hours}时${minutes}分${seconds}秒${milliseconds}毫秒`;
    default:
      return date.toString();
  }
}

// 列出可用工具
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: 'get_current_time',
        description: '获取当前系统时间，支持多种格式输出',
        inputSchema: {
          type: 'object',
          properties: {
            format: {
              type: 'string',
              description: '时间格式：iso(ISO 8601), date(仅日期), time(仅时间), datetime(日期时间), full(完整中文), timestamp(时间戳), detailed(详细中文)',
              enum: ['iso', 'date', 'time', 'datetime', 'full', 'timestamp', 'detailed', 'default'],
              default: 'datetime',
            },
            timezone: {
              type: 'string',
              description: '时区（可选），例如：Asia/Shanghai, America/New_York',
            },
          },
        },
      },
      {
        name: 'get_time_info',
        description: '获取详细的时间信息，包括年、月、日、时、分、秒、星期等',
        inputSchema: {
          type: 'object',
          properties: {},
        },
      },
      {
        name: 'calculate_time_diff',
        description: '计算两个时间之间的差值',
        inputSchema: {
          type: 'object',
          properties: {
            start_time: {
              type: 'string',
              description: '开始时间（ISO 8601 格式或时间戳）',
            },
            end_time: {
              type: 'string',
              description: '结束时间（ISO 8601 格式或时间戳），留空则使用当前时间',
            },
          },
          required: ['start_time'],
        },
      },
    ],
  };
});

// 处理工具调用
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  if (name === 'get_current_time') {
    const format = (args?.format as string) || 'datetime';
    const timezone = args?.timezone as string | undefined;
    
    let date = new Date();
    
    // 如果指定了时区，转换时区
    if (timezone) {
      try {
        const dateStr = date.toLocaleString('zh-CN', { timeZone: timezone });
        date = new Date(dateStr);
      } catch (error) {
        return {
          content: [
            {
              type: 'text',
              text: `错误：无效的时区 "${timezone}"`,
            },
          ],
          isError: true,
        };
      }
    }
    
    const formattedTime = formatDateTime(date, format);
    
    return {
      content: [
        {
          type: 'text',
          text: `当前时间：${formattedTime}`,
        },
      ],
    };
  }

  if (name === 'get_time_info') {
    const now = new Date();
    
    const weekdays = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六'];
    const months = ['一月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '十一月', '十二月'];
    
    const info = {
      年: now.getFullYear(),
      月: now.getMonth() + 1,
      月份名称: months[now.getMonth()],
      日: now.getDate(),
      星期: weekdays[now.getDay()],
      小时: now.getHours(),
      分钟: now.getMinutes(),
      秒: now.getSeconds(),
      毫秒: now.getMilliseconds(),
      时间戳: now.getTime(),
      ISO格式: now.toISOString(),
      本地时间: now.toLocaleString('zh-CN'),
      UTC时间: now.toUTCString(),
    };
    
    const infoText = Object.entries(info)
      .map(([key, value]) => `${key}: ${value}`)
      .join('\n');
    
    return {
      content: [
        {
          type: 'text',
          text: `详细时间信息：\n\n${infoText}`,
        },
      ],
    };
  }

  if (name === 'calculate_time_diff') {
    const startTimeStr = args?.start_time as string;
    const endTimeStr = (args?.end_time as string) || new Date().toISOString();
    
    let startTime: Date;
    let endTime: Date;
    
    try {
      // 尝试解析为时间戳或 ISO 字符串
      startTime = isNaN(Number(startTimeStr)) 
        ? new Date(startTimeStr) 
        : new Date(Number(startTimeStr));
      
      endTime = isNaN(Number(endTimeStr)) 
        ? new Date(endTimeStr) 
        : new Date(Number(endTimeStr));
      
      if (isNaN(startTime.getTime()) || isNaN(endTime.getTime())) {
        throw new Error('无效的时间格式');
      }
    } catch (error) {
      return {
        content: [
          {
            type: 'text',
            text: '错误：无效的时间格式。请使用 ISO 8601 格式或时间戳。',
          },
        ],
        isError: true,
      };
    }
    
    const diffMs = Math.abs(endTime.getTime() - startTime.getTime());
    
    const days = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    const hours = Math.floor((diffMs % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((diffMs % (1000 * 60)) / 1000);
    const milliseconds = diffMs % 1000;
    
    return {
      content: [
        {
          type: 'text',
          text: `时间差：\n\n总毫秒数: ${diffMs}\n总秒数: ${Math.floor(diffMs / 1000)}\n总分钟数: ${Math.floor(diffMs / (1000 * 60))}\n总小时数: ${Math.floor(diffMs / (1000 * 60 * 60))}\n总天数: ${Math.floor(diffMs / (1000 * 60 * 60 * 24))}\n\n详细:\n${days} 天 ${hours} 小时 ${minutes} 分钟 ${seconds} 秒 ${milliseconds} 毫秒`,
        },
      ],
    };
  }

  throw new Error(`未知工具: ${name}`);
});

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('system-time MCP server 运行中...');
}

main().catch((error) => {
  console.error('服务器错误:', error);
  process.exit(1);
});
