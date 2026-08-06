<script setup lang="ts">
import { ref } from 'vue'
import axios from 'axios'

import Button from 'primevue/button'
import FileUpload from 'primevue/fileupload'
import ProgressBar from 'primevue/progressbar'
import Toast from 'primevue/toast'

import { useToast } from 'primevue/usetoast'
import { uploadFile } from '@/services/fileService'

interface PrimeVueFileSelectEvent {
  files: File[]
}

const toast = useToast()

const selectedFile = ref<File | null>(null)
const uploading = ref<boolean>(false)
const uploadProgress = ref<number>(0)

const handleFileSelect = (
  event: PrimeVueFileSelectEvent
): void => {
  selectedFile.value = event.files[0] ?? null
  uploadProgress.value = 0
}

const handleUpload = async (): Promise<void> => {
  if (!selectedFile.value) {
    toast.add({
      severity: 'warn',
      summary: 'No file selected',
      detail: 'Please select a file first.',
      life: 3000
    })

    return
  }

  try {
    uploading.value = true
    uploadProgress.value = 0

    const response = await uploadFile(
      selectedFile.value,
      (percentage: number) => {
        uploadProgress.value = percentage
      }
    )

    toast.add({
      severity: 'success',
      summary: 'Upload successful',
      detail: response.message,
      life: 3000
    })

    selectedFile.value = null
  } catch (error: unknown) {
    let message = 'The file could not be uploaded.'

    if (axios.isAxiosError(error)) {
      message =
        error.response?.data?.message ??
        error.message
    }

    toast.add({
      severity: 'error',
      summary: 'Upload failed',
      detail: message,
      life: 4000
    })
  } finally {
    uploading.value = false
  }
}
</script>

<template>
  <section class="upload-container">
    <Toast />

    <h2>Upload CTI document</h2>

    <FileUpload
      name="file"
      mode="advanced"
      accept=".pdf,.txt,.json"
      :multiple="false"
      :max-file-size="5_000_000"
      :custom-upload="true"
      :show-upload-button="false"
      :show-cancel-button="false"
      choose-label="Choose file"
      @select="handleFileSelect"
    >
      <template #empty>
        <div class="drop-area">
          <i class="pi pi-cloud-upload upload-icon" />

          <p>Drag and drop your file here</p>

          <small>
            PDF, TXT or JSON — maximum 5 MB
          </small>
        </div>
      </template>
    </FileUpload>

    <div
      v-if="selectedFile"
      class="selected-file"
    >
      <p>
        Selected:
        <strong>{{ selectedFile.name }}</strong>
      </p>

      <Button
        label="Upload to Flask"
        icon="pi pi-upload"
        :loading="uploading"
        @click="handleUpload"
      />
    </div>

    <ProgressBar
      v-if="uploading || uploadProgress > 0"
      :value="uploadProgress"
      class="progress-bar"
    />
  </section>
</template>

<style scoped>
.upload-container {
  width: min(700px, 90%);
  margin: 40px auto;
}

.drop-area {
  min-height: 180px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  text-align: center;
}

.upload-icon {
  font-size: 3rem;
}

.drop-area p {
  margin: 0;
  font-weight: 600;
}

.selected-file {
  margin-top: 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
}

.progress-bar {
  margin-top: 20px;
}
</style>