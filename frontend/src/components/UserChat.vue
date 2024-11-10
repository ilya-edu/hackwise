<template>
  <div class="user-chat" ref="scrollContainer">
    <div class="user-chat__scroll-item" v-if="lastMessageUser && !userStore.isAdmin" >
      <UserMessageSkeleton />
    </div>
    <div
      class="user-chat__scroll-item"
      v-for="message in messages"
      :key="message.id"
    >
      <UserMessage :reverse="message.user.name === userStore.user.username" v-bind="message" :refs="message.references" />
    </div>
  </div>
</template>
<script setup lang="ts">
import UserMessage from './UserMessage.vue'
import UserMessageSkeleton from './UserMessageSkeleton.vue'
import { Message, useMessageStore } from 'src/stores/MessageStore'
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { MessageService } from 'src/api/services/MessageService'
import { useUserStore } from 'src/stores/UserStore'
import { throttle } from 'quasar'
import { useStorage } from '@vueuse/core'
const currentRoomId = useStorage('currentRoom', -1)

const userStore = useUserStore()
const messageStore = useMessageStore()

const oldMessages = ref<Message[]>([])
let oldMessagesOffset = 0
const oldMessagesLoading = ref(false)

const props = defineProps<{searchedMessages: Message[]}>()

const messages = computed<Message[]>(() => {
  if (props.searchedMessages.length) {
    return props.searchedMessages
  }
  return [...[...messageStore.messages].reverse(), ...oldMessages.value]
})

const lastMessageUser = computed(() => {
  return messages.value.at(0)?.user?.name !== 'admin' && messages.value.at(0)?.user?.name !== 'manager' && messages.value.length
})

const scrollContainer = ref<HTMLDivElement>()

function scrollBottom () {
  if (scrollContainer.value) {
    scrollContainer.value.scrollTop = scrollContainer.value.scrollHeight
  }
}

function listenScroll () {
  if (scrollContainer.value?.clientHeight && scrollContainer.value.scrollHeight) {
    if (scrollContainer.value.clientHeight - scrollContainer.value.scrollHeight + 100 > scrollContainer.value?.scrollTop) {
      fetchMessages()
    }
  }
}

const fetchMessages = throttle(async function () {
  if (!oldMessagesLoading.value) {
    oldMessagesLoading.value = true
    oldMessages.value = [...oldMessages.value, ...(await MessageService.getMessages(oldMessagesOffset))]
    oldMessagesOffset += 20
    oldMessagesLoading.value = false
  }
}, 500)

watch(() => messageStore.currentRoomId, (v) => {
  currentRoomId.value = v
  oldMessagesOffset = 0
  oldMessages.value = []
  fetchMessages()
})
onMounted(() => {
  if (messageStore.currentRoomId === -1 && currentRoomId.value !== -1) {
    messageStore.currentRoomId = currentRoomId.value
  }
  messageStore.connect()
  fetchMessages()
  if (scrollContainer.value) {
    scrollContainer.value.addEventListener('scroll', listenScroll)
  }
})
onBeforeUnmount(() => {
  scrollContainer.value?.removeEventListener('scroll', listenScroll)
})

defineExpose({
  scrollBottom
})
</script>
<style scoped lang="scss">
.user-chat {
  display: flex;
  flex-direction: column-reverse;
  max-height: 100%;
  overflow-y: scroll;
  &__scroll-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-top: 20px;
    & > * {
      max-width: 1000px;
    }
  }
}
</style>
