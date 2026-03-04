import fs from 'fs';
import path from 'path';

/**
 * React Next.js 项目生成器
 * 根据需求文档和UI设计图生成完整的项目
 */

class ReactProjectGenerator {
  private projectName: string;
  private outputDir: string;
  
  constructor(projectName: string, outputDir: string) {
    this.projectName = projectName;
    this.outputDir = outputDir;
  }
  
  /**
   * 从需求文档和UI图生成项目
   */
  async generateFromRequirements(requirementsDoc: string, uiImagePath?: string) {
    console.log(`开始为项目 ${this.projectName} 生成代码`);
    
    // 1. 分析需求文档
    const parsedRequirements = await this.parseRequirements(requirementsDoc);
    
    // 2. 如果有UI图，分析UI元素
    let uiAnalysis = null;
    if (uiImagePath) {
      uiAnalysis = await this.analyzeUI(uiImagePath);
    }
    
    // 3. 创建项目结构
    await this.createProjectStructure();
    
    // 4. 生成页面组件
    await this.generatePages(parsedRequirements, uiAnalysis);
    
    // 5. 生成状态管理
    await this.generateStores(parsedRequirements);
    
    // 6. 生成共享组件
    await this.generateComponents(parsedRequirements, uiAnalysis);
    
    console.log(`项目 ${this.projectName} 生成完成！`);
    return `${this.outputDir}/${this.projectName}`;
  }
  
  /**
   * 解析需求文档
   */
  private async parseRequirements(doc: string): Promise<any> {
    // 这里应该实现实际的需求文档解析逻辑
    // 由于我们没有具体的需求文档格式，这里简化处理
    
    // 模拟解析过程
    const pages = this.extractPagesFromRequirements(doc);
    const features = this.extractFeaturesFromRequirements(doc);
    const components = this.extractComponentsFromRequirements(doc);
    
    return {
      pages,
      features,
      components,
      title: this.extractTitleFromRequirements(doc),
      description: this.extractDescriptionFromRequirements(doc)
    };
  }
  
  private extractPagesFromRequirements(doc: string): Array<{name: string, route: string, description: string}> {
    // 提取页面信息的简单实现
    const pageMatches = doc.match(/页面[:：]\s*([^\n]+)/gi) || [];
    return pageMatches.map((match, index) => {
      const pageStr = match.replace(/页面[:：]\s*/, '');
      const parts = pageStr.split(',').map(p => p.trim());
      return {
        name: parts[0] || `Page${index}`,
        route: parts[1] || `/${parts[0]?.toLowerCase() || `page${index}`}`,
        description: parts[2] || `页面描述`
      };
    });
  }
  
  private extractFeaturesFromRequirements(doc: string): string[] {
    // 提取功能特性的简单实现
    const featureMatches = doc.match(/功能[:：]\s*([^\n]+)/gi) || [];
    return featureMatches.map(match => match.replace(/功能[:：]\s*/, '').trim());
  }
  
  private extractComponentsFromRequirements(doc: string): string[] {
    // 提取组件的简单实现
    const componentMatches = doc.match(/组件[:：]\s*([^\n]+)/gi) || [];
    return componentMatches.map(match => match.replace(/组件[:：]\s*/, '').trim());
  }
  
  private extractTitleFromRequirements(doc: string): string {
    // 提取项目标题
    const titleMatch = doc.match(/项目名称[:：]\s*([^\n]+)/i);
    return titleMatch ? titleMatch[1].trim() : this.projectName;
  }
  
  private extractDescriptionFromRequirements(doc: string): string {
    // 提取项目描述
    const descMatch = doc.match(/描述[:：]\s*([^\n]+)/i);
    return descMatch ? descMatch[1].trim() : '基于需求文档生成的React应用';
  }
  
  /**
   * 分析UI设计图
   */
  private async analyzeUI(imagePath: string): Promise<any> {
    // 这里应该调用图像分析工具来识别UI元素
    // 返回识别出的组件、布局、颜色方案等信息
    console.log(`分析UI图像: ${imagePath}`);
    
    // 模拟UI分析结果
    return {
      layout: 'responsive',
      colors: {
        primary: '#1890ff',
        secondary: '#52c41a',
        background: '#fafafa'
      },
      components: [
        {
          type: 'header',
          props: { logo: true, navigation: true }
        },
        {
          type: 'sidebar',
          props: { collapsible: true }
        },
        {
          type: 'card',
          props: { shadow: true, rounded: true }
        }
      ],
      typography: {
        heading: 'Inter',
        body: 'Inter'
      }
    };
  }
  
