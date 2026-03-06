// OpenClaw 新手指南 - 主要 JavaScript 功能

document.addEventListener('DOMContentLoaded', function() {
    // 默认选中"大模型常识"标签
    const basicsTab = document.querySelector('[data-tab="basics"]');
    if (basicsTab) {
        basicsTab.click();
    }

    initTabs();
    initFAQ();
    initCommands();
    initBestPractice();
});

// ==================== 标签页切换功能 ====================
function initTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabId = btn.getAttribute('data-tab');
            
            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));
            
            btn.classList.add('active');
            document.getElementById(tabId).classList.add('active');
        });
    });
}

// ==================== 视角切换功能 ====================
function switchPerspective(perspective) {
    const btns = document.querySelectorAll('.perspective-btn');
    const contents = document.querySelectorAll('.perspective-content');
    
    btns.forEach(btn => btn.classList.remove('active'));
    contents.forEach(content => content.classList.remove('active'));
    
    event.currentTarget.classList.add('active');
    document.getElementById(perspective + '-perspective').classList.add('active');
}

// ==================== 产业视角详情数据 ====================
const industryDetails = {
    'chip-vendor': {
        title: '芯片厂商',
        subtitle: 'Chip Vendor',
        icon: 'fas fa-microchip',
        simple: '提供 AI 计算能力的硬件基础。',
        detail: '芯片厂商是 AI 产业链的最上游，提供 GPU、TPU、NPU 等专用芯片，是 AI 计算能力的物理基础。',
        examples: [
            'NVIDIA：GPU 市场领导者，A100/H100 是训练大模型的主力',
            'AMD：MI300 系列挑战 NVIDIA 地位',
            'Intel：Gaudi2 等专用 AI 芯片',
            '国内：华为昇腾、寒武纪、摩尔线程等'
        ],
        whyMatters: '芯片性能直接决定 AI 模型的训练速度和推理成本，是 AI 产业的核心瓶颈之一。'
    },
    'cloud-provider': {
        title: '云服务商',
        subtitle: 'Cloud Service Provider',
        icon: 'fas fa-cloud',
        simple: '提供 AI 基础设施和算力租用服务。',
        detail: '云服务商提供 GPU 租赁、模型托管、数据存储等基础设施服务，让企业无需自建机房就能使用 AI。',
        examples: [
            '国际：AWS、Google Cloud、Azure',
            '国内：阿里云、腾讯云、华为云',
            '服务：GPU 租赁、模型 API、向量数据库等'
        ],
        whyMatters: '云服务商降低了 AI 使用门槛，让中小企业也能用上大模型。'
    },
    'model-company': {
        title: '基础模型公司',
        subtitle: 'Foundation Model Company',
        icon: 'fas fa-brain',
        simple: '训练和提供大模型的公司。',
        detail: '基础模型公司投入巨资训练大模型，通过 API 或开源方式提供给下游使用。',
        examples: [
            'OpenAI：GPT-4、DALL-E、Whisper',
            'Anthropic：Claude 3 系列',
            'Google：Gemini、PaLM',
            'Meta：LLaMA 系列（开源）',
            '国内：百度文心一言、阿里通义千问、智谱 GLM'
        ],
        whyMatters: '基础模型是 AI 应用的核心能力来源，决定了应用的天花板。'
    },
    'ai-framework': {
        title: 'AI应用框架',
        subtitle: 'AI Application Framework',
        icon: 'fas fa-puzzle-piece',
        simple: '帮助快速构建 AI 应用的开发框架。',
        detail: 'AI 应用框架封装了模型调用、Prompt 管理、Agent 编排等通用功能，让开发者专注于业务逻辑。',
        examples: [
            'LangChain：最流行的 LLM 应用开发框架',
            'OpenClaw：个人 AI 助手网关',
            'AutoGPT：自主 Agent 框架',
            'Dify：低代码 AI 应用开发平台'
        ],
        whyMatters: '框架大大降低了 AI 应用开发门槛，加速了 AI 落地。'
    },
    'vector-db': {
        title: '向量数据库',
        subtitle: 'Vector Database',
        icon: 'fas fa-database',
        simple: '存储和检索向量数据的专用数据库。',
        detail: '向量数据库将文本、图像等转换为向量存储，支持相似度搜索，是 RAG（检索增强生成）的核心组件。',
        examples: [
            'Pinecone：托管式向量数据库',
            'Milvus：开源向量数据库',
            'Weaviate：支持混合搜索',
            'Chroma：轻量级嵌入式向量数据库'
        ],
        whyMatters: '向量数据库让 AI 能够"记住"和"查找"信息，是实现长期记忆的关键。'
    },
    'ai-middleware': {
        title: 'AI中间件',
        subtitle: 'AI Middleware',
        icon: 'fas fa-layer-group',
        simple: '提供监控、安全、计费等企业级功能。',
        detail: 'AI 中间件填补了模型和应用之间的空白，提供生产环境必需的监控、安全、成本控制等功能。',
        examples: [
            '监控：LangSmith、Weights & Biases',
            '安全：Prompt 注入防护、内容审核',
            '计费：Token 使用量追踪、成本分摊',
            '测试：A/B 测试、模型评估'
        ],
        whyMatters: '中间件让 AI 从"实验"变成"可运营的生产系统"。'
    },
    'industry-app': {
        title: '行业应用',
        subtitle: 'Industry Application',
        icon: 'fas fa-building',
        simple: '针对特定行业的 AI 解决方案。',
        detail: '行业应用将 AI 能力与行业知识结合，解决特定场景的问题。',
        examples: [
            '医疗：辅助诊断、药物研发、病历分析',
            '金融：风控、投研、智能客服',
            '教育：个性化学习、作业批改、知识图谱',
            '法律：合同审查、案例分析、法律咨询'
        ],
        whyMatters: '行业应用是 AI 价值落地的最终场景，决定了 AI 的商业价值。'
    },
    'enterprise-digital': {
        title: '企业数字化',
        subtitle: 'Enterprise Digitalization',
        icon: 'fas fa-users',
        simple: '用 AI 提升企业运营效率。',
        detail: '企业数字化将 AI 融入企业日常工作流程，提升效率和降低成本。',
        examples: [
            '智能客服：7x24 小时自动应答',
            '办公助手：文档处理、会议纪要、邮件撰写',
            '知识管理：企业知识库、智能搜索',
            '流程自动化：RPA + AI 自动化业务流程'
        ],
        whyMatters: '企业数字化是 AI 最大的市场，每个企业都需要 AI 助手。'
    }
};

