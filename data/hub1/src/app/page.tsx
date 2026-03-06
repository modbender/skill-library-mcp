'use client'

import { motion, useScroll, useTransform } from 'framer-motion'
import { useRef } from 'react'
import dynamic from 'next/dynamic'
import Logo from '@/components/Logo'

const ParticleField = dynamic(() => import('@/components/ParticleField'), {
  ssr: false,
})

const Playground = dynamic(() => import('@/components/Playground'), {
  ssr: false,
})

const fadeInUp = {
  initial: { opacity: 0, y: 40 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.8, ease: [0.25, 0.4, 0.25, 1] }
}

const staggerContainer = {
  animate: {
    transition: {
      staggerChildren: 0.1
    }
  }
}

function Navbar() {
  return (
    <motion.header
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="fixed top-0 left-0 right-0 z-50 border-b border-white/5 bg-black/50 backdrop-blur-xl"
    >
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <Logo />
        <nav className="hidden md:flex items-center gap-8">
          <a href="#playground" className="text-sm text-zinc-400 hover:text-white transition-colors duration-300">Try It</a>
          <a href="#features" className="text-sm text-zinc-400 hover:text-white transition-colors duration-300">Features</a>
          <a href="/docs" className="text-sm text-zinc-400 hover:text-white transition-colors duration-300">Docs</a>
          <a href="/dashboard" className="text-sm text-zinc-400 hover:text-white transition-colors duration-300">Dashboard</a>
        </nav>
        <a
          href="https://x.com/openclawdy"
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-white/10 rounded-full hover:bg-white/20 transition-all duration-300"
        >
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
            <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
          </svg>
          Follow
        </a>
      </div>
    </motion.header>
  )
}

function Hero() {
  const ref = useRef(null)
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start start", "end start"]
  })
  const opacity = useTransform(scrollYProgress, [0, 0.5], [1, 0])
  const scale = useTransform(scrollYProgress, [0, 0.5], [1, 0.95])

  return (
    <motion.section
      ref={ref}
      style={{ opacity, scale }}
      className="relative min-h-screen flex items-center justify-center overflow-hidden"
    >
      <ParticleField />

      <div className="relative z-10 max-w-5xl mx-auto px-6 text-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
          className="inline-flex items-center gap-2 px-4 py-2 mb-8 text-xs font-medium text-zinc-400 bg-white/5 border border-white/10 rounded-full backdrop-blur-sm"
        >
          <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse" />
          Now in Beta
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.1 }}
          className="text-5xl sm:text-6xl md:text-7xl lg:text-8xl font-bold tracking-tight leading-[0.9]"
        >
          <span className="block text-white">Persistent</span>
          <span className="block text-white/40">Memory</span>
          <span className="block text-white/20">for Agents</span>
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.3 }}
          className="mt-8 text-lg md:text-xl text-zinc-500 max-w-2xl mx-auto leading-relaxed"
        >
          Memory infrastructure for OpenClaw agents and all autonomous systems. Store context, recall knowledge, build smarter agents.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.5 }}
          className="mt-12 flex flex-col sm:flex-row gap-4 justify-center"
        >
          <a
            href="/dashboard"
            className="group relative px-8 py-4 text-sm font-semibold text-black bg-white rounded-full overflow-hidden transition-transform duration-300 hover:scale-105"
          >
            <span className="relative z-10">Launch Dashboard</span>
            <div className="absolute inset-0 bg-gradient-to-r from-white via-zinc-200 to-white opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
          </a>
          <a
            href="/docs"
            className="px-8 py-4 text-sm font-semibold text-white border border-white/20 rounded-full hover:bg-white/5 hover:border-white/40 transition-all duration-300"
          >
            Read Docs
          </a>
        </motion.div>
      </div>

      <div className="absolute bottom-12 left-1/2 -translate-x-1/2">
        <motion.div
          animate={{ y: [0, 8, 0] }}
          transition={{ duration: 2, repeat: Infinity }}
          className="w-6 h-10 border-2 border-white/20 rounded-full flex justify-center pt-2"
        >
          <div className="w-1 h-2 bg-white/40 rounded-full" />
        </motion.div>
      </div>
    </motion.section>
  )
}

