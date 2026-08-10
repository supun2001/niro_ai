<script setup lang="ts">
import { computed, ref } from 'vue'
import Button from 'primevue/button'

import type { AnalysisReport, DependencyAssessment, RiskLevel } from '@/services/fileService'

const props = defineProps<{ report: AnalysisReport }>()

const query = ref('')
const riskFilter = ref<'All' | RiskLevel>('All')
const visibleLimit = ref(50)

const filteredAssessments = computed(() => {
  const needle = query.value.trim().toLowerCase()
  return props.report.assessments.filter((assessment) => {
    const matchesQuery = !needle || assessment.package.toLowerCase().includes(needle)
    const matchesRisk = riskFilter.value === 'All' || assessment.risk_level === riskFilter.value
    return matchesQuery && matchesRisk
  })
})

const visibleAssessments = computed(() => filteredAssessments.value.slice(0, visibleLimit.value))

const riskOptions: Array<'All' | RiskLevel> = ['All', 'High', 'Medium', 'Low', 'Unknown']

const suggestionsByPriority = computed(() => {
  const suggestions = props.report.suggestions || []
  return {
    critical: suggestions.filter(s => s.priority === 'critical'),
    high: suggestions.filter(s => s.priority === 'high'),
    medium: suggestions.filter(s => s.priority === 'medium'),
    low: suggestions.filter(s => s.priority === 'low')
  }
})

const percentage = (count: number): number => {
  if (!props.report.summary.dependency_count) return 0
  return Math.max(2, Math.round((count / props.report.summary.dependency_count) * 100))
}

const confidencePercent = computed(() => Math.round(props.report.summary.confidence * 100))

const riskClass = (level: string): string => `risk-${level.toLowerCase()}`

const priorityIcon = (priority: string): string => {
  const icons: Record<string, string> = {
    critical: 'pi-exclamation-circle',
    high: 'pi-alert-circle',
    medium: 'pi-info-circle',
    low: 'pi-check-circle'
  }
  return icons[priority] || 'pi-info-circle'
}

const priorityColor = (priority: string): string => {
  const colors: Record<string, string> = {
    critical: '#c84832',
    high: '#c17b18',
    medium: '#0066cc',
    low: '#2b7a5d'
  }
  return colors[priority] || '#666'
}

const formatDate = (value: string): string => new Intl.DateTimeFormat('en-GB', {
  dateStyle: 'medium',
  timeStyle: 'short'
}).format(new Date(value))

const downloadReport = (): void => {
  const data = JSON.stringify(props.report, null, 2)
  const url = URL.createObjectURL(new Blob([data], { type: 'application/json' }))
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = `niro-report-${props.report.report_id}.json`
  anchor.click()
  URL.revokeObjectURL(url)
}

const showMore = (): void => {
  visibleLimit.value += 50
}

const vulnerabilityLabel = (assessment: DependencyAssessment): string => {
  const count = assessment.known_vulnerabilities.length
  return count === 1 ? '1 match' : `${count} matches`
}
</script>