// ==================== 工程视角详情数据 ====================
const engineeringDetails = {
    'app-layer': {
        title: 'AI应用',
        subtitle: 'AI Application',
        icon: 'fas fa-mobile-alt',
        simple: '面向最终用户的 AI 产品。',
        detail: 'AI 应用是将 AI 能力包装成用户友好的产品，如 Copilot、客服机器人、写作助手等。',
        examples: [
            'GitHub Copilot：代码助手',
            'ChatGPT：对话式 AI',
            'Jasper：AI 写作助手',
            'Midjourney：AI 绘画'
        ],
        whyMatters: '应用层是用户接触 AI 的界面，决定了用户体验和产品价值。'
    },
    'saas': {
        title: 'SaaS产品',
        subtitle: 'Software as a Service',
        icon: 'fas fa-cloud-upload-alt',
        simple: '云端提供的 AI 服务。',
        detail: 'SaaS 产品将 AI 能力以订阅制方式提供，用户无需部署即可使用。',
        examples: [
            'Notion AI：智能笔记',
            'Canva AI：设计助手',
            'Salesforce Einstein：CRM AI',
            'Zendesk AI：客服 AI'
        ],
        whyMatters: 'SaaS 模式降低了 AI 使用门槛，让非技术用户也能用上 AI。'
    },
    'vertical-solution': {
        title: '行业方案',
        subtitle: 'Vertical Solution',
        icon: 'fas fa-industry',
        simple: '针对特定行业的定制化 AI 解决方案。',
        detail: '行业方案将 AI 与行业深度知识结合，解决行业特有问题。',
        examples: [
            '医疗：辅助诊断系统',
            '金融：智能投研平台',
            '制造：预测性维护',
            '零售：智能推荐系统'
        ],
        whyMatters: '行业方案是 AI 价值最大化的路径，深度 > 广度。'
    },
    'agent-layer': {
        title: 'Agent协作',
        subtitle: 'Agent Collaboration',
        icon: 'fas fa-user-astronaut',
        simple: '让 AI 自主完成复杂任务。',
        detail: 'Agent 是能自主思考、规划、执行的 AI 系统。多 Agent 协作可以完成更复杂的任务。',
        examples: [
            '任务拆解：将大任务分解为小步骤',
            '自主决策：根据情况选择行动',
            '工具调用：搜索、执行代码、调用 API',
            '反思优化：从结果中学习改进'
        ],
        whyMatters: 'Agent 是 AI 从"会聊天"到"能干活"的关键，是 AI 的未来方向。'
    },
    'workflow': {
        title: '工作流',
        subtitle: 'Workflow',
        icon: 'fas fa-project-diagram',
        simple: '管理多步骤 AI 任务流程。',
        detail: '工作流系统编排多个 AI 调用和工具使用，完成端到端的业务流程。',
        examples: [
            '客服流程：意图识别 → 知识检索 → 回答生成',
            '内容生产：选题 → 大纲 → 撰写 → 审核发布',
            '数据分析：数据收集 → 清洗 → 分析 → 报告生成'
        ],
        whyMatters: '工作流让 AI 能完成真实业务流程，而不仅仅是单点任务。'
    },
    'planning': {
        title: '任务规划',
        subtitle: 'Task Planning',
        icon: 'fas fa-tasks',
        simple: '让 AI 学会制定和执行计划。',
        detail: '任务规划是 Agent 的核心能力，包括目标分解、步骤规划、资源调度、进度跟踪等。',
        examples: [
            '目标分解：将"写一个网站"分解为设计、前端、后端、测试等子任务',
            '步骤规划：确定任务执行顺序和依赖关系',
            '资源调度：分配模型、工具、数据等资源',
            '进度跟踪：监控任务完成情况，动态调整'
        ],
        whyMatters: '规划能力决定了 Agent 能否完成复杂任务。'
    },
    'rag': {
        title: 'RAG',
        subtitle: 'Retrieval-Augmented Generation',
        icon: 'fas fa-search',
        simple: '让 AI 能够"查资料"再回答。',
        detail: 'RAG 将检索和生成结合，先从知识库检索相关信息，再让模型基于检索结果生成回答。',
        examples: [
            '企业知识库：员工可以问"公司的报销流程是什么"',
            '文档问答：上传 PDF，AI 基于文档回答问题',
            '客服系统：检索历史工单和知识库回答问题'
        ],
        whyMatters: 'RAG 解决了大模型知识过时和幻觉问题，是企业应用的核心技术。'
    },
    'finetune': {
        title: '微调',
        subtitle: 'Fine-tuning',
        icon: 'fas fa-sliders-h',
        simple: '用特定数据训练模型，让它更懂你的业务。',
        detail: '微调是在预训练模型基础上，用领域数据继续训练，让模型适应特定任务或行业。',
        examples: [
            'SFT（监督微调）：用标注数据训练',
            'LoRA：低成本微调方法',
            '领域适配：医疗、法律、金融等专业领域',
            '风格迁移：让模型按特定风格回答'
        ],
        whyMatters: '微调让通用模型变成专业模型，提升特定任务的表现。'
    },
    'tool-use': {
        title: 'Tool Use',
        subtitle: '工具使用',
        icon: 'fas fa-tools',
        simple: '让 AI 能够调用外部工具和系统。',
        detail: 'Tool Use 让模型不只是聊天，还能执行实际操作，如搜索、计算、调用 API 等。',
        examples: [
            'Function Calling：调用预定义函数',
            '代码执行：运行 Python 代码',
            'API 调用：查询天气、订票、发邮件',
            '文件操作：读取、写入、处理文件'
        ],
        whyMatters: '工具使用让 AI 从"聊天机器人"变成"数字助手"。'
    },
    'prompt-eng': {
        title: 'Prompt工程',
        subtitle: 'Prompt Engineering',
        icon: 'fas fa-edit',
        simple: '设计提示词，让模型输出更符合预期。',
        detail: 'Prompt 工程是通过精心设计的提示词，引导模型产生更好的输出。',
        examples: [
            'Few-shot：给几个示例让模型学习',
            'Chain-of-Thought：让模型一步步思考',
            'Role-playing：让模型扮演特定角色',
            '结构化输出：要求模型按 JSON、表格等格式输出'
        ],
        whyMatters: '好的 Prompt 可以显著提升模型输出质量，是使用 AI 的核心技能。'
    },
    'model-serving': {
        title: '基础模型',
        subtitle: 'Foundation Model',
        icon: 'fas fa-brain',
        simple: 'AI 系统的"大脑"。',
        detail: '基础模型是经过海量数据训练的大规模神经网络，是 AI 应用的核心能力来源。',
        examples: [
            'GPT-4：OpenAI 的旗舰模型',
            'Claude 3：Anthropic 的对话模型',
            'LLaMA：Meta 的开源模型系列',
            '文心一言：百度的中文大模型'
        ],
        whyMatters: '基础模型决定了 AI 系统的能力上限，是整个架构的核心。'
    },
    'inference': {
        title: '推理服务',
        subtitle: 'Inference Service',
        icon: 'fas fa-server',
        simple: '提供模型推理的 API 服务。',
        detail: '推理服务将模型部署为 API，支持高并发、低延迟的模型调用。',
        examples: [
            'OpenAI API：GPT-4 的 API 服务',
            'vLLM：高性能推理引擎',
            'TGI：HuggingFace 的推理容器',
            'TensorRT-LLM：NVIDIA 的推理优化库'
        ],
        whyMatters: '推理服务的性能直接决定用户体验和运营成本。'
    },
    'model-router': {
        title: '模型路由',
        subtitle: 'Model Router',
        icon: 'fas fa-route',
        simple: '智能选择最合适的模型。',
        detail: '模型路由根据任务类型、成本、延迟等因素，自动选择最合适的模型。',
        examples: [
            '成本优化：简单任务用小模型，复杂任务用大模型',
            '延迟优化：实时任务用快速模型',
            '能力匹配：代码任务用代码模型，对话用对话模型',
            '负载均衡：分散请求到多个模型实例'
        ],
        whyMatters: '模型路由可以显著降低成本、提升性能。'
    },
    'vector-db-layer': {
        title: '向量数据库',
        subtitle: 'Vector Database',
        icon: 'fas fa-database',
        simple: '存储和检索向量数据。',
        detail: '向量数据库将文本、图像等转换为向量存储，支持高效的相似度搜索。',
        examples: [
            'Pinecone：托管式向量数据库',
            'Milvus：开源向量数据库',
            'Weaviate：支持混合搜索',
            'Chroma：轻量级嵌入式向量数据库'
        ],
        whyMatters: '向量数据库是 RAG 和长期记忆的基础设施。'
    },
    'knowledge-graph': {
        title: '知识图谱',
        subtitle: 'Knowledge Graph',
        icon: 'fas fa-project-diagram',
        simple: '结构化的知识表示方式。',
        detail: '知识图谱以图结构存储实体和关系，支持复杂的知识推理和查询。',
        examples: [
            '实体关系：人物、地点、事件及其关系',
            '行业知识：医疗知识图谱、金融知识图谱',
            '企业知识：组织架构、业务流程、产品知识',
            '推理能力：基于关系发现隐含知识'
        ],
        whyMatters: '知识图谱让 AI 具备结构化知识，提升推理能力。'
    },
    'memory': {
        title: '记忆管理',
        subtitle: 'Memory Management',
        icon: 'fas fa-memory',
        simple: '让 AI 记住对话历史和用户偏好。',
        detail: '记忆管理系统负责存储和管理对话历史、用户信息、上下文等，支持长期记忆。',
        examples: [
            '短期记忆：当前对话的上下文',
            '长期记忆：用户偏好、历史对话',
            '工作记忆：当前任务相关的信息',
            '记忆检索：根据相关性召回历史信息'
        ],
        whyMatters: '记忆管理让 AI 能够持续对话、个性化服务。'
    },
    'monitoring': {
        title: '监控日志',
        subtitle: 'Monitoring & Logging',
        icon: 'fas fa-chart-line',
        simple: '实时监控 AI 系统运行状态。',
        detail: '监控系统追踪模型调用、性能指标、错误日志等，确保系统稳定运行。',
        examples: [
            '性能监控：延迟、吞吐量、错误率',
            '成本监控：Token 使用量、费用',
            '质量监控：输出质量、用户反馈',
            '告警系统：异常检测和通知'
        ],
        whyMatters: '监控是生产系统的必备能力，保障系统稳定。'
    },
    'security': {
        title: '安全审计',
        subtitle: 'Security & Audit',
        icon: 'fas fa-shield-alt',
        simple: '保护 AI 系统和数据安全。',
        detail: '安全系统防止 Prompt 注入、数据泄露、滥用等安全问题。',
        examples: [
            'Prompt 注入防护：检测和过滤恶意 Prompt',
            '内容审核：过滤敏感、有害内容',
            '数据脱敏：保护用户隐私',
            '访问控制：权限管理和审计日志'
        ],
        whyMatters: '安全是企业级 AI 系统的底线要求。'
    },
    'cost-control': {
        title: '成本控制',
        subtitle: 'Cost Control',
        icon: 'fas fa-coins',
        simple: '监控和优化 AI 使用成本。',
        detail: '成本控制系统追踪 Token 使用量，优化模型选择，控制运营成本。',
        examples: [
            'Token 计费监控：实时追踪使用量',
            '成本分摊：按部门、项目分摊费用',
            '优化建议：识别高成本场景',
            '预算控制：设置使用上限和告警'
        ],
        whyMatters: '成本控制让 AI 可持续运营，避免费用失控。'
    },
    'gpu': {
        title: 'GPU/TPU',
        subtitle: 'GPU/TPU',
        icon: 'fas fa-microchip',
        simple: 'AI 计算的硬件基础。',
        detail: 'GPU 和 TPU 是 AI 训练和推理的核心硬件，提供大规模并行计算能力。',
        examples: [
            'NVIDIA GPU：A100、H100、RTX 4090',
            'Google TPU：专用 AI 加速器',
            '华为昇腾：国产 AI 芯片',
            '性能指标：FLOPS、显存、带宽'
        ],
        whyMatters: '硬件性能直接决定 AI 系统的计算能力和成本。'
    },
    'cloud-infra': {
        title: '云平台',
        subtitle: 'Cloud Platform',
        icon: 'fas fa-cloud',
        simple: '提供弹性的计算资源。',
        detail: '云平台提供 GPU 租赁、存储、网络等基础设施服务，支持弹性扩展。',
        examples: [
            'AWS：EC2、SageMaker',
            'Google Cloud：Vertex AI',
            'Azure：Azure ML',
            '国内：阿里云 PAI、腾讯云 TI'
        ],
        whyMatters: '云平台让企业无需自建机房，快速部署 AI 系统。'
    },
    'container': {
        title: '容器化',
        subtitle: 'Containerization',
        icon: 'fas fa-cubes',
        simple: '标准化部署和运行 AI 应用。',
        detail: '容器技术（Docker、Kubernetes）让 AI 应用可以快速部署、弹性扩展。',
        examples: [
            'Docker：容器化 AI 应用',
            'Kubernetes：容器编排和管理',
            '自动扩缩容：根据负载动态调整',
            '服务网格：微服务治理'
        ],
        whyMatters: '容器化是现代 AI 系统部署的标准方式。'
    }
};

