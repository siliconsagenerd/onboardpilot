<template>
  <aside class="float-widget" aria-label="Companion project">
    <div class="float-widget__monogram" aria-hidden="true">PP</div>
    <div class="float-widget__body">
      <div class="float-widget__eyebrow">{{ t('related_project') }}</div>
      <h3 class="float-widget__title">ProzessPilot</h3>
      <a href="https://github.com/siliconsagenerd/prozesspilot" target="_blank" rel="noopener" class="float-widget__primary-link">{{ t('open_prozesspilot') }}</a>
      <div class="float-widget__extra">
        <p class="float-widget__desc">{{ t('prozesspilot_desc') }}</p>
        <div class="float-widget__chips">
          <span class="chip">FastAPI</span>
          <span class="chip">LLM</span>
          <span class="chip">RAG</span>
          <span class="chip">Human-in-the-loop</span>
        </div>
        <div class="float-widget__links">
          <a href="https://github.com/siliconsagenerd/prozesspilot" target="_blank" rel="noopener" class="float-widget__link">ProzessPilot ↗</a>
          <a href="https://github.com/siliconsagenerd/securedoc-ai" target="_blank" rel="noopener" class="float-widget__link">SecureDoc-AI ↗</a>
        </div>
      </div>
      <div class="float-widget__hint">{{ t('hover_expand') }}</div>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
const { t } = useI18n()
</script>

<style scoped>
.float-widget {
  position: fixed;
  bottom: 1.5rem;
  right: 1.5rem;
  z-index: 40;
  width: 320px;
  max-width: calc(100vw - 3rem);
  background: var(--color-surface);
  color: var(--color-ink);
  border: 2px solid var(--color-accent);
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.18);
  padding: 1.1rem 1.25rem;
  display: flex;
  gap: 0.9rem;
  align-items: flex-start;
  overflow: hidden;
  cursor: default;
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
  border-radius: var(--radius-md);
}
.float-widget:hover {
  transform: translateY(-4px);
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.28);
}
.float-widget::before {
  content: "";
  position: absolute;
  top: -40%;
  right: -30%;
  width: 160px;
  height: 160px;
  border-radius: 50%;
  background: radial-gradient(circle, var(--color-accent-soft) 0%, transparent 70%);
  pointer-events: none;
}
.float-widget__monogram {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  font-weight: 700;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-accent);
  color: #0f172a;
  flex-shrink: 0;
  letter-spacing: 0.02em;
  border-radius: var(--radius-xs);
}
.float-widget__body { min-width: 0; flex: 1; }
.float-widget__eyebrow {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--color-accent);
  margin-bottom: 0.25rem;
  font-weight: 600;
}
.float-widget__title {
  font-size: 1.1rem;
  font-weight: 800;
  letter-spacing: -0.01em;
  color: var(--color-ink);
  margin: 0 0 0.35rem;
  line-height: 1.1;
}
.float-widget__primary-link {
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--color-accent);
  text-decoration: none;
}
.float-widget__primary-link:hover { text-decoration: underline; }
.float-widget__extra {
  max-height: 0;
  opacity: 0;
  overflow: hidden;
  transition: max-height 0.25s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.2s;
  font-size: 0.82rem;
}
.float-widget:hover .float-widget__extra {
  max-height: 400px;
  opacity: 1;
}
.float-widget__desc {
  line-height: 1.5;
  color: var(--color-ink-soft);
  margin-bottom: 0.6rem;
}
.float-widget__chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  margin-bottom: 0.6rem;
}
.float-widget__chips .chip {
  font-family: var(--font-mono);
  font-size: 0.7rem;
  padding: 2px 6px;
  background: var(--color-canvas-subtle);
  color: var(--color-ink);
  border: 1px solid var(--color-line);
  border-radius: var(--radius-xs);
}
.float-widget__links {
  display: flex;
  gap: 0.75rem;
  font-size: 0.78rem;
  font-weight: 600;
}
.float-widget__link {
  color: var(--color-accent);
  text-decoration: none;
}
.float-widget__link:hover { text-decoration: underline; }
.float-widget__hint {
  font-family: var(--font-mono);
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--color-muted);
  opacity: 1;
  margin-top: 0.4rem;
  transition: opacity 0.2s;
}
.float-widget:hover .float-widget__hint { opacity: 0; }
</style>
