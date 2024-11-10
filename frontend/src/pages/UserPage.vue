<template>
  <div  class="index-page">
    <UserChat ref="chat" :searchedMessages="searchedMessages" class="index-page__chat" />

    <div class="index-page__input-wrapper">
      <UserInput @send="chat.scrollBottom()" v-model:extended="expanded" v-model="input" />
    </div>
  </div>
</template>
<script setup lang="ts">
import { MessageService } from 'src/api/services/MessageService'
import UserChat from 'src/components/UserChat.vue'
import UserInput from 'src/components/UserInput.vue'
import { Message } from 'src/stores/MessageStore'
import { useSearchStore } from 'src/stores/searchStore'
import { computed, ref, watch } from 'vue'

const chat = ref()

const searchStore = useSearchStore()

const searchedMessages = ref<Message[]>([])

const expanded = ref(false)
const input = ref('')
const chatPadding = computed(() => {
  if (expanded.value) {
    return '458px'
  }
  return '166px'
})
watch(() => searchStore.search, async (v) => {
  if (!v) {
    searchedMessages.value = []
    return
  }
  const resp = await MessageService.searchMessages(v)
  if (resp) {
    searchedMessages.value = resp
  } else {
    searchedMessages.value = []
  }
})
</script>
<style scoped lang="scss">
@import "../css/app.scss";

.index-page {
  height: calc(100vh - 58px);
  display: flex;
  align-items: center;
  flex-direction: column;
  &__chat{
    flex: 1 0 auto;
    width: 100%;
    transition: padding 0.55s ease;
    padding-bottom: v-bind(chatPadding)
  }
  &__input-wrapper {
    @extend .background;
    position: absolute;
    border-radius: 12px 12px 0 0;
    bottom: 0;
    width: 100%;
    padding: 24px 16px 24px 16px;
    max-width: 1024px;
  }
}
</style>