// ==================== 显示产业视角详情 ====================
function showIndustryDetail(moduleId) {
    const detail = industryDetails[moduleId];
    if (!detail) return;
    
    showModalContent(detail);
}

// ==================== 显示工程视角详情 ====================
function showEngineeringDetail(moduleId) {
    const detail = engineeringDetails[moduleId];
    if (!detail) return;
    
    showModalContent(detail);
}

// ==================== 显示弹窗内容 ====================
function showModalContent(detail) {
    const modal = document.getElementById('module-modal');
    const modalBody = document.getElementById('modal-body');
    
    let html = `
        <div class="modal-header">
            <div class="modal-icon">
                <i class="${detail.icon}"></i>
            </div>
            <div>
                <h2 class="modal-title">${detail.title}</h2>
                <p class="modal-subtitle">${detail.subtitle}</p>
            </div>
        </div>
    `;
    
    // 简单解释
    html += `
        <div class="modal-section">
            <div class="modal-section-title">
                <i class="fas fa-lightbulb"></i>
                <span>简单说</span>
            </div>
            <div class="simple-explanation">
                <p>${detail.simple}</p>
            </div>
        </div>
    `;
    
    // 详细解释
    html += `
        <div class="modal-section">
            <div class="modal-section-title">
                <i class="fas fa-info-circle"></i>
                <span>详细说明</span>
            </div>
            <div class="detail-explanation">
                <p>${detail.detail}</p>
            </div>
        </div>
    `;
    
    // 实例
    if (detail.examples) {
        html += `
            <div class="modal-section">
                <div class="modal-section-title">
                    <i class="fas fa-list"></i>
                    <span>实例</span>
                </div>
                <div class="modal-examples">
                    <ul>
                        ${detail.examples.map(ex => `<li>${ex}</li>`).join('')}
                    </ul>
                </div>
            </div>
        `;
    }
    
    // 为什么重要
    html += `
        <div class="modal-section">
            <div class="modal-section-title">
                <i class="fas fa-star"></i>
                <span>为什么重要</span>
            </div>
            <div class="modal-why-matters">
                <p>${detail.whyMatters}</p>
            </div>
        </div>
    `;
    
    modalBody.innerHTML = html;
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
}

