// Which coding agent is running the skill. The map records it in graph.meta.agent so its UI and
// "Fix with …" / "Build this with …" prompts name the right agent (or use universal "your agent" copy
// when unknown), and serve.mjs prefers a matching CLI engine when one is installed.
// --agent <name> (or FLOORPLAN_AGENT) overrides auto-detection.
const DETECT = {
  claude: (env) => !!(env.CLAUDECODE || env.CLAUDE_CODE_ENTRYPOINT || env.CLAUDE_CODE_SESSION || env.CLAUDE_SKILL_DIR),
  codex: (env) => !!(env.CODEX_THREAD_ID || env.CODEX_SESSION_ID || env.CODEX_SANDBOX || env.CODEX_CI),
  gemini: (env) => !!(env.GEMINI_CLI || env.GEMINI_SESSION_ID),
  antigravity: (env) => !!(env.ANTIGRAVITY_CLI_ALIAS || env.ANTIGRAVITY_AGENT || env.AGY_ACCOUNT),
  cursor: (env) => !!(env.CURSOR_TRACE_ID || env.CURSOR_SESSION_ID || /cursor/i.test(env.TERM_PROGRAM || '')),
  windsurf: (env) => !!(env.WINDSURF_SESSION || /windsurf|codeium/i.test(env.TERM_PROGRAM || '')),
  opencode: (env) => !!(env.OPENCODE || env.OPENCODE_SESSION),
  aider: (env) => !!(env.AIDER_MODEL || env.AIDER_CHAT_HISTORY_FILE),
};
export const AGENTS = Object.keys(DETECT);

export function detectAgent(args = {}, env = process.env) {
  const v = String(args.agent || env.FLOORPLAN_AGENT || '').trim().toLowerCase();
  if (v && /^[a-z0-9_.\-]+$/.test(v)) return v;
  return AGENTS.find((a) => DETECT[a](env)) || 'agent';
}
