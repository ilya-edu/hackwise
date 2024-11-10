<template>
<q-btn color="white" padding="xs" flat>
  <q-icon :name="symRoundedSettings" size="28px" />
  <q-menu class="model-settings__menu">
    <div class="text-subtitle1 q-mb-sm">Температура</div>
    <q-slider v-model=temperature :min="0" :max="1" :step="0.01" label />
    <div class="text-subtitle1 q-mb-sm q-mt-md">Максимальная длина ответа</div>
    <q-slider v-model="maxRespLen" :min="0" :max="4096" label />
  </q-menu>
</q-btn>
</template>
<script setup lang="ts">
import { symRoundedSettings } from '@quasar/extras/material-symbols-rounded'
import { ref } from 'vue'

const temperature = ref(0.6)
const maxRespLen = ref(2048)

</script>
<style scoped lang="scss">
:global(.model-settings__menu) {
  max-width: 100dvw;
  width: 400px !important;
  height: fit-content;
  padding: 24px;
}
</style>