// ==================== 关闭弹窗 ====================
function closeModal(event) {
    if (event && event.target !== event.currentTarget) return;
    
    const modal = document.getElementById('module-modal');
    modal.classList.remove('active');
    document.body.style.overflow = '';
}

// ESC 键关闭弹窗
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeModal();
    }
});


// ==================== FAQ 初始化 ====================
function initFAQ() {
    const faqData = [
        {
            category: 'install',
            question: '安装 OpenClaw 时提示 "command not found"',
            answer: `
                <p><strong>原因：</strong>OpenClaw 未正确安装或 PATH 配置问题。</p>
                <div class="tip-box">
                    <i class="fas fa-lightbulb"></i>
                    <p><strong>解决方案：</strong></p>
                </div>
                <ol>
                    <li>重新安装：npm install -g openclaw@latest</li>
                    <li>关闭终端重新打开</li>
                    <li>检查 PATH：echo $PATH</li>
                    <li>手动添加到 PATH：export PATH="$PATH:$(npm config get prefix)/bin"</li>
                </ol>
            `
        },
        {
            category: 'install',
            question: '安装时提示权限错误 EACCES',
            answer: `
                <p><strong>原因：</strong>npm 全局安装目录权限不足。</p>
                <div class="tip-box">
                    <i class="fas fa-lightbulb"></i>
                    <p><strong>解决方案：</strong></p>
                </div>
                <ol>
                    <li>推荐：使用 nvm 管理 Node.js</li>
                    <li>或使用 sudo：sudo npm install -g openclaw@latest</li>
                    <li>或修改 npm 全局目录权限</li>
                </ol>
            `
        },
        {
            category: 'install',
            question: 'Node.js 版本不兼容',
            answer: `
                <p><strong>原因：</strong>OpenClaw 需要 Node.js 22 或更高版本。</p>
                <div class="tip-box">
                    <i class="fas fa-lightbulb"></i>
                    <p><strong>解决方案：</strong></p>
                </div>
                <ol>
                    <li>检查 Node.js 版本：node --version</li>
                    <li>使用 nvm 安装 Node.js 22：nvm install 22</li>
                    <li>切换到 Node.js 22：nvm use 22</li>
                    <li>设置默认版本：nvm alias default 22</li>
                </ol>
            `
        },
        {
            category: 'install',
            question: 'npm 安装速度很慢或超时',
            answer: `
                <p><strong>原因：</strong>网络问题或 npm 源访问慢。</p>
                <div class="tip-box">
                    <i class="fas fa-lightbulb"></i>
                    <p><strong>解决方案：</strong></p>
                </div>
                <ol>
                    <li>使用淘宝镜像：npm config set registry https://registry.npmmirror.com</li>
                    <li>或使用 pnpm：npm install -g pnpm && pnpm add -g openclaw</li>
                    <li>配置代理：npm config set proxy http://your-proxy:port</li>
                    <li>使用 VPN 加速网络</li>
                </ol>
            `
        },
        {
            category: 'network',
            question: '无法连接到 AI 模型 API',
            answer: `
                <p><strong>原因：</strong>网络问题或 API Key 配置错误。</p>
                <div class="tip-box">
                    <i class="fas fa-lightbulb"></i>
                    <p><strong>解决方案：</strong></p>
                </div>
                <ol>
                    <li>检查网络连接</li>
                    <li>验证 API Key 是否正确</li>
                    <li>检查代理设置：export HTTP_PROXY=http://your-proxy:port</li>
                    <li>测试 API 连接：curl -I https://api.anthropic.com</li>
                </ol>
            `
        },
        {
            category: 'network',
            question: 'API 返回 401 Unauthorized 错误',
            answer: `
                <p><strong>原因：</strong>API Key 无效或已过期。</p>
                <div class="tip-box">
                    <i class="fas fa-lightbulb"></i>
                    <p><strong>解决方案：</strong></p>
                </div>
                <ol>
                    <li>检查 API Key 是否正确输入</li>
                    <li>在服务商官网验证 API Key 状态</li>
                    <li>检查 API Key 余额是否充足</li>
                    <li>重新生成 API Key 并配置</li>
                </ol>
            `
        },
        {
            category: 'network',
            question: 'API 返回 429 Too Many Requests',
            answer: `
                <p><strong>原因：</strong>请求频率超过限制。</p>
                <div class="tip-box">
                    <i class="fas fa-lightbulb"></i>
                    <p><strong>解决方案：</strong></p>
                </div>
                <ol>
                    <li>降低请求频率</li>
                    <li>检查并发连接数</li>
                    <li>联系服务商提升配额</li>
                    <li>使用多个 API Key 轮询</li>
                </ol>
            `
        },
        {
            category: 'gateway',
            question: 'Gateway 启动失败',
            answer: `
                <p><strong>原因：</strong>端口被占用或配置文件错误。</p>
                <div class="tip-box">
                    <i class="fas fa-lightbulb"></i>
                    <p><strong>解决方案：</strong></p>
                </div>
                <ol>
                    <li>检查端口占用：lsof -i :8080</li>
                    <li>修改端口：openclaw config set gateway.port 8081</li>
                    <li>检查配置文件：cat ~/.openclaw/openclaw.json</li>
                    <li>运行诊断：openclaw doctor</li>
                </ol>
            `
        },
        {
            category: 'gateway',
            question: 'Gateway 启动后立即退出',
            answer: `
                <p><strong>原因：</strong>配置错误或依赖缺失。</p>
                <div class="tip-box">
                    <i class="fas fa-lightbulb"></i>
                    <p><strong>解决方案：</strong></p>
                </div>
                <ol>
                    <li>查看错误日志：openclaw logs</li>
                    <li>检查 API Key 配置</li>
                    <li>验证模型配置是否正确</li>
                    <li>尝试重新安装：npm reinstall -g openclaw</li>
                </ol>
            `
        },
        {
            category: 'gateway',
            question: 'Gateway 占用内存过高',
            answer: `
                <p><strong>原因：</strong>上下文过长或并发连接过多。</p>
                <div class="tip-box">
                    <i class="fas fa-lightbulb"></i>
                    <p><strong>解决方案：</strong></p>
                </div>
                <ol>
                    <li>减少并发连接数</li>
                    <li>重启 Gateway 释放内存</li>
                    <li>升级服务器配置</li>
                </ol>
            `
        },
        {
            category: 'channel',
            question: 'Telegram Bot 无法接收消息',
            answer: `
                <p><strong>原因：</strong>Bot Token 配置错误或网络问题。</p>
                <div class="tip-box">
                    <i class="fas fa-lightbulb"></i>
                    <p><strong>解决方案：</strong></p>
                </div>
                <ol>
                    <li>验证 Bot Token：在 Telegram 中给 Bot 发送 /start</li>
                    <li>检查 Gateway 日志：openclaw logs</li>
                    <li>重新配置：openclaw channels add --channel telegram</li>
                    <li>检查网络代理设置</li>
                </ol>
            `
        },
        {
            category: 'channel',
            question: 'Telegram Bot 回复很慢',
            answer: `
                <p><strong>原因：</strong>网络延迟或模型响应慢。</p>
                <div class="tip-box">
                    <i class="fas fa-lightbulb"></i>
                    <p><strong>解决方案：</strong></p>
                </div>
                <ol>
                    <li>切换到更快的模型：claude-3-haiku</li>
                    <li>使用代理加速网络</li>
                    <li>检查 API 响应时间</li>
                    <li>减少消息长度</li>
                </ol>
            `
        },
        {
            category: 'channel',
            question: '如何配置多个 Telegram Bot',
            answer: `
                <p><strong>说明：</strong>OpenClaw 支持配置多个频道。</p>
                <div class="tip-box">
                    <i class="fas fa-lightbulb"></i>
                    <p><strong>配置步骤：</strong></p>
                </div>
                <ol>
                    <li>在 Telegram 创建多个 Bot</li>
                    <li>分别获取每个 Bot 的 Token</li>
                    <li>使用 openclaw channels add --channel telegram 添加频道</li>
                    <li>为每个频道配置不同的 Token</li>
                    <li>使用 openclaw channels list 查看所有频道</li>
                </ol>
            `
        },
        {
            category: 'performance',
            question: '响应速度很慢',
            answer: `
                <p><strong>原因：</strong>网络延迟、模型选择或系统资源不足。</p>
                <div class="tip-box">
                    <i class="fas fa-lightbulb"></i>
                    <p><strong>优化方案：</strong></p>
                </div>
                <ol>
                    <li>选择更快的模型：claude-3-haiku（最快）</li>
                    <li>使用代理加速网络</li>
                    <li>减少上下文长度</li>
                    <li>检查系统资源：top 或 htop</li>
                </ol>
            `
        },
        {
            category: 'performance',
            question: 'Token 消耗过快',
            answer: `
                <p><strong>原因：</strong>上下文过长或频繁调用。</p>
                <div class="tip-box">
                    <i class="fas fa-lightbulb"></i>
                    <p><strong>优化方案：</strong></p>
                </div>
                <ol>
                    <li>使用更简洁的提示词减少Token消耗</li>
                    <li>使用更便宜的模型：claude-3-haiku</li>
                    <li>开启流式响应减少等待</li>
                    <li>定期清理对话历史</li>
                </ol>
            `
        },
        {
            category: 'performance',
            question: 'Gateway CPU 占用过高',
            answer: `
                <p><strong>原因：</strong>并发请求过多或处理逻辑复杂。</p>
                <div class="tip-box">
                    <i class="fas fa-lightbulb"></i>
                    <p><strong>解决方案：</strong></p>
                </div>
                <ol>
                    <li>限制并发连接数</li>
                    <li>优化 Skill 代码</li>
                    <li>使用缓存减少重复计算</li>
                    <li>升级服务器配置</li>
                </ol>
            `
        },
        {
            category: 'config',
            question: '如何备份和恢复配置',
            answer: `
                <p><strong>说明：</strong>配置文件位于 ~/.openclaw/openclaw.json</p>
                <div class="tip-box">
                    <i class="fas fa-lightbulb"></i>
                    <p><strong>操作步骤：</strong></p>
                </div>
                <ol>
                    <li>备份配置：cp ~/.openclaw/openclaw.json ~/openclaw-backup.json</li>
                    <li>恢复配置：cp ~/openclaw-backup.json ~/.openclaw/openclaw.json</li>
                    <li>重启 Gateway 生效</li>
                </ol>
            `
        },
        {
            category: 'config',
            question: '如何切换不同的 AI 模型',
            answer: `
                <p><strong>说明：</strong>OpenClaw 支持多种 AI 模型。</p>
                <div class="tip-box">
                    <i class="fas fa-lightbulb"></i>
                    <p><strong>切换方法：</strong></p>
                </div>
                <ol>
                    <li>查看可用模型：openclaw models list</li>
                    <li>切换模型：openclaw models set &lt;model-id&gt;</li>
                    <li>或使用：openclaw config set models.default &lt;model-id&gt;</li>
                    <li>重启 Gateway 生效</li>
                </ol>
            `
        },
        {
            category: 'skill',
            question: '如何安装和使用 Skill',
answer: `
                <p><strong>说明：</strong>Skill 是扩展 OpenClaw 功能的插件。</p>
                <div class="tip-box">
                    <i class="fas fa-lightbulb"></i>
                    <p><strong>使用步骤：</strong></p>
                </div>
                <ol>
                    <li>查找 Skill：clawhub search &lt;关键词&gt;</li>
                    <li>安装 Skill：clawhub install &lt;slug&gt;</li>
                    <li>查看已安装：openclaw skills list</li>
                </ol>
            `
        },
        {
            category: 'skill',
            question: '如何开发自定义 Skill',
            answer: `
                <p><strong>说明：</strong>OpenClaw 支持自定义 Skill 开发。</p>
                <div class="tip-box">
                    <i class="fas fa-lightbulb"></i>
                    <p><strong>开发步骤：</strong></p>
                </div>
                <ol>
                    <li>创建 Skill 目录：mkdir ~/.openclaw/skills/my-skill</li>
                    <li>编写 skill.json 配置文件</li>
                    <li>实现 index.js 主逻辑</li>
                    <li>测试和调试 Skill</li>
                    <li>发布到社区（可选）</li>
                </ol>
            `
        }
    ];
    
    const faqList = document.getElementById('faq-list');
    if (!faqList) return;
    
    faqList.innerHTML = faqData.map((item, index) => `
        <div class="faq-item" data-category="${item.category}">
            <div class="faq-question" onclick="toggleFAQ(${index})">
                <span class="question-text">${item.question}</span>
                <i class="fas fa-chevron-down"></i>
            </div>
            <div class="faq-answer">
                <div class="faq-answer-content">
                    ${item.answer}
                </div>
            </div>
        </div>
    `).join('');
}

