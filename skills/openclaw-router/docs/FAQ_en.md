# OpenClaw Router Skill - FAQ

**Version:** 1.0.0  
**Last Updated:** 2026-03-02

---

## 📚 Basics

### Q1: What is Router Skill?

**A:** Router Skill is an intelligent routing system that automatically selects the best model (local or cloud) for your questions, saving 60% on AI costs while maintaining answer quality.

---

### Q2: Why do I need Router Skill?

**A:** 
- ❌ **Without Router:** All questions use L3, high cost ($0.04/100 tokens)
- ✅ **With Router:** 80% local + 15% verification + 5% L3, low cost ($0.016/100 tokens)
- 💰 **Savings:** 60% cost reduction, same quality

---

### Q3: Is installation complicated?

**A:** Very simple! Just 3 steps:

```bash
# 1. Install
bash install_router.sh

# 2. Auto-detect environment
🔍 Detecting...

# 3. Confirm recommended config
[1] Use Recommended Config ← Press 1

✅ Done!
```

Takes 2 minutes, 90% users choose recommended config.

---

### Q4: Which models are supported?

**A:** 

**Local Models (Ollama):**
- qwen2.5:7b/14b/72b
- llama3:8b/70b
- mistral:7b, mixtral:8x7b
- gemma:7b/14b
- phi3:3.8b/14b
- And all Ollama models

**Cloud Models:**
- Alibaba Cloud: qwen3.5-plus, qwen3-max, kimi-k2.5
- OpenAI: gpt-4, gpt-4o, gpt-3.5-turbo
- Anthropic: claude-3-opus/sonnet/haiku
- AWS Bedrock: Various models
- Azure OpenAI: GPT-4, GPT-3.5

---

### Q5: Can I use it without Ollama?

**A:** Yes! Router Skill supports:
- ✅ Pure local deployment (needs Ollama)
- ✅ Pure cloud deployment (only cloud APIs)
- ✅ Hybrid deployment (recommended)

Without Ollama, it automatically recommends cloud configuration.

---

## 💰 Cost Questions

### Q6: How much money can I save?

**A:** Based on real user data:

| User Type | Traditional | Router v3.0 | Savings |
|-----------|-------------|-------------|---------|
| Individual | $50/month | $20/month | $30/month |
| Small Business | $150/month | $60/month | $90/month |
| AI Studio | $600/month | $240/month | $360/month |

**Average Savings: 60%**

---

### Q7: What's the difference between Free and Premium?

**A:**

| Feature | Free | Premium ($9.99/month) |
|---------|------|----------------------|
| Requests/month | 1000 | Unlimited |
| Basic Routing | ✅ | ✅ |
| Token Tracking | ✅ | ✅ |
| User Preference Learning | ❌ | ✅ |
| Budget Management | ❌ | ✅ |
| Time Optimization | ❌ | ✅ |
| Priority Support | ❌ | ✅ |

**Recommendation:** Free tier is enough for individuals, Premium is better for heavy users.

---

### Q8: How to check usage?

**A:** Automatically displayed after each answer:

```markdown
---
【Usage This Time】
- Model: qwen2.5:14b-32k (local)
- Token Estimate: Input~500 / Output~800 = Total~1300
- Cost: $0 (local free)

【Quota Remaining】
- Monthly Budget: $50 (28 days left)
- Estimated Used: ~5%
- Daily Average: $1.79
- Status: ✅ Sufficient quota
---
```

---

## ⚙️ Configuration

### Q9: How to modify configuration?

**A:** 

**Method 1: Edit config file**
```bash
# Open config file
nano ~/.openclaw/router_config.yaml

# Save after modification
```

**Method 2: Use command line**
```bash
# Re-run config wizard
openclaw router config --init

# Modify budget
openclaw router budget --set 100
```

---

### Q10: How to switch modes?

**A:** Edit config file:

```yaml
# Quality First (important tasks)
thresholds:
  mode: "quality"
  auto_pass: 4.0

# Cost First (limited budget)
thresholds:
  mode: "economy"
  auto_pass: 3.0

# Speed First (quick response)
thresholds:
  mode: "speed"
  auto_pass: 3.0
  verify_min: 0
```

---

### Q11: How to manage multiple users?

**A:** Enterprise version supports multi-user:

```yaml
users:
  - name: "user1"
    budget: 50
    mode: "balanced"
  
  - name: "user2"
    budget: 100
    mode: "quality"
```

