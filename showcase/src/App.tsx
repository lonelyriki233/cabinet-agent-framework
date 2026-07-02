import { motion } from 'framer-motion'
import {
  Boxes,
  BrainCircuit,
  CheckCircle2,
  ChevronRight,
  CircuitBoard,
  DatabaseZap,
  FileStack,
  GitBranch,
  Hammer,
  Network,
  ShieldCheck,
  Sparkles,
  TerminalSquare,
  Workflow,
} from 'lucide-react'
import './App.css'

const modules = [
  {
    icon: <Network />,
    title: 'Project Harness Core',
    desc: '把复杂项目表示为 project / module / milestone / task / dependency / decision / risk。',
    status: '已接入 v1.0',
  },
  {
    icon: <Hammer />,
    title: 'Worker Runtime',
    desc: 'HarnessTask 生成 worker prompt，worker 提交 manifest，产物进入 registry。',
    status: '已接入 v1.0',
  },
  {
    icon: <ShieldCheck />,
    title: 'Gate System',
    desc: '阶段硬验收：没有 artifact、没有 validation、缺必需类型就不能通过。',
    status: '已接入 v1.0',
  },
  {
    icon: <FileStack />,
    title: 'Artifact Registry',
    desc: '项目不靠口头总结推进，所有 code/docs/tests/design/logs 都登记、哈希、验收。',
    status: '已接入 v1.0',
  },
  {
    icon: <BrainCircuit />,
    title: 'Context / Memory Engine',
    desc: '管理任务该读什么、禁止读什么、如何沉淀决策、失败、证据与长期记忆。',
    status: '已接入 v1.0',
  },
  {
    icon: <CircuitBoard />,
    title: 'Orchestrator / Supervisor',
    desc: '主 agent 从聊天者升级为项目监督者：拆解、分派、审查、返工、归档。',
    status: '原型已接入 intake',
  },
]

const flow = [
  '需求输入',
  'Harness Project',
  'HarnessTask',
  'Worker Runtime',
  'Artifact Registry',
  'Gate 审查',
  '返工 / 归档',
]

const commands = [
  'python3 -m cabinet_framework.cli harness-intake --request "完善 CAF worker runtime" --authority L2',
  'python3 -m cabinet_framework.cli harness-run --task-id <TASK> --mode prompt',
  'python3 -m cabinet_framework.cli harness-submit --manifest manifest.json',
  'python3 -m cabinet_framework.cli harness-gate --task-id <TASK>',
]

const metrics = [
  ['25', 'tests passing'],
  ['4', 'v1.0 milestones shipped'],
  ['6', 'core modules defined'],
  ['1', 'closed loop running'],
]

function App() {
  return (
    <main className="page">
      <section className="hero">
        <div className="noise" />
        <motion.div
          className="hero-copy"
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7 }}
        >
          <div className="eyebrow"><Sparkles size={16} /> CAF v1.0 Showcase</div>
          <h1>Agent Project Harness for complex development.</h1>
          <p>
            CAF 不是具体业务项目，而是让多个 agent / worker / skill / hook / memory / gate
            协同开发大项目的工程框架。
          </p>
          <div className="hero-actions">
            <a href="#flow" className="primary">查看运行闭环 <ChevronRight size={18} /></a>
            <a href="#modules" className="secondary">框架模块</a>
          </div>
        </motion.div>
        <motion.div
          className="terminal-card"
          initial={{ opacity: 0, scale: 0.96 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.15, duration: 0.7 }}
        >
          <div className="terminal-top"><span/><span/><span/></div>
          <code>
            <b>$ caf harness-intake</b>{'\n'}
            request → project → task → worker → artifact → gate{`\n\n`}
            <b>status:</b> v1.0 minimal loop PASS{`\n`}
            <b>tests:</b> 25 passed{`\n`}
            <b>gate:</b> caf gate PASS
          </code>
        </motion.div>
      </section>

      <section className="metrics">
        {metrics.map(([n, label]) => (
          <motion.div className="metric" key={label} whileHover={{ y: -4 }}>
            <strong>{n}</strong>
            <span>{label}</span>
          </motion.div>
        ))}
      </section>

      <section className="panel" id="flow">
        <div className="section-head">
          <Workflow />
          <div>
            <h2>v1.0 运行闭环</h2>
            <p>目标是让复杂项目靠结构化任务、真实产物和硬 gate 推进。</p>
          </div>
        </div>
        <div className="flow">
          {flow.map((item, index) => (
            <motion.div className="flow-node" key={item} initial={{ opacity: 0, y: 10 }} whileInView={{ opacity: 1, y: 0 }} transition={{ delay: index * 0.04 }}>
              <span>{String(index + 1).padStart(2, '0')}</span>
              <b>{item}</b>
            </motion.div>
          ))}
        </div>
      </section>

      <section className="panel" id="modules">
        <div className="section-head">
          <Boxes />
          <div>
            <h2>框架内容</h2>
            <p>当前版本重点不是行业，而是支撑 agent 开发大项目的底层 harness。</p>
          </div>
        </div>
        <div className="grid">
          {modules.map((m) => (
            <motion.article className="module-card" key={m.title} whileHover={{ y: -6, scale: 1.01 }}>
              <div className="module-icon">{m.icon}</div>
              <h3>{m.title}</h3>
              <p>{m.desc}</p>
              <span>{m.status}</span>
            </motion.article>
          ))}
        </div>
      </section>

      <section className="split">
        <div className="panel compact">
          <div className="section-head">
            <TerminalSquare />
            <div>
              <h2>CLI 入口</h2>
              <p>展示页对应的真实 v1.0 命令。</p>
            </div>
          </div>
          <div className="cmd-list">
            {commands.map((cmd) => <code key={cmd}>{cmd}</code>)}
          </div>
        </div>
        <div className="panel compact accent">
          <div className="section-head">
            <DatabaseZap />
            <div>
              <h2>下一步</h2>
              <p>不急着做行业应用，继续补强 CAF 本体。</p>
            </div>
          </div>
          <ul className="next">
            <li><CheckCircle2 /> Dashboard 改为 Showcase + Runtime View</li>
            <li><CheckCircle2 /> Context / Memory Engine 深化</li>
            <li><CheckCircle2 /> Gate 合并 hooks/lifecycle</li>
            <li><CheckCircle2 /> Worker manifest schema 强校验</li>
          </ul>
        </div>
      </section>

      <footer>
        <GitBranch size={16} /> CAF v1.0 · Agent Project Harness · not a vertical project
      </footer>
    </main>
  )
}

export default App