  /**
   * 创建项目基本结构
   */
  private async createProjectStructure() {
    const projectPath = path.join(this.outputDir, this.projectName);
    
    // 创建目录结构
    const dirs = [
      'src',
      'src/app',
      'src/app/api',
      'src/app/components',
      'src/app/pages',
      'src/app/styles',
      'src/components',
      'src/stores',
      'src/utils',
      'public'
    ];
    
    for (const dir of dirs) {
      const fullPath = path.join(projectPath, dir);
      await fs.promises.mkdir(fullPath, { recursive: true });
    }
    
    // 创建基础文件
    await this.createBasicFiles(projectPath);
  }
  
  /**
   * 创建基础项目文件
   */
  private async createBasicFiles(projectPath: string) {
    // package.json
    const packageJson = {
      name: this.projectName,
      version: '0.1.0',
      private: true,
      scripts: {
        dev: 'next dev',
        build: 'next build',
        start: 'next start',
        lint: 'next lint'
      },
      dependencies: {
        'react': '^18',
        'react-dom': '^18',
        'next': '14.0.1',
        'antd': '^5.0.0',
        'zustand': '^4.4.0',
        '@ant-design/icons': '^5.0.0'
      },
      devDependencies: {
        'typescript': '^5',
        '@types/node': '^20',
        '@types/react': '^18',
        '@types/react-dom': '^18',
        'autoprefixer': '^10.4.16',
        'postcss': '^8',
        'tailwindcss': '^3.3.0',
        'eslint': '^8',
        'eslint-config-next': '14.0.1'
      }
    };
    
    await fs.promises.writeFile(
      path.join(projectPath, 'package.json'),
      JSON.stringify(packageJson, null, 2)
    );
    
    // tsconfig.json
    const tsConfig = {
      compilerOptions: {
        target: 'es5',
        lib: ['dom', 'dom.iterable', 'es6'],
        allowJs: true,
        skipLibCheck: true,
        strict: true,
        noEmit: true,
        esModuleInterop: true,
        module: 'esnext',
        moduleResolution: 'bundler',
        resolveJsonModule: true,
        isolatedModules: true,
        jsx: 'preserve',
        incremental: true,
        plugins: [
          {
            name: 'next'
          }
        ],
        baseUrl: '.',
        paths: {
          '@/*': ['./src/*']
        }
      },
      include: ['next-env.d.ts', '**/*.ts', '**/*.tsx', '.next/types/**/*.ts'],
      exclude: ['node_modules']
    };
    
    await fs.promises.writeFile(
      path.join(projectPath, 'tsconfig.json'),
      JSON.stringify(tsConfig, null, 2)
    );
    
    // tailwind.config.js
    const tailwindConfig = `
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
`;
    
    await fs.promises.writeFile(
      path.join(projectPath, 'tailwind.config.js'),
      tailwindConfig
    );
    
    // postcss.config.js
    const postcssConfig = `
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
`;
    
    await fs.promises.writeFile(
      path.join(projectPath, 'postcss.config.js'),
      postcssConfig
    );
  }
  
  /**
   * 生成页面组件
   */
  private async generatePages(requirements: any, uiAnalysis: any) {
    const projectPath = path.join(this.outputDir, this.projectName);
    const pagesDir = path.join(projectPath, 'src/app');
    
    // 如果需求中没有定义页面，则创建默认主页
    if (!requirements.pages || requirements.pages.length === 0) {
      const defaultPage = this.generateDefaultPage();
      await fs.promises.writeFile(path.join(pagesDir, 'page.tsx'), defaultPage);
    } else {
      // 为每个页面生成对应的文件
      for (const page of requirements.pages) {
        const routePath = page.route.startsWith('/') ? page.route.slice(1) : page.route;
        const pageDir = routePath === '' ? pagesDir : path.join(pagesDir, ...routePath.split('/'));
        
        if (routePath !== '') {
          await fs.promises.mkdir(pageDir, { recursive: true });
        }
        
        const pageContent = this.generatePageComponent(page, requirements, uiAnalysis);
        await fs.promises.writeFile(path.join(pageDir, 'page.tsx'), pageContent);
      }
    }
  }
  
