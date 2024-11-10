<template>
  <div class="user-message" :class="{ reverse: reverse }">
    <div :class="{ reverse: reverse }">
      <q-icon
        class="user-message__avatar"
        :color="reverse ? 'secondary' : 'primary'"
        :name="
          props.user.name !== 'admin' ? 'person_outline' : symRoundedNeurology
        "
        size="40px"
      />
      <div class="user-message__thumbs" v-if="userStore.user.username !== props.user.name && userStore.user.username !== 'admin'">
        <q-btn :flat="!like" class="q-mb-xs" dense round color="positive" @click="like=!like; dislike = false">
          <q-icon size="24px" :name="symRoundedThumbUp" />
        </q-btn>
        <q-btn :flat="!dislike" dense round color="negative" @click="dislike=!dislike; like=false">
          <q-icon size="24px" :name="symRoundedThumbDown" />
        </q-btn>
      </div>
      <div class="user-message__content" :style="{alignItems: reverse?'end':'start'}">
        <div class="q-mx-md q-mb-xs text-grey-8" :style="{textAlign: reverse?'right': 'start'}">
          {{ timeFormat() }} {{ isLinksShown}}
        </div>
        <div
          class="user-message__text-block"
          :class="{ 'reverse-color': reverse }"
        >
          <div
            class="user-message__text-block__text"
            ref="preview"
            :class="{ 'q-mt-xs': reverse }"
          >
            <MdPreview style="background-color: transparent;" :modelValue="formatMessageText()" language="ru"/>
          </div>
        </div>
        <div v-if="isLinksShown" class="user-message__links q-gutter-md" :style="{justifyContent: reverse?'end':'start'}">
          <div v-for="ref in props.refs" class="row" :key="ref">
            <button  @click="handleRefClick(JSON.parse(ref).url)"  class="user-message__links__link q-mr-xs relative-position" v-ripple="{ color: 'blue-3' }" :style="{ borderRadius: reverse?'12px 0 0 12px':'2px 0 0 12px'}">
              {{ parseRef(ref).name }}
            </button>
            <button  @click="handleRefClick(JSON.parse(ref).slide_url)" class="user-message__links__link relative-position" v-ripple="{ color: 'blue-3' }" :style="{ borderRadius: reverse?'0 2px 12px 0':'0 12px 12px 0'}">
              {{ parseRef(ref).slide_name }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { symRoundedNeurology, symRoundedThumbUp, symRoundedThumbDown } from '@quasar/extras/material-symbols-rounded'
import { Message } from 'src/stores/MessageStore'
import { MdPreview, config } from 'md-editor-v3'
import 'md-editor-v3/lib/style.css'
import ru from '@vavt/cm-extension/dist/locale/ru'
import { computed, onMounted, ref } from 'vue'
import { useUserStore } from 'src/stores/UserStore'

config({
  editorConfig: {
    languageUserDefined: {
      ru
    }
  }
})

const userStore = useUserStore()

const like = ref(false)
const dislike = ref(false)

const preview = ref<HTMLDivElement>()

const isLinksShown = computed(() => {
  return props.text !== 'Извините, но в доступных мне данных нет информации, которая позволила бы мне завершить ваш вопрос. Я могу ответить только на вопросы, используя информацию из базы данных.'
})

const timeFormat = () => {
  const tIndex = props.created_at.indexOf('T')
  const commaIndex = props.created_at.indexOf('.')
  return props.created_at.slice(tIndex + 1, commaIndex - 3)
}

const parseRef = (reference: string) => {
  return JSON.parse(reference)
}

const formatMessageText = () => {
  return props.text.replaceAll('\'\'\'', '```')
}

function handleRefClick (url: string) {
  window.open(url, '_blank')
}

onMounted(() => {
  const links = preview.value?.querySelectorAll('a') as HTMLLinkElement[] | undefined
  links?.forEach((link) => {
    if (link.href.slice(-4) === '.svg' || link.href.slice(-4) === '.jpg' || link.href.slice(-4) === '.png' || link.href.slice(-4) === 'webp') {
      const img = document.createElement('img')
      img.src = link.href
      link.replaceWith(img)
    }
  })
})

const props = defineProps<Message & { reverse?: boolean, refs: string[] | null }>()
</script>
<style scoped lang="scss">
.user-message {
  display: flex;
  width: 100%;
  position: relative;
  & > :first-child {
    display: flex;
  }
  &__text-block {
    background-color: white;
    width: fit-content;
    margin: 0 16px;
    border-radius: 4px 24px 24px 4px;
    padding: 8px 16px 12px 16px;
    &__name {
      font-size: 18px;
      color: $primary;
    }
    &__text {
      & :deep(.md-editor-preview-wrapper){
        padding: 0;
      }
      & :deep(.md-editor-preview){
        word-break: normal;
      }
      & :deep(.md-editor-preview > :first-child){
        margin-top: 0;
      }
      & :deep(.md-editor-preview > :last-child){
        margin-bottom: 0;
      }
    }
  }
  &__content{
    display: flex;
    flex-direction: column;
    position: relative;
  }
  &__thumbs {
    position: absolute;
    display: flex;
    flex-direction: column;
    margin-left: 2px;
    margin-right: 2px;
    top:42px;
  }
  &__links{
    display: flex;
    flex-wrap: wrap;
    margin: 8px 16px 0 8px;
    &__link{
      background-color: $secondary;
      transition: background-color 0.35s ease;
      color:white;
      cursor: pointer;
      padding: 8px 12px;
      border: 0;
      &:hover{
        background-color: rgba(0, 102, 255, 0.9);
      }
    }
  }
}
.reverse {
  flex-direction: row-reverse;
  & .user-message__text-block{
    border-radius: 24px 4px 4px 24px;
  }
}
.reverse-color {
  background-color: rgb(227, 237, 255);
}
</style>
