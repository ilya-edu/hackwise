<template>
  <div>
    <q-dialog v-model="addFile"
      persistent
    >
      <q-card>
        <q-card-section>
          <div class="text-h6">Добавить файл</div>

        </q-card-section>
        <q-card-section class="row items-center">
          <q-file @focusin="inputFocused = true"
            style="width:300px"
            @focusout="inputFocused = false"
            clearable
            color="primary"
            accept="pdf"
            filled
            v-model="file"
            label="Загрузить файл"
            class="cursor-pointer q-mr-lg col"
            :loading="fileLoading"
          >
            <template v-slot:prepend>
              <q-icon :color="inputFocused ? 'primary' : undefined"
                name="upload_file"
              />
            </template>
          </q-file>
          <q-input
            v-model.number="year"
            type="number"
            filled
            style="width:140px"
            label="Год"
          />
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat
            label="Отменить"
            color="primary"
            v-close-popup
          />
          <q-btn
            label="Добавить"
            :disable="!file || !year"
            color="secondary"
            @click="sendFile(file)"
            v-close-popup
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
    <div class="row items-start">
      <div class="row">
        <q-btn
          @click="addFile = true"
          :icon="matAdd"
          class="q-mb-lg"
          color="secondary"
        >
          Добавить файл
        </q-btn>
        <q-spinner v-if="fileLoading"
          size="38px"
          class="q-ml-md"
          color="primary"
          :thickness="4"
        />
      </div>
      <q-btn @click="emit('back')" flat color="secondary" padding="xs" class="q-mr-xs q-ml-md" size="md">
        <q-icon :name="symRoundedArrowBack" size="28px"  />
      </q-btn>
    </div>
    <q-virtual-scroll
      v-show="!filesLoading"
      class="file-system-scroll"
      :items="searchedFiles"
      v-slot="{ item:file }"
      separator
    >
      <expansion-file class="file-system-scroll__file shadow-default"
        :file="file"
      />
    </q-virtual-scroll>
  </div>
</template>
<script setup lang="ts">
import DirectoryController, { FileData } from 'src/api/services/directoryController'
import { computed, ref, watch } from 'vue'
import { symRoundedArrowBack } from '@quasar/extras/material-symbols-rounded'
import { matAdd } from '@quasar/extras/material-icons'
import { Notify } from 'quasar'
import { useSearchStore } from 'src/stores/searchStore'
import ExpansionFile from './ExpansionFile.vue'

const files = ref<FileData[]>([])
const searchStore = useSearchStore()
const inputFocused = ref(false)
const file = ref()
const fileLoading = ref(false)
const filesLoading = ref(false)
const year = ref(new Date().getFullYear())
const addFile = ref(false)
const props = defineProps<{folderId: number}>()

const emit = defineEmits<{back: []}>()

const searchedFiles = computed(() => {
  if (!searchStore.search) {
    return files.value
  }
  return files.value.filter((f) => searchStore.search.includes(f.name))
})

async function sendFile (f: File | undefined | null): Promise<void> {
  if (year.value === null || year.value === undefined) {
    year.value = new Date().getFullYear()
  }
  if (f === undefined || f === null) return
  fileLoading.value = true
  const formData = new FormData()
  formData.append('file', f)

  try {
    await DirectoryController.uploadFile(formData, props.folderId, year.value)
    getFiles()
  } catch (err) {
    Notify.create({
      type: 'negative',
      message: 'Превышен допустимый размер файла'
    })
  }
  file.value = undefined
  fileLoading.value = false
}

async function getFiles () {
  filesLoading.value = true
  files.value = await DirectoryController.getFileList(props.folderId)
  filesLoading.value = false
}

watch(() => props.folderId, getFiles, { immediate: true })
</script>
<style scoped lang="scss">
$text-primary: #060606;
$text-primary-thin: #393939;
$text-secondary: #5e5e5e;

$page-bg: #e4e2eb;

$primary: #003274;
$secondary: #025ea1;
$secondary-thin: #6cace4;

$primary-hover: #0032741a;

$danger: #892a2a;
$warning: #fcc30b;
$warning-accent: #fd6925;
$success: #56c02b;

  .file-system-scroll{
    max-height: calc(100vh - 276px);
    padding-right: 4px;
    &__file{
      margin-bottom: 12px;
    }
  }
</style>