function toggleFAQ(index) {
    const items = document.querySelectorAll('.faq-item');
    items[index].classList.toggle('active');
}

// ==================== Commands 初始化 ====================
function initCommands() {
    const commandsData = [
        // 基础诊断
        {
            category: 'basic',
            name: 'openclaw status',
            desc: '查看系统状态',
            example: 'openclaw status'
        },
        {
            category: 'basic',
            name: 'openclaw health',
            desc: '检查Gateway健康状态',
            example: 'openclaw health'
        },
        {
            category: 'basic',
            name: 'openclaw doctor',
            desc: '诊断系统问题',
            example: 'openclaw doctor'
        },
        {
            category: 'basic',
            name: 'openclaw logs',
            desc: '查看运行日志',
            example: 'openclaw logs'
        },
        // Gateway管理
        {
            category: 'gateway',
            name: 'openclaw gateway start',
            desc: '启动 Gateway 服务',
            example: 'openclaw gateway start'
        },
        {
            category: 'gateway',
            name: 'openclaw gateway stop',
            desc: '停止 Gateway 服务',
            example: 'openclaw gateway stop'
        },
        {
            category: 'gateway',
            name: 'openclaw gateway restart',
            desc: '重启 Gateway 服务',
            example: 'openclaw gateway restart'
        },
        {
            category: 'gateway',
            name: 'openclaw gateway status',
            desc: '查看 Gateway 状态',
            example: 'openclaw gateway status'
        },
        // 配置管理
        {
            category: 'config',
            name: 'openclaw config get <key>',
            desc: '获取配置项',
            example: 'openclaw config get gateway.port'
        },
        {
            category: 'config',
            name: 'openclaw config set <key> <value>',
            desc: '设置配置项',
            example: 'openclaw config set gateway.port 18789'
        },
        {
            category: 'config',
            name: 'openclaw config unset <key>',
            desc: '删除配置项',
            example: 'openclaw config unset gateway.port'
        },
        // 频道管理
        {
            category: 'channel',
            name: 'openclaw channels list',
            desc: '列出所有频道',
            example: 'openclaw channels list'
        },
        {
            category: 'channel',
            name: 'openclaw channels add',
            desc: '添加频道',
            example: 'openclaw channels add --channel telegram'
        },
        {
            category: 'channel',
            name: 'openclaw channels remove',
            desc: '移除频道',
            example: 'openclaw channels remove --channel telegram'
        },
        // 模型管理
        {
            category: 'model',
            name: 'openclaw models list',
            desc: '列出可用模型',
            example: 'openclaw models list'
        },
        {
            category: 'model',
            name: 'openclaw models set <model>',
            desc: '设置默认模型',
            example: 'openclaw models set minimax-portal/MiniMax-M2.1'
        },
        // Skill管理
        {
            category: 'skill',
            name: 'openclaw skills list',
            desc: '列出已安装 Skill',
            example: 'openclaw skills list'
        },
        {
            category: 'skill',
            name: 'openclaw skills info <name>',
            desc: '查看 Skill 详情',
            example: 'openclaw skills info weather'
        },
        {
            category: 'skill',
            name: 'openclaw skills check',
            desc: '检查 Skill 状态',
            example: 'openclaw skills check'
        },
        {
            category: 'skill',
            name: 'clawhub search <query>',
            desc: '搜索 Skill',
            example: 'clawhub search weather'
        },
        {
            category: 'skill',
            name: 'clawhub install <slug>',
            desc: '安装 Skill',
            example: 'clawhub install weather'
        },
        // 更新升级
        {
            category: 'update',
            name: 'openclaw update',
            desc: '检查更新',
            example: 'openclaw update'
        },
        {
            category: 'update',
            name: 'openclaw --version',
            desc: '查看当前版本',
            example: 'openclaw --version'
        }
    ];
    
    const commandsGrid = document.getElementById('commands-grid');
    if (!commandsGrid) return;
    
    commandsGrid.innerHTML = commandsData.map(cmd => `
        <div class="command-card" data-category="${cmd.category}">
            <div class="command-name">
                <code>${cmd.name}</code>
                <button class="copy-btn" onclick="copyCommand('${cmd.example}')">
                    <i class="fas fa-copy"></i>
                </button>
            </div>
            <div class="command-desc">${cmd.desc}</div>
            <div class="command-example">
                <span>示例：</span>
                <code>${cmd.example}</code>
            </div>
        </div>
    `).join('');
}