  /**
   * 生成默认主页
   */
  private generateDefaultPage(): string {
    return `\
'use client';
import React from 'react';
import { Button, Card, Space, Typography } from 'antd';
import { PlusOutlined, MinusOutlined, ReloadOutlined } from '@ant-design/icons';
import MainLayout from '@/components/Layout';
import { useCounterStore } from '@/stores/useCounterStore';

const { Title, Text } = Typography;

export default function Home() {
  const { count, increment, decrement, reset } = useCounterStore();

  return (
    <MainLayout title="首页">
      <Card className="w-full max-w-md mx-auto shadow-lg">
        <Title level={2} className="text-center mb-6">计数器示例</Title>
        
        <div className="flex flex-col items-center">
          <div className="mb-6">
            <Text strong className="text-xl">
              当前计数: 
            </Text>
            <div className="text-4xl font-bold text-blue-600 my-2">{count}</div>
          </div>
          
          <Space size="middle">
            <Button 
              type="primary" 
              icon={<PlusOutlined />} 
              onClick={increment}
              className="bg-blue-500 hover:bg-blue-600"
            >
              增加
            </Button>
            <Button 
              type="default" 
              icon={<MinusOutlined />} 
              onClick={decrement}
            >
              减少
            </Button>
            <Button 
              type="ghost" 
              icon={<ReloadOutlined />} 
              onClick={reset}
            >
              重置
            </Button>
          </Space>
        </div>
      </Card>
      
      <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card title="特性 1" className="shadow-md">
          <p>使用 Ant Design 组件</p>
        </Card>
        <Card title="特性 2" className="shadow-md">
          <p>集成 Zustand 状态管理</p>
        </Card>
        <Card title="特性 3" className="shadow-md">
          <p>支持 Tailwind CSS 样式</p>
        </Card>
      </div>
    </MainLayout>
  );
}
`;
  }
  
  /**
   * 生成页面组件
   */
  private generatePageComponent(page: any, requirements: any, uiAnalysis: any): string {
    // 根据页面需求和UI分析生成具体的页面组件
    return `\
'use client';
import React from 'react';
import { Card, Typography } from 'antd';
import MainLayout from '@/components/Layout';

const { Title, Paragraph } = Typography;

export default function ${page.name}Page() {
  return (
    <MainLayout title="${page.name}">
      <div className="container mx-auto px-4 py-8">
        <Card className="shadow-lg">
          <Title level={2}>${page.name}</Title>
          <Paragraph>${page.description}</Paragraph>
          
          <div className="mt-6">
            <p>此页面是根据需求文档自动生成的。</p>
          </div>
        </Card>
      </div>
    </MainLayout>
  );
}
`;
  }
  
  /**
   * 生成状态管理(store)
   */
  private async generateStores(requirements: any) {
    const projectPath = path.join(this.outputDir, this.projectName);
    const storesDir = path.join(projectPath, 'src/stores');
    
    // 根据需求中的功能生成相应的store
    if (requirements.features && requirements.features.length > 0) {
      for (const feature of requirements.features) {
        const storeName = this.toCamelCase(feature.split(' ')[0]);
        const storeContent = this.generateStore(storeName, feature);
        await fs.promises.writeFile(
          path.join(storesDir, `${storeName}Store.ts`),
          storeContent
        );
      }
    }
    
    // 如果没有特定功能，生成一个示例store
    if (!requirements.features || requirements.features.length === 0) {
      const exampleStore = this.generateExampleStore();
      await fs.promises.writeFile(
        path.join(storesDir, 'useCounterStore.ts'),
        exampleStore
      );
    }
  }
  
  /**
   * 生成示例store
   */
  private generateExampleStore(): string {
    return `\
import { create } from 'zustand';

interface CounterState {
  count: number;
  increment: () => void;
  decrement: () => void;
  reset: () => void;
}

export const useCounterStore = create<CounterState>((set) => ({
  count: 0,
  increment: () => set((state) => ({ count: state.count + 1 })),
  decrement: () => set((state) => ({ count: state.count - 1 })),
  reset: () => set({ count: 0 }),
}));
`;
  }
  
  /**
   * 生成特定功能的store
   */
  private generateStore(storeName: string, feature: string): string {
    return `\
import { create } from 'zustand';

interface ${this.toPascalCase(storeName)}State {
  // TODO: Define state structure based on feature: ${feature}
  data: any[];
  loading: boolean;
  error: string | null;
  
  // Actions
  fetchData: () => Promise<void>;
  addItem: (item: any) => void;
  updateItem: (id: string, item: any) => void;
  removeItem: (id: string) => void;
}

export const use${this.toPascalCase(storeName)}Store = create<${this.toPascalCase(storeName)}State>((set, get) => ({
  data: [],
  loading: false,
  error: null,
  
  fetchData: async () => {
    set({ loading: true, error: null });
    try {
      // TODO: Implement fetch logic for ${feature}
      // const response = await fetch('/api/...');
      // const data = await response.json();
      // set({ data, loading: false });
    } catch (error) {
      set({ error: error.message, loading: false });
    }
  },
  
  addItem: (item) => {
    set((state) => ({ data: [...state.data, item] }));
  },
  
  updateItem: (id, item) => {
    set((state) => ({
      data: state.data.map((i) => (i.id === id ? item : i))
    }));
  },
  
  removeItem: (id) => {
    set((state) => ({
      data: state.data.filter((i) => i.id !== id)
    }));
  }
}));
`;
  }
  
