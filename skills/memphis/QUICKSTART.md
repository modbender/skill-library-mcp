# Memphis Quick Start Guide

**Get started with Memphis in 5 minutes!** 🚀

---

## 📦 Installation (30 seconds)

```bash
# Install Memphis from ClawHub
clawhub install memphis
```

---

## 🚀 Initialization (2 minutes)

### **Option 1: Interactive Setup**
```bash
memphis init
```

Follow the prompts:
- Agent name
- Role
- Location
- LLM provider (Ollama recommended)

### **Option 2: Quick Setup**
```bash
memphis init --identity "YourAgent" --role "Assistant" --location "localhost"
```

---

## 🧠 First Memory (1 minute)

```bash
# Create your first memory
memphis journal "Hello Memphis! I'm your first memory!" --tags first,hello

# Search your memory
memphis ask "What is my first memory?" --provider ollama
```

---

## 🎯 First Decision (1 minute)

```bash
# Record a conscious decision
memphis decide "Framework choice" "React" \
  --options "React|Vue|Angular" \
  --reasoning "Best ecosystem and community support" \
  --tags tech,frontend

# View your decision
memphis show decision 1
```

---

## 🔮 Predict (30 seconds)

```bash
# See predicted decisions
memphis predict

# Enable learning mode
memphis predict --learn
```

---

## ✅ Done!

Your Memphis brain is now ready!

### **What's Next?**

1. **Daily Usage:**
   ```bash
   memphis journal "Learned X" --tags learning
   memphis decide "Use Y" -r "Because Z"
   memphis ask "What did I decide?"
   ```

2. **Explore Features:**
   ```bash
   memphis --help
   memphis status
   memphis doctor
   ```

3. **Advanced:**
   ```bash
   memphis graph build
   memphis share-sync
   memphis reflect --daily
   ```

---

## 📚 Resources

- **Full Docs:** SKILL.md
- **GitHub:** https://github.com/elathoxu-crypto/memphis
- **Discord:** https://discord.com/invite/clawd

---

## 🆘 Need Help?

```bash
# Health check
memphis doctor

# View logs
cat ~/.memphis/logs/memphis.log

# Ask community
# Discord: #memphis channel
```

---

**You're ready!** 🎉

Start building your AI brain now!