function copyCommand(command) {
    navigator.clipboard.writeText(command).then(() => {
        alert('命令已复制到剪贴板');
    });
}

// ==================== BestPractice 初始化 ====================
function initBestPractice() {
    // 最佳实践部分已经在 HTML 中静态定义
    // 这里可以添加动态交互功能
}

// 复制代码功能
function copyCode(button) {
    const codeBlock = button.parentElement.querySelector('code');
    const text = codeBlock.textContent;
    navigator.clipboard.writeText(text).then(() => {
        const originalIcon = button.innerHTML;
        button.innerHTML = '<i class="fas fa-check"></i>';
        setTimeout(() => {
            button.innerHTML = originalIcon;
        }, 2000);
    });
}

// 步骤导航
let currentStep = 1;

function nextStep(step) {
    updateStep(step);
}

function prevStep(step) {
    updateStep(step);
}

function updateStep(step) {
    currentStep = step;
    
    // 更新步骤指示器
    document.querySelectorAll('.progress-steps .step').forEach((s, i) => {
        if (i < step) {
            s.classList.add('completed');
        } else {
            s.classList.remove('completed');
        }
        if (i + 1 === step) {
            s.classList.add('active');
        } else {
            s.classList.remove('active');
        }
    });
    
    // 更新进度条
    const progress = ((step - 1) / 5) * 100;
    document.getElementById('progress-fill').style.width = progress + '%';
    
    // 显示当前步骤内容
    document.querySelectorAll('.practice-step').forEach((s, i) => {
        if (i + 1 === step) {
            s.classList.add('active');
        } else {
            s.classList.remove('active');
        }
    });
}


