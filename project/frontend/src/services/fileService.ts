import api from './api'

export interface UploadedFile {
  name: string
  path: string
}

export interface UploadResponse {
  success: boolean
  message: string
  file: UploadedFile
}

export const uploadFile = async (
  file: File,
  onProgress?: (percentage: number) => void
): Promise<UploadResponse> => {
  const formData = new FormData()

  // "file" must match request.files["file"] in Flask.
  formData.append('file', file)

  const response = await api.post<UploadResponse>(
    '/upload',
    formData,
    {
      onUploadProgress: (progressEvent) => {
        if (!progressEvent.total) {
          return
        }

        const percentage = Math.round(
          (progressEvent.loaded * 100) / progressEvent.total
        )

        onProgress?.(percentage)
      }
    }
  )

  return response.data
}