<template>
  <section id="results" class="results" aria-labelledby="results-title">
    <div class="results-header">
      <div>
        <div class="section-kicker"><span>02</span> Evidence report</div>
        <h2 id="results-title">Dependency risk overview</h2>
        <p>{{ report.source_file }} · {{ formatDate(report.generated_at) }}</p>
      </div>
      <div class="report-actions">
        <span class="report-id">ID {{ report.report_id.slice(0, 8) }}</span>
        <Button label="Export JSON" icon="pi pi-download" severity="secondary" outlined @click="downloadReport" />
      </div>
    </div>

    <div class="summary-grid">
      <article class="summary-card primary-card">
        <span>Overall exposure</span>
        <strong :class="riskClass(report.summary.overall_risk_level)">
          {{ report.summary.overall_risk_level }}
        </strong>
        <p>Evidence-based triage level</p>
      </article>
      <article class="summary-card">
        <span>Dependencies</span>
        <strong>{{ report.summary.dependency_count }}</strong>
        <p>{{ report.summary.dependencies_with_matches }} with local CVE matches</p>
      </article>
      <article class="summary-card">
        <span>Vulnerability evidence</span>
        <strong>{{ report.summary.known_vulnerability_count }}</strong>
        <p>Exact package-name matches</p>
      </article>
      <article class="summary-card">
        <span>Evidence confidence</span>
        <strong>{{ confidencePercent }}%</strong>
        <p>{{ report.coverage.records_indexed }} indexed CVE records</p>
      </article>
    </div>

    <div class="insight-grid">
      <article class="panel distribution-panel">
        <div class="panel-heading">
          <div>
            <span class="eyebrow">Risk distribution</span>
            <h3>Dependency signals</h3>
          </div>
          <span class="mode-badge">{{ report.analysis_mode.replaceAll('-', ' ') }}</span>
        </div>

        <div class="distribution-list">
          <div v-for="level in (['High', 'Medium', 'Low', 'Unknown'] as RiskLevel[])" :key="level" class="distribution-row">
            <span>{{ level }}</span>
            <div class="distribution-track">
              <i :class="riskClass(level)" :style="{ width: `${percentage(report.summary.risk_distribution[level])}%` }" />
            </div>
            <strong>{{ report.summary.risk_distribution[level] }}</strong>
          </div>
        </div>
      </article>

      <article class="panel review-panel">
        <div class="review-icon"><i class="pi pi-eye" /></div>
        <span class="eyebrow">Analyst checkpoint</span>
        <h3>Human review is required</h3>
        <p>This report supports early triage. It does not confirm a future or active zero-day vulnerability.</p>
        <div class="coverage-line">
          <span>Dataset status</span>
          <strong :class="{ available: report.coverage.dataset_available }">
            {{ report.coverage.dataset_available ? 'Available' : 'Unavailable' }}
          </strong>
        </div>
      </article>
    </div>

    <div v-if="Object.values(suggestionsByPriority).some(arr => arr.length)" class="suggestions-panel">
      <div class="suggestions-header">
        <span class="eyebrow">Action items</span>
        <h3>Recommended remediation steps</h3>
      </div>
      <div class="suggestions-list">
        <div
          v-for="suggestion in [...suggestionsByPriority.critical, ...suggestionsByPriority.high, ...suggestionsByPriority.medium, ...suggestionsByPriority.low]"
          :key="suggestion.title"
          class="suggestion-card"
          :style="{ borderLeftColor: priorityColor(suggestion.priority) }"
        >
          <div class="suggestion-header">
            <div class="suggestion-icon" :style="{ color: priorityColor(suggestion.priority) }">
              <i :class="`pi ${priorityIcon(suggestion.priority)}`" />
            </div>
            <div>
              <strong>{{ suggestion.title }}</strong>
              <span class="priority-badge" :style="{ color: priorityColor(suggestion.priority) }">{{ suggestion.priority }}</span>
            </div>
          </div>
          <p>{{ suggestion.description }}</p>
          <div v-if="suggestion.packages" class="suggestion-packages">
            <span class="packages-label">Affected:</span>
            <div class="package-tags">
              <code v-for="pkg in suggestion.packages" :key="pkg">{{ pkg }}</code>
            </div>
          </div>
          <div class="suggestion-action">
            <i class="pi pi-arrow-right" />
            <span>{{ suggestion.action }}</span>
          </div>
        </div>
      </div>
    </div>

    <article class="panel dependency-panel">
      <div class="table-toolbar">
        <div>
          <span class="eyebrow">Package evidence</span>
          <h3>Dependency assessment</h3>
        </div>
        <div class="filters">
          <label class="search-field">
            <i class="pi pi-search" />
            <input v-model="query" type="search" placeholder="Search package" aria-label="Search packages">
          </label>
          <div class="risk-filters" aria-label="Filter by risk">
            <button
              v-for="option in riskOptions"
              :key="option"
              type="button"
              :class="{ active: riskFilter === option }"
              @click="riskFilter = option"
            >
              {{ option }}
            </button>
          </div>
        </div>
      </div>

      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Package</th>
              <th>Installed</th>
              <th>Risk</th>
              <th>CVE evidence</th>
              <th>Confidence</th>
            </tr>
          </thead>
          <tbody>
            <template v-for="assessment in visibleAssessments" :key="`${assessment.package}-${assessment.installed_version}`">
              <tr>
                <td>
                  <strong>{{ assessment.package }}</strong>
                  <small>{{ assessment.dependency_group }}</small>
                </td>
                <td><code>{{ assessment.installed_version }}</code></td>
                <td><span class="risk-pill" :class="riskClass(assessment.risk_level)">{{ assessment.risk_level }}</span></td>
                <td>
                  <details v-if="assessment.known_vulnerabilities.length" class="evidence-details">
                    <summary>{{ vulnerabilityLabel(assessment) }}</summary>
                    <div class="evidence-list">
                      <article v-for="evidence in assessment.known_vulnerabilities" :key="evidence.cve_id">
                        <div>
                          <strong>{{ evidence.cve_id }}</strong>
                          <span>{{ evidence.severity }}<template v-if="evidence.cvss_score"> · CVSS {{ evidence.cvss_score }}</template></span>
                        </div>
                        <p>{{ evidence.summary }}</p>
                        <a v-if="evidence.references[0]" :href="evidence.references[0]" target="_blank" rel="noopener">View source <i class="pi pi-external-link" /></a>
                      </article>
                    </div>
                  </details>
                  <span v-else class="no-match">No local match</span>
                </td>
                <td>{{ Math.round(assessment.confidence * 100) }}%</td>
              </tr>
            </template>
            <tr v-if="!visibleAssessments.length">
              <td colspan="5" class="empty-row">No packages match the selected filters.</td>
            </tr>
          </tbody>
        </table>
      </div>

      <button
        v-if="visibleAssessments.length < filteredAssessments.length"
        type="button"
        class="show-more"
        @click="showMore"
      >
        Show 50 more dependencies
      </button>
    </article>

    <div class="limitations">
      <i class="pi pi-info-circle" />
      <div>
        <strong>Interpret with care</strong>
        <ul>
          <li v-for="note in report.limitations" :key="note">{{ note }}</li>
        </ul>
      </div>
    </div>
  </section>
