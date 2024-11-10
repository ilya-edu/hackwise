<template>
  <q-list class="rooms" padding>
    <div class="rooms__search">
      <q-input filled class="q-mb-md q-mx-md" @focus="searchFocused=true" @blur="searchFocused=false" @mouseover="searchHovered = true" @mouseleave ="searchHovered = false" v-model="search" placeholder="Поиск" >
        <template v-slot:append>
          <q-icon :color="searchIconColor" name="search" />
        </template>
      </q-input>
    </div>
    <q-item class="rooms__room" :class="{'rooms__room-selected': messageStore.currentRoomId === room.id}" @click="changeRoom(room.id)" clickable v-ripple="{color: 'primary'}" v-for="room in searchedRooms" :key="room.id">
      {{ room.name }}
      <div class="column q-ml-sm items-center">
        <q-icon v-if="room.human_need" color="negative" class="q-mb-xs" size="20px" name="help_outline" />
        <q-btn flat dense round padding="4px" @click.stop="handleDelete(room.id)">
          <q-icon color="negative" size="20px" name="delete_outline" />
        </q-btn>
      </div>
    </q-item>
  </q-list>
</template>
<script setup lang="ts">
import { MessageService, Room } from 'src/api/services/MessageService'
import { useMessageStore } from 'src/stores/MessageStore'
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

const messageStore = useMessageStore()
const rooms = ref<Room[]>([])
const router = useRouter()
const searchedRooms = computed(() => {
  return rooms.value.filter((room) => {
    return room.name.toLowerCase().includes(search.value.trim().toLowerCase())
  }).sort((room1, room2) => {
    if (room1.human_need) {
      return -1
    }
    if (room2.human_need) {
      return 1
    }
    return 0
  })
})

const search = ref('')
const searchHovered = ref(false)
const searchFocused = ref(false)

const searchIconColor = computed(() => {
  if (searchFocused.value) {
    return 'primary'
  }
  if (searchHovered.value) {
    return 'black'
  }
  return undefined
})

onMounted(async () => {
  rooms.value = await MessageService.getRooms()
  setInterval(async () => {
    rooms.value = await MessageService.getRooms()
  }, 3000)
})

function changeRoom (id: number) {
  router.push({ name: 'User' })
  messageStore.changeRoom(id)
}
async function handleDelete (id: number) {
  await MessageService.deleteRoom(id)
  rooms.value = await MessageService.getRooms()
}
</script>
<style scoped lang="scss">
.rooms{
  background-color:white;
  padding: 0px 8px;
  &__search {
    background-color: white;
    position: sticky;
    top:0px;
    padding-top:16px;
    z-index: 1;
    margin-right: 2px;
  }
  &__room {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-right: 2px;
  }
  &__room-selected {
    background-color: rgba(0, 119, 255, 0.3);
  }
}
</style>
