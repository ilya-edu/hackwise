<template>
  <q-layout view="hHh Lpr lFf">
    <q-header elevated class="bg-primary">
      <q-toolbar color="white" class="q-my-xs q-mx-sm q-pr-lg">
        <div class="row">
          <q-btn @click="drawerOpened = !drawerOpened" v-if="store.user.username === 'admin'" class="q-mr-md" color="white" padding="xs" flat>
            <q-icon :name="symRoundedMenu" size="28px"  />
          </q-btn>
          <div v-else style="width:48px"></div>
          <img :src="logo" style="height:40px" />
        </div>
        <q-space />
        <div class="search" style="margin-left: -6%;">
          <q-input dark dense filled hide-hint v-model="search" placeholder="Поиск по сообщениям" >
            <template v-slot:append>
              <q-icon :color="'white'" name="search" />
            </template>
          </q-input>
        </div>
        <q-space />
        <div class="row items-center">
          <template v-if="store.user.username === 'admin'">
            <model-settings v-if="route.name==='Admin'" class="q-mr-sm" />
            <q-btn v-else @click="router.push({name: 'Admin'})" flat color="white" padding="xs" size="md">
              <q-icon :name="symRoundedFolder" size="28px"  />
            </q-btn>
          </template>
          <q-btn @click="handleClick()" flat color="white" padding="xs" size="md">
            <q-icon :name="symRoundedLogout" size="28px"  />
          </q-btn>
        </div>
      </q-toolbar>
    </q-header>
    <q-drawer
        v-model="drawerOpened"
        elevated
        :breakpoint="700"
      >
        <q-scroll-area class="fit">
          <UserRooms v-if="store.user.username === 'admin'" />
        </q-scroll-area>
      </q-drawer>
    <q-page-container>
      <q-page class="background">
        <router-view />
      </q-page>
    </q-page-container>
  </q-layout>
</template>
<script setup lang="ts">
import { useMessageStore } from 'src/stores/MessageStore'
import ModelSettings from 'src/components/ModelSettings.vue'
import logo from 'assets/media_wise_logo_white.png'
import { useUserStore } from 'src/stores/UserStore'
import UserRooms from 'src/components/UserRooms.vue'
import { symRoundedMenu, symRoundedLogout, symRoundedFolder } from '@quasar/extras/material-symbols-rounded'
import { useRoute, useRouter } from 'vue-router'
import { ref, watch } from 'vue'
import { useSearchStore } from 'src/stores/searchStore'
import { debounce } from 'quasar'

const route = useRoute()
const router = useRouter()
const store = useUserStore()
const messageStore = useMessageStore()
const drawerOpened = ref(true)

const searchStore = useSearchStore()
const search = ref('')

const setSearch = debounce(function (v) {
  searchStore.search = v
}, 500)

function handleClick () {
  messageStore.disconnect()
  store.logout()
  router.push({ name: 'Login' })
}

watch(() => store.user.username, (name) => {
  if (name !== 'admin') {
    drawerOpened.value = false
  }
}, { immediate: true })
watch(search, (v) => {
  setSearch(v)
})
</script>
