<template>
  <div class="expansion-file"
    :class="{'opened':opened}"
  >
    <div class="expansion-file__inner">
      <a
        class="col"
        @click.stop="opened = !opened"
      >
        <q-item
          :class="{
            'file-system-scroll__file':!fileStore.fileSelected(file),
            'file-system-scroll__file-selected':fileStore.fileSelected(file),
            'bg-accent q-mb-sm rounded-borders cursor-pointer':true
          }"
          :key="file.id"
          v-ripple:white
        >

          <div class="row items-center justify-between full-width">
            <span class="text-white text-subtitle1">
              {{ file.name }}
            </span>
          </div>
        </q-item>
      </a>
      <div class="q-px-lg q-pb-md q-pt-sm fit">
        <div class="expansion-file__inner__row">
          Организационная структура: : <b>{{file.year}}</b>
        </div>
        <div class="expansion-file__inner__row">
          Файл добавлен: <b>{{file.createdAt.slice(0,10).split('-').reverse().join('.')}}</b>
        </div>
        <div class="expansion-file__inner__row">
          Скачать файл:
          <a :href="prepareFileUrl(file.url)"
            class="q-ml-sm"
            target="_blank"
          >
            <q-btn flat
              color="primary"
              :icon="matDownload"
              size="12px"
              padding="4px"
            />
          </a>
        </div>
        <q-btn :icon="outlinedDelete"
          @click.stop="promptDelete(file.id, file.name)"
          class="expansion-file__inner__delete"
          round
          color="red-10"
          size="14px"
          padding="6px"
          flat
        />
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import DirectoryController, { type FileData } from 'src/api/services/directoryController'
import { useFileStore } from 'src/stores/fileStore'
import { matDownload } from '@quasar/extras/material-icons'
import { outlinedDelete } from '@quasar/extras/material-icons-outlined'
import { useQuasar } from 'quasar'
import { ref } from 'vue'

const fileStore = useFileStore()
const q = useQuasar()
const opened = ref(false)

defineProps<{
  file: FileData
}>()

function promptDelete (id: number, name: string): void {
  q.dialog({
    title: 'Удалить файл ' + name,
    message: 'Вы уверены?',
    cancel: 'Отмена',
    ok: 'Да'
  }).onOk(() => {
    fileStore.files = fileStore.files.filter((f) => f.id !== id)
    void DirectoryController.deleteFile(id).then(async () => {
      if (fileStore.folder !== undefined) { fileStore.files = await DirectoryController.getFileList(fileStore.folder.id) }
    })
  })
}

function prepareFileUrl (url: string) {
  return 'https://minio.kovalev.team' + url.slice(21, url.indexOf('?'))
}
</script>
<style scoped lang="scss">
@import "../css/quasar.variables.scss";

.expansion-file{
  display: grid;
  background-color: white;
  grid-template-rows: 0fr;
  transition: grid-template-rows 0.33s ease-out;
  border-radius: 4px;
  &__inner {
    overflow: hidden;
    position: relative;
    min-height: 48px;
    &__row{
      font-size: 16px;
      height: 30px;
    }
    &__delete{
      position: absolute;
      right:8px;
      top: 56px;
    }
  }
  &.opened {
    grid-template-rows: 1fr;
  }
}
</style>
