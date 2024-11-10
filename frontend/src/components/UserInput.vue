<template>
  <div
    @click="
      model = formattedSearch;
      prompt = undefined;
    "
    v-if="prompt"
    class="prompt"
  >
    Возможно вы имели ввиду: {{ formattedSearch }}?
  </div>
  <div class="mark-editor-wrapper" :class="{'user-input-animated': !focused}">
    <MdEditor @keydown="keyPress" class='mark-editor-wrapper__editor' @focus="focused = true" :toolbars-exclude="['github', 'catalog', 'htmlPreview', 'preview', 'fullscreen', 'pageFullscreen', 'save', 'image', 'codeRow']" :preview="false" language="ru" v-model="model" />
    <q-btn
        ref="btn"
        @click="extended = !extended"
        flat
        color="rgb(63, 74, 84)"
        class="mark-editor-wrapper__btn-expand"
        padding="0 4px 0 4px"
      >
        <q-icon
          :name="symRoundedKeyboardArrowUp"
          :class="{'rotate-180': extended}"
          size="24px"
          class="mark-editor-wrapper__btn-expand__icon"
        ></q-icon>
    </q-btn>
    <transition
      appear
      enter-active-class="animated fadeIn"
      leave-active-class="animated fadeOut"
    >
      <q-btn
        ref="btn"
        @click="send()"
        v-show="model.trim().length"
        flat
        rounded
        color="primary"
        class="mark-editor-wrapper__btn"
        padding="5px 6px 7px 6px"
      >
        <q-icon
          :name="symRoundedSend"
          size="30px"
          class="mark-editor-wrapper__btn__icon"
        ></q-icon>
      </q-btn>
    </transition>
  </div>
</template>
<script setup lang="ts">
import { symRoundedSend, symRoundedKeyboardArrowUp } from '@quasar/extras/material-symbols-rounded'
import { QBtn, debounce } from 'quasar'
import { MessageService } from 'src/api/services/MessageService'
import { spellcheck } from 'src/api/services/SpellCheck'
import { computed, ref, watch } from 'vue'
import { MdEditor, config } from 'md-editor-v3'
import 'md-editor-v3/lib/style.css'
import ru from '@vavt/cm-extension/dist/locale/ru'

const focused = ref(false)

const model = computed({
  get () {
    return props.modelValue
  },
  set (v: string) {
    emit('update:modelValue', v)
  }
})

const extended = computed({
  get () {
    return props.extended
  },
  set (v: string) {
    emit('update:extended', v)
  }
})

config({
  editorConfig: {
    languageUserDefined: {
      ru
    }
  }
})

const emit = defineEmits(['update:modelValue', 'update:extended', 'send'])

const props = defineProps<{
  modelValue: string;
  extended: boolean;
}>()

async function send () {
  if (model.value) {
    await MessageService.sendMessage(model.value)
    emit('send')
    setTimeout(() => {
      model.value = ''
      prompt.value = undefined
    }, 1)
  }
}

const prompt = ref<
  | {
      pos: number;
      len: number;
      s: string[];
    }[]
  | undefined
>(undefined)

const formattedSearch = computed(() => {
  let str = model.value
  if (prompt.value) {
    prompt.value.forEach((v) => {
      str = str.slice(0, v.pos) + v.s[0] + str.slice(v.pos + v.len)
    })
  } else {
    str = ''
  }
  return str
})

const searchHandle = async (v: string) => {
  const resp = await spellcheck(v)
  prompt.value = resp
  if (prompt.value && !prompt.value.length) {
    prompt.value = undefined
  }
}

const keyPress = (k: KeyboardEvent) => {
  if (k.shiftKey && k.key === 'Enter') {
    const event = new KeyboardEvent('keydown', {
      key: 'Enter',
      code: 'Enter',
      which: 13,
      keyCode: 13
    })
    document.getElementsByClassName('cm-content')[0].dispatchEvent(event)
    return
  }
  if (k.key === 'Enter') {
    send()
  }
}

const debouncedSearch = debounce(searchHandle, 400)

const inputHeight = computed(() => {
  if (extended.value) {
    return '400px'
  }
  return '108px'
})

watch(model, (v: string) => {
  if (v) {
    debouncedSearch(v)
  }
})
</script>
<style scoped lang="scss">
@use "sass:color";
@import "../css/quasar.variables.scss";

.mark-editor-wrapper{
  overflow: auto !important;
  border-radius: 16px;
  &__editor{
    position: static;
    overflow: auto !important;
    height: v-bind(inputHeight);
    transition: height 0.55s ease;
    border-radius: 16px;
    & :deep(.md-editor-footer){
      display: none;
    }
  }
  &__btn {
    position: absolute;
    right: 28px;
    top: 67px;
    &__icon {
      position: relative;
      top: 2px;
      left: 2px;
    }
  }
  &__btn-expand {
    position: absolute;
    right: 84px;
    top: 30px;
  }
}

.user-input {
  background-color: white;
  border-radius: 28px;
  & :deep(.q-field__control:before) {
    border: none !important;
  }
  & :deep(.q-field__control) {
    padding-left: 24px;
  }
  & :deep(*) {
    font-size: 1.2rem;
  }
}

.prompt {
  position: absolute;
  top: 2px;
  left: 40px;
  cursor: pointer;
  color: rgb(41, 41, 255);
  &:hover {
    text-decoration: underline;
  }
}

.category {
  border: 1px solid $primary;
  height: min-content;
  border-radius: 4px;
  padding: 0 8px;
  color: $primary;
}

.user-input-animated {
  animation: pulse-animation 1.5s infinite;
}

@keyframes pulse-animation {
  0% {
    box-shadow: 0 0 0 0 color.adjust($primary, $alpha: -0.8);
  }
  100% {
    box-shadow: 0 0 10px 20px color.adjust($primary, $alpha: -1);
  }
}
</style>