</template>

<style scoped>
.results { padding-top: 5rem; scroll-margin-top: 2rem; }
.results-header { display: flex; align-items: flex-end; justify-content: space-between; gap: 2rem; margin-bottom: 1.8rem; }
.section-kicker { display: flex; align-items: center; gap: .65rem; margin-bottom: .8rem; color: var(--accent-dark); font-size: .74rem; font-weight: 800; letter-spacing: .13em; text-transform: uppercase; }
.section-kicker span { display: grid; width: 28px; height: 28px; place-items: center; border-radius: 50%; color: #fff; background: var(--ink); font-size: .68rem; }
.results-header h2 { margin: 0 0 .35rem; font-size: clamp(1.75rem, 4vw, 2.6rem); }
.results-header p { margin: 0; color: var(--muted); }
.report-actions { display: flex; align-items: center; gap: .8rem; }
.report-actions :deep(.p-button) { border-color: var(--line); color: var(--ink); }
.report-id, .mode-badge { padding: .5rem .7rem; border-radius: 7px; color: var(--muted); background: #eceee9; font-family: ui-monospace, monospace; font-size: .7rem; text-transform: uppercase; }

.summary-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; }
.summary-card { padding: 1.4rem; border: 1px solid var(--line); border-radius: 16px; background: var(--surface); }
.summary-card > span { color: var(--muted); font-size: .72rem; font-weight: 700; letter-spacing: .07em; text-transform: uppercase; }
.summary-card strong { display: block; margin: .75rem 0 .3rem; color: var(--ink); font-family: var(--display-font); font-size: 2.15rem; line-height: 1; }
.summary-card p { margin: 0; color: var(--muted); font-size: .75rem; }
.primary-card { color: #fff; border-color: var(--ink); background: var(--ink); }
.primary-card > span, .primary-card p { color: #aeb8b3; }
.primary-card strong { color: #fff; }

.risk-high { color: #c84832 !important; }
.risk-medium { color: #c17b18 !important; }
.risk-low { color: #2b7a5d !important; }
.risk-unknown { color: #748079 !important; }

.insight-grid { display: grid; grid-template-columns: 1.5fr .8fr; gap: 1rem; margin-top: 1rem; }
.panel { padding: 1.6rem; border: 1px solid var(--line); border-radius: 18px; background: var(--surface); }
.panel-heading, .table-toolbar { display: flex; align-items: flex-start; justify-content: space-between; gap: 1.5rem; }
.eyebrow { color: var(--accent-dark); font-size: .68rem; font-weight: 800; letter-spacing: .11em; text-transform: uppercase; }
.panel h3, .table-toolbar h3 { margin: .35rem 0 0; font-size: 1.18rem; }
.distribution-list { display: grid; gap: 1rem; margin-top: 1.6rem; }
.distribution-row { display: grid; grid-template-columns: 65px 1fr 32px; align-items: center; gap: .8rem; font-size: .78rem; }
.distribution-row > span { color: var(--muted); }
.distribution-row > strong { text-align: right; }
.distribution-track { height: 8px; overflow: hidden; border-radius: 99px; background: #eceeea; }
.distribution-track i { display: block; height: 100%; border-radius: inherit; background: currentColor; }

.review-panel { background: #f6f1e9; }
.review-icon { display: grid; width: 42px; height: 42px; margin-bottom: 1.2rem; place-items: center; border-radius: 12px; color: var(--accent-dark); background: var(--accent-soft); }
.review-panel p { color: var(--muted); font-size: .84rem; line-height: 1.6; }
.coverage-line { display: flex; justify-content: space-between; margin-top: 1.2rem; padding-top: 1rem; border-top: 1px solid #ddd8ce; color: var(--muted); font-size: .76rem; }
.coverage-line strong { color: #a64b3b; }
.coverage-line strong.available { color: #2b7a5d; }

.suggestions-panel { margin-top: 1rem; padding: 1.6rem; border: 1px solid var(--line); border-radius: 18px; background: var(--surface); }
.suggestions-header { margin-bottom: 1.4rem; }
.suggestions-header span { color: var(--accent-dark); font-size: .68rem; font-weight: 800; letter-spacing: .11em; text-transform: uppercase; }
.suggestions-header h3 { margin: .35rem 0 0; font-size: 1.18rem; }
.suggestions-list { display: grid; gap: 1rem; }
.suggestion-card { padding: 1.2rem; border-left: 4px solid #c84832; border-radius: 10px; background: #fafaf8; }
.suggestion-header { display: flex; align-items: flex-start; gap: .8rem; margin-bottom: .8rem; }
.suggestion-icon { display: grid; width: 32px; height: 32px; place-items: center; border-radius: 8px; flex: 0 0 auto; opacity: 0.2; font-size: 1rem; }
.suggestion-header strong { display: block; margin-bottom: .2rem; }
.priority-badge { display: inline-block; padding: .2rem .5rem; border-radius: 4px; font-size: .65rem; font-weight: 700; text-transform: uppercase; opacity: 0.7; }
.suggestion-card p { margin: 0 0 1rem; color: var(--muted); line-height: 1.5; font-size: .85rem; }
.suggestion-packages { display: flex; flex-wrap: wrap; gap: .5rem; align-items: center; margin-bottom: .8rem; }
.packages-label { color: var(--muted); font-size: .75rem; font-weight: 600; }
.package-tags { display: flex; flex-wrap: wrap; gap: .4rem; }
.package-tags code { padding: .25rem .5rem; border-radius: 4px; background: #eceeea; font-size: .7rem; color: var(--ink-soft); }
.suggestion-action { display: flex; align-items: center; gap: .5rem; color: var(--accent-dark); font-size: .78rem; font-weight: 600; }
.suggestion-action i { font-size: .65rem; }

.dependency-panel { margin-top: 1rem; padding: 0; overflow: hidden; }
.table-toolbar { padding: 1.5rem; border-bottom: 1px solid var(--line); }
.filters { display: flex; align-items: center; gap: .8rem; }
.search-field { display: flex; align-items: center; gap: .5rem; padding: .55rem .75rem; border: 1px solid var(--line); border-radius: 9px; color: var(--muted); background: #fafaf8; }
.search-field input { width: 130px; border: 0; outline: 0; color: var(--ink); background: transparent; }
.risk-filters { display: flex; padding: 3px; border-radius: 9px; background: #edeeda; }
.risk-filters button { padding: .45rem .65rem; border: 0; border-radius: 7px; cursor: pointer; color: var(--muted); background: transparent; font-size: .72rem; }
.risk-filters button.active { color: var(--ink); background: #fff; box-shadow: 0 1px 4px #18322818; }

.table-wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; text-align: left; }
th { padding: .8rem 1rem; color: var(--muted); background: #f7f7f3; font-size: .67rem; letter-spacing: .06em; text-transform: uppercase; }
td { padding: 1rem; border-top: 1px solid var(--line); color: var(--ink-soft); font-size: .8rem; vertical-align: top; }
td:first-child strong, td:first-child small { display: block; }
td:first-child small { margin-top: .2rem; color: var(--muted); text-transform: capitalize; }
td code { padding: .25rem .4rem; border-radius: 5px; background: #f0f1ed; font-size: .72rem; }
.risk-pill { display: inline-flex; padding: .35rem .55rem; border-radius: 999px; background: currentColor; font-size: .68rem; font-weight: 800; }
.risk-pill::first-line { color: currentColor; }
.risk-pill.risk-high { background: #fff0ed; }
.risk-pill.risk-medium { background: #fff5df; }
.risk-pill.risk-low { background: #eaf7f1; }
.risk-pill.risk-unknown { background: #eef0ee; }
.no-match { color: var(--muted); }
.evidence-details summary { cursor: pointer; color: var(--accent-dark); font-weight: 700; }
.evidence-list { width: min(440px, 70vw); display: grid; gap: .65rem; margin-top: .75rem; }
.evidence-list article { padding: .8rem; border-left: 3px solid var(--accent); border-radius: 6px; background: #f7f7f3; }
.evidence-list article > div { display: flex; justify-content: space-between; gap: 1rem; }
.evidence-list article span { color: var(--muted); font-size: .7rem; }
.evidence-list article p { margin: .55rem 0; color: var(--muted); line-height: 1.5; }
.evidence-list article a { color: var(--accent-dark); font-size: .72rem; font-weight: 700; }
.empty-row { padding: 2.5rem; text-align: center; color: var(--muted); }
.show-more { display: block; margin: 0 auto 1.2rem; padding: .6rem 1rem; border: 1px solid var(--line); border-radius: 8px; cursor: pointer; color: var(--ink); background: #fff; }

.limitations { display: flex; gap: 1rem; margin-top: 1rem; padding: 1.3rem 1.5rem; border: 1px solid #e6d7ba; border-radius: 14px; color: #6c5839; background: #fff8e9; }
.limitations > i { margin-top: .15rem; }
.limitations strong { font-size: .82rem; }
.limitations ul { margin: .5rem 0 0; padding-left: 1.1rem; font-size: .76rem; line-height: 1.65; }

@media (max-width: 900px) {
  .summary-grid { grid-template-columns: repeat(2, 1fr); }
  .insight-grid { grid-template-columns: 1fr; }
  .table-toolbar { flex-direction: column; }
  .filters { width: 100%; align-items: stretch; flex-direction: column; }
  .search-field input { width: 100%; }
  .risk-filters { overflow-x: auto; }
}

@media (max-width: 620px) {
  .results-header { align-items: flex-start; flex-direction: column; }
  .report-actions { width: 100%; justify-content: space-between; }
  .summary-grid { grid-template-columns: 1fr; }
}
</style>
