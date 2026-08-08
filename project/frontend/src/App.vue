<script setup lang="ts">
import { nextTick, onMounted, ref } from 'vue'
import Toast from 'primevue/toast'

import FileUploader from '@/components/FileUploader.vue'
import ResultsDashboard from '@/components/ResultsDashboard.vue'
import {
  getHealth,
  getReport,
  type AnalysisReport,
  type HealthResponse
} from '@/services/fileService'

const report = ref<AnalysisReport | null>(null)
const health = ref<HealthResponse | null>(null)
const apiOnline = ref(false)

onMounted(async () => {
  try {
    health.value = await getHealth()
    apiOnline.value = true
  } catch {
    apiOnline.value = false
  }

  const reportId = new URLSearchParams(window.location.search).get('report')
  if (reportId && /^[0-9a-f-]{36}$/i.test(reportId)) {
    try {
      report.value = await getReport(reportId)
    } catch {
      // The main upload flow remains available when a shared report is missing.
    }
  }
})

const handleReport = async (newReport: AnalysisReport): Promise<void> => {
  report.value = newReport
  await nextTick()
  document.querySelector('#results')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}
</script>

<template>
  <div class="app-shell">
    <Toast position="top-right" />

    <header class="site-header">
      <a class="brand" href="#top" aria-label="Niro AI home">
        <span class="brand-mark">N</span>
        <span><strong>Niro</strong> AI</span>
      </a>
      <nav aria-label="Primary navigation">
        <a href="#upload">Analyse</a>
        <a href="#methodology">Methodology</a>
        <a href="#about">About</a>
      </nav>
      <div class="api-status" :class="{ online: apiOnline }">
        <i />
        {{ apiOnline ? 'API online' : 'API offline' }}
      </div>
    </header>

    <main id="top">
      <section class="hero">
        <div class="hero-copy">
          <div class="research-label"><i class="pi pi-shield" /> Defensive security research prototype</div>
          <h1>See the risk hiding in your <em>dependencies.</em></h1>
          <p class="hero-lead">
            Turn Node.js manifests into structured vulnerability evidence for faster, more responsible security triage.
          </p>
          <div class="hero-actions">
            <a class="primary-action" href="#upload">Analyse a manifest <i class="pi pi-arrow-down" /></a>
            <a class="text-action" href="#methodology">How it works <i class="pi pi-arrow-right" /></a>
          </div>
          <div class="trust-row">
            <span><i class="pi pi-check-circle" /> Public CVE evidence</span>
            <span><i class="pi pi-check-circle" /> Conservative scoring</span>
            <span><i class="pi pi-check-circle" /> Analyst-first output</span>
          </div>
        </div>

        <aside class="signal-card" aria-label="System evidence status">
          <div class="signal-topline">
            <span>Evidence engine</span>
            <i class="pi pi-wave-pulse" />
          </div>
          <div class="signal-visual">
            <span class="orbit orbit-one" />
            <span class="orbit orbit-two" />
            <div class="signal-core"><strong>CTI</strong><small>retrieval</small></div>
            <i class="node n1" /><i class="node n2" /><i class="node n3" /><i class="node n4" />
          </div>
          <div class="signal-metrics">
            <div><span>Indexed records</span><strong>{{ health?.dataset.records_indexed ?? '—' }}</strong></div>
            <div><span>Analysis mode</span><strong>{{ health?.qwen_configured ? 'Qwen + baseline' : 'Local baseline' }}</strong></div>
          </div>
          <p><i class="pi pi-info-circle" /> No result is presented as a confirmed zero-day prediction.</p>
        </aside>
      </section>

      <section class="workspace">
        <FileUploader @analyzed="handleReport" />
        <ResultsDashboard v-if="report" :report="report" />
      </section>

      <section id="methodology" class="methodology">
        <div class="method-copy">
          <span class="eyebrow">Transparent by design</span>
          <h2>From manifest to evidence in four clear stages.</h2>
          <p>Niro separates fact retrieval from risk estimation so analysts can see where every conclusion begins.</p>
        </div>
        <ol class="method-steps">
          <li><span>01</span><div><strong>Parse</strong><p>Extract package names and installed version ranges.</p></div></li>
          <li><span>02</span><div><strong>Retrieve</strong><p>Match package names against prepared public CVE evidence.</p></div></li>
          <li><span>03</span><div><strong>Score</strong><p>Apply conservative severity and confidence rules.</p></div></li>
          <li><span>04</span><div><strong>Review</strong><p>Export structured findings for human validation.</p></div></li>
        </ol>
      </section>
    </main>

    <footer id="about">
      <div class="brand footer-brand"><span class="brand-mark">N</span><span><strong>Niro</strong> AI</span></div>
      <p>MSc Cyber Security research prototype · University of the West of Scotland</p>
      <p>Defensive use only. Not a commercial scanner or confirmed zero-day predictor.</p>
    </footer>
  </div>
</template>
