import api from './api'

export type RiskLevel = 'High' | 'Medium' | 'Low' | 'Unknown'

export interface VulnerabilityEvidence {
  cve_id: string
  summary: string
  severity: string
  cvss_score: number | null
  cwe: string
  patch_status: string
  exploit_evidence: string
  recommendation: string
  references: string[]
}

export interface DependencyAssessment {
  package: string
  installed_version: string
  dependency_group: string
  risk_level: RiskLevel
  confidence: number
  candidate_zero_day_indicator: string
  known_vulnerabilities: VulnerabilityEvidence[]
  recommendation: string
  human_review_required: boolean
}

export interface AnalysisReport {
  report_id: string
  generated_at: string
  source_file: string
  analysis_mode: string
  summary: {
    dependency_count: number
    dependencies_with_matches: number
    known_vulnerability_count: number
    overall_risk_level: RiskLevel
    risk_distribution: Record<RiskLevel, number>
    confidence: number
  }
  assessments: DependencyAssessment[]
  ai_analysis: Record<string, unknown> | null
  coverage: {
    dataset: string
    records_indexed: number
    dataset_available: boolean
  }
  limitations: string[]
  human_review_required: boolean
}

export interface AnalysisResponse {
  success: boolean
  message: string
  report: AnalysisReport
}

export interface HealthResponse {
  success: boolean
  message: string
  service: string
  version: string
  dataset: {
    available: boolean
    records_indexed: number
  }
  qwen_configured: boolean
}

export const analyzeFile = async (
  file: File,
  onProgress?: (percentage: number) => void
): Promise<AnalysisReport> => {
  const formData = new FormData()
  formData.append('file', file)

  const response = await api.post<AnalysisResponse>('/analyze', formData, {
    onUploadProgress: (progressEvent) => {
      if (!progressEvent.total) return
      onProgress?.(Math.round((progressEvent.loaded * 100) / progressEvent.total))
    }
  })

  return response.data.report
}

export const getHealth = async (): Promise<HealthResponse> => {
  const response = await api.get<HealthResponse>('/health')
  return response.data
}

export const getReport = async (reportId: string): Promise<AnalysisReport> => {
  const response = await api.get<{ success: boolean; report: AnalysisReport }>(
    `/report/${reportId}`
  )
  return response.data.report
}
