<template>
  <div class="folders-wrapper q-gutter-lg">
    <div class="folders-wrapper__folder"
      @click="promptAdd()"
    >
      <q-icon :name="outlinedCreateNewFolder"
        color="secondary"
        size="120px"
      />
      <div class="folders-wrapper__folder__title text-secondary">
        Добавить
      </div>
    </div>
    <div
      @click="handleRedirect(f)"
      class="folders-wrapper__folder"
      v-for="f in searchedFolders"
      :key="f.id"
    >
      <q-btn :icon="matClose"
        @click.stop="promptDelete(f.name,f.id)"
        class="folders-wrapper__folder__action"
        round
        color="red-10"
        size="12px"
        padding="4px"
        flat
      />
      <q-btn :icon="outlinedEdit"
        @click.stop="promptRename(f.name,f.id)"
        class="folders-wrapper__folder__action"
        round
        style="right:20px"
        color="yellow-10"
        size="12px"
        padding="4px"
        flat
      />
      <q-icon :name="outlinedFolder"

        color="secondary"
        size="120px"
      />
      <div class="folders-wrapper__folder__title text-secondary">
        {{ f.name }}
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import DirectoryController, { type FolderData } from 'src/api/services/directoryController'
import { useFileStore } from 'src/stores/fileStore'
import { outlinedFolder, outlinedCreateNewFolder, outlinedEdit } from '@quasar/extras/material-icons-outlined'
import { matClose } from '@quasar/extras/material-icons'
import { useQuasar } from 'quasar'
import { computed, onMounted } from 'vue'
import { useSearchStore } from 'src/stores/searchStore'

const emit = defineEmits<{
  'open-folder': [id: number]
}>()

const searchStore = useSearchStore()

const searchedFolders = computed(() => {
  if (!searchStore.search) return fileStore.folders
  return fileStore.folders.filter((f) => searchStore.search.includes(f.name))
})

async function handleRedirect (f: FolderData): Promise<void> {
  await fileStore.selectFolder(f)
  emit('open-folder', f.id)
}

const fileStore = useFileStore()
const q = useQuasar()
function promptAdd (): void {
  q.dialog({
    title: 'Добавить папку',
    message: 'Введиите название папки',
    prompt: {
      model: '',
      isValid: val => val.length > 2, // << here is the magic
      type: 'text' // optional
    },
    cancel: 'Отмена',
    persistent: true
  }).onOk((data: string) => {
    void DirectoryController.addFolder(data).then(async () => {
      fileStore.folders = await DirectoryController.getFolderList()
    })
  })
}
function promptRename (name: string, id: number): void {
  q.dialog({
    title: 'Переименовать папку ' + name,
    message: 'Введиите новое название папки',
    prompt: {
      model: '',
      isValid: val => val.length > 2, // << here is the magic
      type: 'text' // optional
    },
    cancel: 'Отмена',
    persistent: true
  }).onOk((newName: string) => {
    void DirectoryController.renameFolder(id, newName).then(async () => {
      fileStore.folders = await DirectoryController.getFolderList()
    })
  })
}
function promptDelete (name: string, id: number): void {
  q.dialog({
    title: 'Удалить папку ' + name,
    message: 'Вы уверены?',
    cancel: 'Отмена',
    ok: 'Да'
  }).onOk(() => {
    void DirectoryController.deleteFolder(id).then(async () => {
      fileStore.folders = await DirectoryController.getFolderList()
    })
  })
}
onMounted(() => {
  fileStore.recoverFromUrlParams()
})
</script>
<style scoped lang="scss">
.folders-wrapper{
  display: flex;
  flex-wrap: wrap;
  &__folder{
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding:4px 12px 20px 12px;
    cursor: pointer;
    border-radius: 20px;
    &__action{
      position: absolute;
      display: none;
      z-index: 1;
      top:-10px;
      right: -10px;
    }
    &__title{
      margin-top: -12px;
      max-width: 120px;
      max-height: 40px;
      position: relative;
      text-align: center;
      text-overflow: ellipsis;
    }
    &:hover{
      & .folders-wrapper__folder__action{
        display: block;
      }
    }
  }
}
</style>
