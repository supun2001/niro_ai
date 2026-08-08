<script setup lang="ts">
import { computed, ref } from 'vue'
import axios from 'axios'

import Button from 'primevue/button'
import { useToast } from 'primevue/usetoast'

import { analyzeFile, type AnalysisReport } from '@/services/fileService'

const emit = defineEmits<{
  analyzed: [report: AnalysisReport]
}>()

const toast = useToast()
const fileInput = ref<HTMLInputElement | null>(null)
const selectedFile = ref<File | null>(null)
const analyzing = ref(false)
const uploadProgress = ref(0)
const isDragging = ref(false)

const supportedNames = new Set([
  'package.json',
  'package-lock.json',
  'npm-shrinkwrap.json',
  'yarn.lock',
  'pnpm-lock.yaml',
  'pnpm-lock.yml'
])

const formattedSize = computed(() => {
  if (!selectedFile.value) return ''
  const bytes = selectedFile.value.size
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
})

const openPicker = (): void => fileInput.value?.click()

const handleInput = (event: Event): void => {
  const input = event.target as HTMLInputElement
  selectFile(input.files?.[0] ?? null)
}

const handleDrop = (event: DragEvent): void => {
  isDragging.value = false
  selectFile(event.dataTransfer?.files[0] ?? null)
}

const selectFile = (file: File | null): void => {
  if (!file) return
  const normalizedName = file.name.toLowerCase()

  if (!supportedNames.has(normalizedName)) {
    toast.add({
      severity: 'warn',
      summary: 'Unsupported manifest',
      detail: 'Choose package.json or an npm, Yarn or pnpm lock file.',
      life: 4000
    })
    return
  }

  if (file.size > 5 * 1024 * 1024) {
    toast.add({
      severity: 'warn',
      summary: 'File is too large',
      detail: 'Dependency manifests must be 5 MB or smaller.',
      life: 4000
    })
    return
  }

  selectedFile.value = file
  uploadProgress.value = 0
}

const clearFile = (): void => {
  selectedFile.value = null
  uploadProgress.value = 0
  if (fileInput.value) fileInput.value.value = ''
}

const startAnalysis = async (): Promise<void> => {
  if (!selectedFile.value) {
    toast.add({
      severity: 'warn',
      summary: 'Choose a manifest',
      detail: 'Select a dependency file before starting the analysis.',
      life: 3000
    })
    return
  }

  try {
    analyzing.value = true
    uploadProgress.value = 0
    const report = await analyzeFile(selectedFile.value, (percentage) => {
      uploadProgress.value = percentage
    })
    emit('analyzed', report)
    toast.add({
      severity: 'success',
      summary: 'Analysis complete',
      detail: `${report.summary.dependency_count} dependencies were reviewed.`,
      life: 3500
    })
  } catch (error: unknown) {
    let message = 'The manifest could not be analysed.'
    if (axios.isAxiosError(error)) {
      message = error.response?.data?.message ?? error.message
    }
    toast.add({
      severity: 'error',
      summary: 'Analysis failed',
      detail: message,
      life: 5000
    })
  } finally {
    analyzing.value = false
  }
}
</script>

<template>
  <section id="upload" class="upload-card" aria-labelledby="upload-title">
    <div class="section-kicker">
      <span>01</span>
      Dependency intake
    </div>
    <div class="upload-heading">
      <div>
        <h2 id="upload-title">Analyse your dependency manifest</h2>
        <p>Upload one manifest. Files are validated before any evidence is retrieved.</p>
      </div>
      <span class="private-badge"><i class="pi pi-lock" /> Local prototype</span>
    </div>

    <input
      ref="fileInput"
      class="visually-hidden"
      type="file"
      accept=".json,.lock,.yaml,.yml"
      @change="handleInput"
    >

    <div
      class="drop-zone"
      :class="{ 'is-dragging': isDragging, 'has-file': selectedFile }"
      role="button"
      tabindex="0"
      @click="openPicker"
      @keydown.enter="openPicker"
      @keydown.space.prevent="openPicker"
      @dragenter.prevent="isDragging = true"
      @dragover.prevent="isDragging = true"
      @dragleave.prevent="isDragging = false"
      @drop.prevent="handleDrop"
    >
      <template v-if="!selectedFile">
        <div class="upload-glyph"><i class="pi pi-arrow-up" /></div>
        <h3>Drop your manifest here</h3>
        <p>or <span>browse from your computer</span></p>
        <div class="file-formats">
          <code>package.json</code>
          <code>package-lock.json</code>
          <code>yarn.lock</code>
          <code>pnpm-lock.yaml</code>
        </div>
        <small>Maximum file size: 5 MB</small>
      </template>

      <template v-else>
        <div class="selected-icon"><i class="pi pi-file" /></div>
        <div class="selected-copy">
          <strong>{{ selectedFile.name }}</strong>
          <span>{{ formattedSize }} · Ready to analyse</span>
        </div>
        <button
          type="button"
          class="remove-file"
          aria-label="Remove selected file"
          :disabled="analyzing"
          @click.stop="clearFile"
        >
          <i class="pi pi-times" />
        </button>
      </template>
    </div>

    <div v-if="analyzing" class="analysis-progress" aria-live="polite">
      <div class="progress-copy">
        <span>{{ uploadProgress < 100 ? 'Uploading manifest' : 'Retrieving CVE evidence' }}</span>
        <span>{{ uploadProgress < 100 ? `${uploadProgress}%` : 'Analysing…' }}</span>
      </div>
      <div class="progress-track">
        <span :class="{ processing: uploadProgress >= 100 }" :style="{ width: `${uploadProgress}%` }" />
      </div>
    </div>

    <div class="upload-actions">
      <p><i class="pi pi-shield" /> Defensive analysis only. Human review remains required.</p>
      <Button
        label="Run risk analysis"
        icon="pi pi-sparkles"
        icon-pos="right"
        :disabled="!selectedFile"
        :loading="analyzing"
        @click="startAnalysis"
      />
    </div>
  </section>