function Problem() {
  const problems = [
    {
      icon: (
        <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M9.75 9.75l4.5 4.5m0-4.5l-4.5 4.5M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
      title: 'Session Amnesia',
      description: 'Every session ends, memory vanishes. Agents start from zero, every single time.'
    },
    {
      icon: (
        <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182m0-4.991v4.99" />
        </svg>
      ),
      title: 'Repeated Mistakes',
      description: 'No learning from past interactions. Same errors, same explanations, infinite loop.'
    },
    {
      icon: (
        <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
      title: 'Wasted Context',
      description: 'Hours spent explaining preferences, project context, and decisions—gone instantly.'
    }
  ]

  return (
    <section className="py-32 border-t border-white/5">
      <div className="max-w-7xl mx-auto px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-20"
        >
          <span className="text-xs font-medium tracking-widest text-zinc-500 uppercase">The Problem</span>
          <h2 className="mt-4 text-4xl md:text-5xl font-bold text-white">
            Agents have amnesia
          </h2>
        </motion.div>

        <motion.div
          variants={staggerContainer}
          initial="initial"
          whileInView="animate"
          viewport={{ once: true }}
          className="grid md:grid-cols-3 gap-6"
        >
          {problems.map((problem, i) => (
            <motion.div
              key={i}
              variants={fadeInUp}
              className="group p-8 bg-gradient-to-b from-white/[0.03] to-transparent border border-white/5 rounded-2xl hover:border-white/10 transition-all duration-500"
            >
              <div className="w-12 h-12 flex items-center justify-center text-zinc-500 bg-white/5 rounded-xl mb-6 group-hover:text-white group-hover:bg-white/10 transition-all duration-300">
                {problem.icon}
              </div>
              <h3 className="text-lg font-semibold text-white mb-3">{problem.title}</h3>
              <p className="text-zinc-500 leading-relaxed">{problem.description}</p>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  )
}

function Features() {
  const features = [
    {
      title: 'Semantic Storage',
      description: 'Store memories with meaning. Facts, preferences, decisions, learnings—all indexed for intelligent retrieval.',
      code: `POST /api/memory/store
{
  "content": "User prefers TypeScript",
  "type": "preference"
}`
    },
    {
      title: 'Instant Recall',
      description: 'Query by meaning, not keywords. Find relevant context across thousands of memories in milliseconds.',
      code: `POST /api/memory/recall
{
  "query": "coding preferences",
  "limit": 5
}`
    },
    {
      title: 'Wallet Auth',
      description: 'No API keys. Authenticate with your agent wallet signature. Each wallet gets an isolated vault.',
      code: `Headers:
X-Agent-Address: 0x...
X-Agent-Signature: 0x...`
    },
    {
      title: 'OpenClaw Native',
      description: 'Install as a skill. Any OpenClaw agent can store and recall memories with zero configuration.',
      code: `openclaw skill install openclawdy`
    }
  ]

  return (
    <section id="features" className="py-32 border-t border-white/5">
      <div className="max-w-7xl mx-auto px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-20"
        >
          <span className="text-xs font-medium tracking-widest text-zinc-500 uppercase">Features</span>
          <h2 className="mt-4 text-4xl md:text-5xl font-bold text-white">
            Built for Agents
          </h2>
        </motion.div>

        <motion.div
          variants={staggerContainer}
          initial="initial"
          whileInView="animate"
          viewport={{ once: true }}
          className="grid md:grid-cols-2 gap-6"
        >
          {features.map((feature, i) => (
            <motion.div
              key={i}
              variants={fadeInUp}
              className="group relative p-8 bg-gradient-to-b from-white/[0.03] to-transparent border border-white/5 rounded-2xl hover:border-white/10 transition-all duration-500 overflow-hidden"
            >
              <div className="absolute top-0 right-0 w-40 h-40 bg-white/[0.02] rounded-full blur-3xl -translate-y-1/2 translate-x-1/2 group-hover:bg-white/[0.04] transition-all duration-500" />

              <h3 className="text-xl font-semibold text-white mb-3">{feature.title}</h3>
              <p className="text-zinc-500 leading-relaxed mb-6">{feature.description}</p>

              <div className="relative">
                <pre className="p-4 bg-black/50 border border-white/5 rounded-xl text-sm text-zinc-400 overflow-x-auto font-mono">
                  {feature.code}
                </pre>
              </div>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  )
}

function Pricing() {
  const tiers = [
    { action: 'Store Memory', price: '$0.001', description: 'Per memory stored' },
    { action: 'Recall Query', price: '$0.005', description: 'Per semantic search' },
    { action: 'Bulk Store', price: '$0.0008', description: 'Per memory in batch' },
    { action: 'Export Vault', price: '$0.02', description: 'Full backup download' },
  ]

  return (
    <section id="pricing" className="py-32 border-t border-white/5">
      <div className="max-w-7xl mx-auto px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-20"
        >
          <span className="text-xs font-medium tracking-widest text-zinc-500 uppercase">Pricing</span>
          <h2 className="mt-4 text-4xl md:text-5xl font-bold text-white">
            Pay only for what you use
          </h2>
          <p className="mt-4 text-zinc-500 max-w-xl mx-auto">
            No subscriptions. No commitments. Simple per-action pricing designed for autonomous agents.
          </p>
        </motion.div>

        <motion.div
          variants={staggerContainer}
          initial="initial"
          whileInView="animate"
          viewport={{ once: true }}
          className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4"
        >
          {tiers.map((tier, i) => (
            <motion.div
              key={i}
              variants={fadeInUp}
              className="group p-6 bg-gradient-to-b from-white/[0.03] to-transparent border border-white/5 rounded-2xl hover:border-white/20 hover:from-white/[0.06] transition-all duration-500 text-center"
            >
              <div className="text-3xl font-bold text-white mb-1">{tier.price}</div>
              <div className="text-sm font-medium text-white/80 mb-2">{tier.action}</div>
              <div className="text-xs text-zinc-500">{tier.description}</div>
            </motion.div>
          ))}
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="mt-12 p-8 bg-gradient-to-r from-white/[0.03] via-white/[0.05] to-white/[0.03] border border-white/10 rounded-2xl text-center"
        >
          <div className="text-lg font-semibold text-white mb-2">Free Tier Included</div>
          <div className="text-zinc-400">
            Every agent gets <span className="text-white font-medium">1,000 memories</span> and <span className="text-white font-medium">100 recalls/day</span> free.
          </div>
        </motion.div>
      </div>
    </section>
  )
}

function API() {
  const endpoints = [
    { method: 'POST', path: '/api/memory/store', desc: 'Store a new memory' },
    { method: 'POST', path: '/api/memory/recall', desc: 'Semantic search' },
    { method: 'GET', path: '/api/memory/list', desc: 'List all memories' },
    { method: 'GET', path: '/api/memory/{id}', desc: 'Get specific memory' },
    { method: 'DELETE', path: '/api/memory/{id}', desc: 'Delete a memory' },
    { method: 'GET', path: '/api/memory/vault', desc: 'Export all memories' },
    { method: 'DELETE', path: '/api/memory/vault', desc: 'Clear entire vault' },
    { method: 'GET', path: '/api/agent/stats', desc: 'Usage statistics' },
  ]

  const methodColors: Record<string, string> = {
    GET: 'text-emerald-400 bg-emerald-400/10',
    POST: 'text-blue-400 bg-blue-400/10',
    DELETE: 'text-red-400 bg-red-400/10',
  }

  return (
    <section id="api" className="py-32 border-t border-white/5">
      <div className="max-w-7xl mx-auto px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-20"
        >
          <span className="text-xs font-medium tracking-widest text-zinc-500 uppercase">API Reference</span>
          <h2 className="mt-4 text-4xl md:text-5xl font-bold text-white">
            Simple. Powerful. Fast.
          </h2>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="overflow-hidden border border-white/5 rounded-2xl"
        >
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-white/5 bg-white/[0.02]">
                  <th className="px-6 py-4 text-left text-xs font-medium text-zinc-500 uppercase tracking-wider">Method</th>
                  <th className="px-6 py-4 text-left text-xs font-medium text-zinc-500 uppercase tracking-wider">Endpoint</th>
                  <th className="px-6 py-4 text-left text-xs font-medium text-zinc-500 uppercase tracking-wider">Description</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {endpoints.map((endpoint, i) => (
                  <tr key={i} className="hover:bg-white/[0.02] transition-colors duration-200">
                    <td className="px-6 py-4">
                      <span className={`px-2.5 py-1 text-xs font-medium rounded-md ${methodColors[endpoint.method]}`}>
                        {endpoint.method}
                      </span>
                    </td>
                    <td className="px-6 py-4 font-mono text-sm text-zinc-300">{endpoint.path}</td>
                    <td className="px-6 py-4 text-sm text-zinc-500">{endpoint.desc}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </motion.div>
      </div>
    </section>
  )
}

function CTA() {
  return (
    <section className="py-32 border-t border-white/5">
      <div className="max-w-4xl mx-auto px-6 text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          <h2 className="text-4xl md:text-6xl font-bold text-white leading-tight">
            Ready to give your
            <br />
            <span className="text-zinc-500">agents memory?</span>
          </h2>
          <p className="mt-6 text-lg text-zinc-500 max-w-xl mx-auto">
            Join the beta. Start storing and recalling memories in minutes.
          </p>
          <div className="mt-10 flex flex-col sm:flex-row gap-4 justify-center">
            <a
              href="https://x.com/openclawdy"
              target="_blank"
              className="group relative px-8 py-4 text-sm font-semibold text-black bg-white rounded-full overflow-hidden transition-transform duration-300 hover:scale-105"
            >
              <span className="relative z-10 flex items-center justify-center gap-2">
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
                </svg>
                Follow for Updates
              </span>
            </a>
          </div>
        </motion.div>
      </div>
    </section>
  )
}

function Footer() {
  return (
    <footer className="py-8 border-t border-white/5">
      <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="opacity-60">
          <Logo size="small" />
        </div>
        <p className="text-sm text-zinc-600">
          Persistent memory for Agents
        </p>
        <a
          href="https://x.com/openclawdy"
          target="_blank"
          className="text-sm text-zinc-600 hover:text-white transition-colors duration-300"
        >
          @openclawdy
        </a>
      </div>
    </footer>
  )
}

export default function Home() {
  return (
    <main className="min-h-screen bg-black text-white overflow-x-hidden">
      <Navbar />
      <Hero />
      <div id="playground">
        <Playground />
      </div>
      <Problem />
      <Features />
      <Pricing />
      <API />
      <CTA />
      <Footer />
    </main>
  )
}
