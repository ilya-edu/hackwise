<template>
  <div class="q-pa-md">
    <folder-system v-show="mode==='folders'" @open-folder="mode = 'files';folderId = $event" />
    <file-system :folder-id="folderId" v-if="mode==='files'" @back="mode='folders'"/>
  </div>
</template>
<script setup lang="ts">
import FolderSystem from 'src/components/FolderSystem.vue'
import FileSystem from 'src/components/FileSystem.vue'
import { ref } from 'vue'

const folderId = ref()
const mode = ref<'folders' | 'files'>('folders')
</script>
<style scoped lang="scss">
</style>