  /**
   * 生成共享组件
   */
  private async generateComponents(requirements: any, uiAnalysis: any) {
    const projectPath = path.join(this.outputDir, this.projectName);
    const componentsDir = path.join(projectPath, 'src/components');
    
    // 生成布局组件
    const layoutComponent = this.generateLayoutComponent(uiAnalysis);
    await fs.promises.writeFile(
      path.join(componentsDir, 'Layout.tsx'),
      layoutComponent
    );
    
    // 如果需求中指定了特定组件，生成这些组件
    if (requirements.components && requirements.components.length > 0) {
      for (const componentName of requirements.components) {
        const componentContent = this.generateComponent(componentName, uiAnalysis);
        await fs.promises.writeFile(
          path.join(componentsDir, `${componentName}.tsx`),
          componentContent
        );
      }
    }
  }
  
  /**
   * 生成布局组件
   */
  private generateLayoutComponent(uiAnalysis: any): string {
    return `\
import React, { ReactNode } from 'react';
import Head from 'next/head';
import { Layout as AntLayout, Menu, theme } from 'antd';
import { AppstoreOutlined, MailOutlined, SettingOutlined } from '@ant-design/icons';

const { Header, Content, Footer } = AntLayout;

interface LayoutProps {
  children: ReactNode;
  title?: string;
}

const MainLayout: React.FC<LayoutProps> = ({ children, title = 'My App' }) => {
  const {
    token: { colorBgContainer },
  } = theme.useToken();

  return (
    <div className="ant-layout">
      <Head>
        <title>{title}</title>
        <meta name="description" content="Generated by create next app" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      
      <Header className="header bg-blue-600 text-white">
        <div className="logo text-xl font-bold">LOGO</div>
        <Menu
          theme="dark"
          mode="horizontal"
          defaultSelectedKeys={['2']}
          items={[
            {
              key: '1',
              label: '首页',
              icon: <AppstoreOutlined />,
            },
            {
              key: '2',
              label: '产品',
              icon: <MailOutlined />,
            },
            {
              key: '3',
              label: '关于我们',
              icon: <SettingOutlined />,
            },
          ]}
          className="bg-blue-600"
        />
      </Header>
      
      <Content style={{ padding: '0 50px' }}>
        <div className="bg-gray-100 rounded-lg p-6 min-h-[calc(100vh-230px)] mt-4">
          {children}
        </div>
      </Content>
      
      <Footer style={{ textAlign: 'center' }} className="mt-10">
        Ant Design ©{new Date().getFullYear()} Created by Ant UED
      </Footer>
    </div>
  );
};

export default MainLayout;
`;
  }
  
  /**
   * 生成特定组件
   */
  private generateComponent(componentName: string, uiAnalysis: any): string {
    return `\
import React from 'react';
import { Card, Typography } from 'antd';

const { Title, Text } = Typography;

interface ${this.toPascalCase(componentName)}Props {
  // TODO: Define props based on requirements
}

const ${this.toPascalCase(componentName)}: React.FC<${this.toPascalCase(componentName)}Props> = ({}) => {
  return (
    <Card className="shadow-md">
      <Title level={4}>${componentName}</Title>
      <Text>This is a generated component based on your requirements.</Text>
    </Card>
  );
};

export default ${this.toPascalCase(componentName)};
`;
  }
  
  /**
   * 辅助函数：转换为驼峰命名
   */
  private toCamelCase(str: string): string {
    return str
      .replace(/[^a-zA-Z0-9]/g, ' ')
      .split(' ')
      .filter(word => word.length > 0)
      .map((word, index) => {
        if (index === 0) {
          return word.toLowerCase();
        }
        return word.charAt(0).toUpperCase() + word.slice(1).toLowerCase();
      })
      .join('');
  }
  
  /**
   * 辅助函数：转换为帕斯卡命名
   */
  private toPascalCase(str: string): string {
    return str
      .replace(/[^a-zA-Z0-9]/g, ' ')
      .split(' ')
      .filter(word => word.length > 0)
      .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
      .join('');
  }
}

// 导出类供外部使用
export default ReactProjectGenerator;