// ==================== FAQ 搜索功能 ====================
function searchFAQ() {
    const searchTerm = document.getElementById('faq-search').value.toLowerCase();
    const items = document.querySelectorAll('.faq-item');
    
    items.forEach(item => {
        const question = item.querySelector('.question-text').textContent.toLowerCase();
        const answer = item.querySelector('.faq-answer-content').textContent.toLowerCase();
        
        if (question.includes(searchTerm) || answer.includes(searchTerm)) {
            item.style.display = 'block';
        } else {
            item.style.display = 'none';
        }
    });
}

// ==================== Commands 搜索功能 ====================
function searchCommands() {
    const searchTerm = document.getElementById('command-search').value.toLowerCase();
    const items = document.querySelectorAll('.command-card');
    
    items.forEach(item => {
        const name = item.querySelector('.command-name code').textContent.toLowerCase();
        const desc = item.querySelector('.command-desc').textContent.toLowerCase();
        
        if (name.includes(searchTerm) || desc.includes(searchTerm)) {
            item.style.display = 'block';
        } else {
            item.style.display = 'none';
        }
    });
}


// ==================== FAQ 标签过滤功能 ====================
document.addEventListener('DOMContentLoaded', function() {
    // FAQ 标签点击
    const faqCategoryBtns = document.querySelectorAll('.category-btn');
    faqCategoryBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const category = this.getAttribute('data-category');
            
            // 更新按钮状态
            faqCategoryBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            // 过滤 FAQ 项目
            const faqItems = document.querySelectorAll('.faq-item');
            faqItems.forEach(item => {
                if (category === 'all' || item.getAttribute('data-category') === category) {
                    item.style.display = 'block';
                } else {
                    item.style.display = 'none';
                }
            });
        });
    });
    
    // Commands 标签点击
    const commandCatBtns = document.querySelectorAll('.cat-btn');
    commandCatBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const category = this.getAttribute('data-cat');
            
            // 更新按钮状态
            commandCatBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            // 过滤命令卡片
            const commandCards = document.querySelectorAll('.command-card');
            commandCards.forEach(card => {
                if (category === 'all' || card.getAttribute('data-category') === category) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    });
});