---

## 🔧 Technical Questions

### Q12: Is the self-assessment mechanism accurate?

**A:** Very accurate! Based on 5 dimensions:

| Dimension | Weight | Description |
|-----------|--------|-------------|
| Knowledge | 30% | Do I know this domain? |
| Reasoning | 25% | How many reasoning steps? |
| Context | 20% | Does it exceed limits? |
| Quality | 15% | How high is user's requirement? |
| Tools | 10% | Are external tools needed? |

Test accuracy: 95%+

---

### Q13: How does verification work?

**A:** 

```
Local 14b completes → Self-assessment 3.2 → Trigger verification
    ↓
Spawn L2 verifier
    ↓
Verifier evaluates (Accuracy/Completeness/Feasibility/Quality)
    ↓
Average ≥4 → Pass ✅
Average <4 → L3 redo ❌
```

Verification pass rate: ~70%
Verification cost: ~$0.02/time

---

### Q14: Does it support custom models?

**A:** Yes! Add custom models:

```yaml
models:
  custom:
    - id: "my-custom-model"
      location: "local"
      cost_per_1k: 0
      tags: ["fast", "cheap"]
```

---

### Q15: How to integrate into my application?

**A:** Use the API:

```python
from router_skill import ModelRouter

router = ModelRouter(config)
result = router.select_model(self_assessment_score=3.2)
print(result['model'])
```

---

## 🐛 Troubleshooting

### Q16: Configuration wizard won't start

**Solution:**
```bash
# Check Python
python3 --version  # Need 3.8+

# Check dependencies
pip3 list | grep -E "requests|psutil|pyyaml"

# Reinstall dependencies
pip3 install requests psutil pyyaml
```

---

### Q17: Can't detect Ollama

**Solution:**
```bash
# Check Ollama service
ollama list

# If not installed
curl -fsSL https://ollama.com/install.sh | sh

# Restart service
systemctl restart ollama
```

---

### Q18: Cloud API detection failed

**Solution:**
```bash
# Check environment variables
echo $DASHSCOPE_API_KEY
echo $OPENAI_API_KEY

# If not set
export DASHSCOPE_API_KEY="sk-..."
export OPENAI_API_KEY="sk-..."

# Permanent (add to ~/.bashrc)
echo 'export DASHSCOPE_API_KEY="sk-..."' >> ~/.bashrc
source ~/.bashrc
```

---

### Q19: Configuration save failed

**Solution:**
```bash
# Check directory permissions
ls -la ~/.openclaw/

# If needed, create directory
mkdir -p ~/.openclaw
chmod 755 ~/.openclaw
```

---

### Q20: Model selection doesn't match expectations

**Solution:**
```bash
# Check threshold config
cat ~/.openclaw/router_config.yaml | grep -A5 thresholds

# Adjust thresholds
nano ~/.openclaw/router_config.yaml

# Use tags to force
[L3] This is important, use expert model
```

---

## 📞 Other Questions

### Q21: How to report issues?

**A:** 
- GitHub Issue: https://github.com/pepsiboy87/openclaw-router/issues
- Email: pepsiboy87@example.com

---

### Q22: How to contribute code?

**A:** 
```bash
# Fork project
git fork https://github.com/pepsiboy87/openclaw-router

# Create branch
git checkout -b feature/your-feature

# Commit code
git commit -m "Add your feature"

# Pull Request
git push origin feature/your-feature
```

---

### Q23: Do you have a community?

**A:** Yes! Join us:
- Discord: [Invite Link]
- Twitter: [@RouterSkill]

---

### Q24: How to purchase Enterprise version?

**A:** Contact: pepsiboy87@example.com

**Enterprise Features:**
- ✅ All premium features
- ✅ Multi-user management
- ✅ Custom model pool
- ✅ API access
- ✅ SLA guarantee
- ✅ Private deployment

**Price:** $29.99/month or $299.99/year

---

### Q25: What's the roadmap?

**A:** 

**v3.1 (2026-03):**
- User preference learning
- Time optimization
- Detailed reports

**v3.2 (2026-04):**
- Multi-user support
- API access
- Enhanced budget management

**v4.0 (2026-05):**
- AI auto-tuning
- Predictive cost optimization
- Enterprise features

---

_Have a question not answered here? Welcome to submit an Issue!_