</template>

<style scoped>
.upload-card {
  position: relative;
  overflow: hidden;
  padding: clamp(1.5rem, 4vw, 2.75rem);
  border: 1px solid var(--line);
  border-radius: 24px;
  background: var(--surface);
  box-shadow: var(--shadow-lg);
}

.upload-card::before {
  content: '';
  position: absolute;
  inset: 0 0 auto;
  height: 3px;
  background: linear-gradient(90deg, var(--accent), #ffb25b 45%, transparent 80%);
}

.section-kicker {
  display: flex;
  align-items: center;
  gap: .65rem;
  margin-bottom: 1rem;
  color: var(--accent-dark);
  font-size: .74rem;
  font-weight: 800;
  letter-spacing: .13em;
  text-transform: uppercase;
}

.section-kicker span {
  display: grid;
  width: 28px;
  height: 28px;
  place-items: center;
  border-radius: 50%;
  color: #fff;
  background: var(--ink);
  font-size: .68rem;
}

.upload-heading {
  display: flex;
  justify-content: space-between;
  gap: 1.5rem;
  align-items: flex-start;
  margin-bottom: 1.75rem;
}

.upload-heading h2 { margin: 0 0 .5rem; font-size: clamp(1.55rem, 3vw, 2.15rem); }
.upload-heading p { margin: 0; color: var(--muted); }

.private-badge {
  flex: 0 0 auto;
  display: inline-flex;
  align-items: center;
  gap: .45rem;
  padding: .55rem .75rem;
  border: 1px solid #dbe8e2;
  border-radius: 999px;
  color: #24644d;
  background: #eff9f4;
  font-size: .76rem;
  font-weight: 700;
}

.drop-zone {
  min-height: 290px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: .7rem;
  padding: 2rem;
  border: 1.5px dashed #c8ccc8;
  border-radius: 18px;
  cursor: pointer;
  background: #fafaf7;
  text-align: center;
  transition: .2s ease;
}

.drop-zone:hover,
.drop-zone.is-dragging { border-color: var(--accent); background: var(--accent-soft); transform: translateY(-2px); }
.drop-zone.has-file { min-height: 150px; flex-direction: row; justify-content: flex-start; text-align: left; }

.upload-glyph,
.selected-icon {
  display: grid;
  place-items: center;
  border-radius: 16px;
  color: var(--accent-dark);
  background: var(--accent-soft);
}

.upload-glyph { width: 62px; height: 62px; margin-bottom: .3rem; font-size: 1.4rem; }
.selected-icon { width: 52px; height: 52px; flex: 0 0 auto; font-size: 1.25rem; }
.drop-zone h3 { margin: .3rem 0 0; font-size: 1.1rem; }
.drop-zone p { margin: 0; color: var(--muted); }
.drop-zone p span { color: var(--accent-dark); font-weight: 700; }
.drop-zone small { margin-top: .35rem; color: var(--muted); }

.file-formats { display: flex; flex-wrap: wrap; justify-content: center; gap: .45rem; margin: .55rem 0 .25rem; }
.file-formats code { padding: .36rem .55rem; border: 1px solid var(--line); border-radius: 7px; color: var(--ink-soft); background: #fff; font-size: .7rem; }
.selected-copy { display: flex; flex: 1; flex-direction: column; gap: .35rem; }
.selected-copy strong { color: var(--ink); }
.selected-copy span { color: var(--muted); font-size: .85rem; }

.remove-file {
  display: grid;
  width: 36px;
  height: 36px;
  place-items: center;
  border: 0;
  border-radius: 50%;
  cursor: pointer;
  color: var(--muted);
  background: #eceeea;
}

.analysis-progress { margin-top: 1.2rem; }
.progress-copy { display: flex; justify-content: space-between; margin-bottom: .5rem; color: var(--muted); font-size: .78rem; font-weight: 700; }
.progress-track { height: 7px; overflow: hidden; border-radius: 999px; background: #e7e8e4; }
.progress-track span { display: block; height: 100%; border-radius: inherit; background: var(--accent); transition: width .2s; }
.progress-track span.processing { width: 45% !important; animation: processing 1.1s ease-in-out infinite alternate; }

.upload-actions { display: flex; align-items: center; justify-content: space-between; gap: 1.5rem; margin-top: 1.4rem; }
.upload-actions p { display: flex; align-items: center; gap: .5rem; margin: 0; color: var(--muted); font-size: .78rem; }
.upload-actions :deep(.p-button) { padding: .85rem 1.2rem; border: 0; border-radius: 10px; background: var(--ink); }
.upload-actions :deep(.p-button:not(:disabled):hover) { background: var(--accent-dark); }

@keyframes processing { from { transform: translateX(0); } to { transform: translateX(120%); } }

@media (max-width: 640px) {
  .upload-heading, .upload-actions { align-items: stretch; flex-direction: column; }
  .private-badge { align-self: flex-start; }
  .drop-zone { min-height: 260px; padding: 1.25rem; }
  .upload-actions :deep(.p-button) { justify-content: center; }
}
</style>