// ==================== 基础术语详情 ====================
const termDetails = {
    token: {
        title: 'Token（令牌）',
        subtitle: 'AI 的"字"单位',
        icon: 'fas fa-coins',
        simple: '就像 AI 的"字"或"词"单位，一个汉字 ≈ 1-2 个 Token。',
        detail: 'AI 不像我们一样按"字"理解，而是把文本拆成一个个小片段，每个片段就是一个 Token。Token 越多，费用越高，就像打电话按分钟收费。',
        examples: [
            '一个汉字 ≈ 1-2 个 Token',
            '一个英文单词 ≈ 1-2 个 Token',
            '"你好世界" ≈ 4 个 Token'
        ],
        whyMatters: 'AI 模型按 Token 收费，就像打电话按分钟收费一样。Token 越多，费用越高。'
    },
    skill: {
        title: 'Skill（技能）',
        subtitle: '给 AI 助手安装的"插件"',
        icon: 'fas fa-puzzle-piece',
        simple: '给 AI 助手安装的"插件"或"扩展"。',
        detail: 'Skill 是一段代码，让 AI 助手能做特定的事情。就像给手机安装 App，手机就能做更多事。',
        examples: [
            '例子：天气查询 Skill、翻译 Skill、代码执行 Skill',
            '作用：扩展 AI 的能力边界',
            'OpenClaw：支持自定义 Skill'
        ],
        whyMatters: '有了 Skill，AI 就不只是聊天，还能真正帮你干活！'
    },
    agent: {
        title: 'Agent（智能体）',
        subtitle: '能自主思考和行动的 AI',
        icon: 'fas fa-user-astronaut',
        simple: '能自主思考和行动的 AI 助手。',
        detail: 'Agent 比普通 AI 更聪明，它能理解你的目标（而不是只回答问题）、自己规划步骤（分步完成任务）、使用工具（搜索、执行代码等）、根据结果调整策略。',
        examples: [
            '理解你的目标，而不是只回答问题',
            '自己规划步骤，分步完成任务',
            '使用工具（搜索、执行代码等）',
            '根据结果调整策略'
        ],
        whyMatters: 'Agent 是 AI 的未来，让 AI 从"聊天工具"变成"工作伙伴"。'
    },
    llm: {
        title: '大模型（LLM）',
        subtitle: 'Large Language Model',
        icon: 'fas fa-brain',
        simple: '一个超级聪明的"聊天机器人"，能对话、能创作、能推理。',
        detail: '大模型是经过海量数据训练的 AI，代表产品有 GPT-4、Claude 3、文心一言等。它能理解语言、回答问题、写代码，但有时会"胡说八道"（幻觉）。',
        examples: [
            '代表：GPT-4、Claude 3、文心一言等',
            '特点：能对话、能创作、能推理',
            '局限：可能会"胡说八道"（幻觉）'
        ],
        whyMatters: '大模型是当前 AI 的核心，OpenClaw 就是帮你用上这些大模型。'
    },
    neural: {
        title: '神经网络',
        subtitle: 'Neural Network',
        icon: 'fas fa-project-diagram',
        simple: '模仿人脑工作方式的计算机程序。',
        detail: '神经网络由很多"节点"连接而成，通过不断训练，这些连接会"学会"识别模式。深度学习就是有很多层的神经网络。',
        examples: [
            '就像教小孩子认字：看多了就认识了',
            '深度学习：有很多层的神经网络',
            '大模型本质上是超大的神经网络'
        ],
        whyMatters: '神经网络是 AI 的基础技术，理解它有助于明白 AI 是怎么"学习"的。'
    },
    api: {
        title: 'API（应用程序接口）',
        subtitle: 'Application Programming Interface',
        icon: 'fas fa-plug',
        simple: '程序之间"说话"的方式。',
        detail: 'API 就像餐厅的菜单，告诉你有哪些菜可以点，怎么点。程序通过 API 调用其他程序的功能。',
        examples: [
            'OpenClaw 通过 API 调用 AI 模型',
            '你需要 API Key 才能使用 AI 服务',
            '就像餐厅需要会员卡才能点菜'
        ],
        whyMatters: '理解 API 就明白为什么需要配置 API Key，以及 OpenClaw 是怎么工作的。'
    },
    'api-key': {
        title: 'API Key（密钥）',
        subtitle: '你的 AI 服务"会员卡号"',
        icon: 'fas fa-key',
        simple: '你的 AI 服务"会员卡号"。',
        detail: 'API Key 是一串字符，用来证明你有权限使用某个 AI 服务。就像密码一样，要保密！',
        examples: [
            '从 AI 服务商官网获取（如 Anthropic、OpenAI）',
            '配置到 OpenClaw 中才能使用',
            '按使用量计费，就像手机话费'
        ],
        warning: '不要把 API Key 发给别人，也不要上传到公开的代码仓库！',
        whyMatters: 'API Key 是使用 AI 服务的凭证，泄露会导致你的账户被盗用。'
    },
    gateway: {
        title: 'Gateway（网关）',
        subtitle: 'OpenClaw 的"心脏"',
        icon: 'fas fa-door-open',
        simple: 'OpenClaw 的"心脏"，负责所有中转工作。',
        detail: 'Gateway 是一个后台服务，负责连接 AI 模型（通过 API）、连接聊天软件（Telegram、WhatsApp 等）、中转消息、管理配置和日志等。',
        examples: [
            '连接 AI 模型（通过 API）',
            '连接聊天软件（Telegram、WhatsApp 等）',
            '中转消息：把你的问题发给 AI，把 AI 的回答发回给你',
            '管理配置、日志等'
        ],
        whyMatters: 'Gateway 必须一直运行，否则 AI 助手就无法工作。所以需要配置开机自启动。'
    },
    rag: {
        title: 'RAG（检索增强生成）',
        subtitle: 'Retrieval-Augmented Generation',
        icon: 'fas fa-search',
        simple: '让 AI 能够"查资料"再回答。',
        detail: 'RAG 将检索和生成结合，先从知识库检索相关信息，再让模型基于检索结果生成回答。解决了大模型知识过时和幻觉问题。',
        examples: [
            '企业知识库：员工可以问"公司的报销流程是什么"',
            '文档问答：上传 PDF，AI 基于文档回答问题',
            '客服系统：检索历史工单和知识库回答问题'
        ],
        whyMatters: 'RAG 是企业应用的核心技术，让 AI 能够基于真实数据回答问题。'
    },
    prompt: {
        title: 'Prompt（提示词）',
        subtitle: '给 AI 的指令',
        icon: 'fas fa-edit',
        simple: '你发给 AI 的指令或问题。',
        detail: 'Prompt 是你给 AI 的输入，可以是问题、指令或任务描述。好的 Prompt 可以让 AI 输出更好的结果。',
        examples: [
            '简单 Prompt："帮我写一篇文章"',
            '详细 Prompt："帮我写一篇关于 AI 的科普文章，500字左右，适合高中生阅读"',
            '结构化 Prompt：包含角色、任务、格式要求等'
        ],
        whyMatters: 'Prompt 工程是使用 AI 的核心技能，好的 Prompt 可以显著提升输出质量。'
    }
};

function showTermDetail(termId) {
    const detail = termDetails[termId];
    if (!detail) return;
    
    showModalContent(detail);
}
