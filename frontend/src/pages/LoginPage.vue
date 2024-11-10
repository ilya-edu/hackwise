<template>
  <div class="login-wrapper" :style="{'background-image': 'url('+backgroundImage+')'}">
    <div class="auth-card">
      <div class="auth-card__logo">
        <img :src="logo" style="width:70%" />
      </div>
      <div class="auth-card-body">
        <q-form @submit="loginUser()" ref="form" class="auth-card-form">
          <q-input :error="loginError" v-model="login" :rules="loginRules" label="Логин" />
          <q-input v-model="pass" :type="showPass?'text':'password'" :rules="passRules" label="Пароль">
            <template #append>
              <q-btn @click="showPass = !showPass" round flat padding="2px" :icon="showPass?'visibility_off':'visibility'" />
            </template>
          </q-input>
        </q-form>
        <div class="auth-card-form-actions">
          <q-checkbox v-model="remeber" density="comfortable" hide-details label="Запомнить меня" />
          <div class="auth-card-form-forgot-link">Забыли пароль?</div>
        </div>
        <div class="auth-card-form-action-btns">
          <q-btn @click="loginGuest()" class="full-width shadow-1" unelevated color="accent" text-color="#222">
            Войти как гость
          </q-btn>
          <q-btn @click="loginUser()" class="full-width q-mt-md" color="primary">
            Войти
          </q-btn>
        </div>
      </div>
    </div>
  </div>
</template>
<script lang="ts" setup>
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import logo from 'assets/media_wise_logo.png'
import { useUserStore } from 'stores/UserStore'
import { useRouter } from 'vue-router'
import { Notify } from 'quasar'
import backgroundImage from 'assets/MediaWise.jpg'

const userStorage = useUserStore()
const router = useRouter()
const error = ref(false)
const loginError = ref(false)

const showPass = ref(false)

const form = ref()

const login = ref('')
const loginRules = [(v: string) => (v.length ? true : 'Поле обязательно')]

const pass = ref('')
const passRules = [(v: string) => (v.length ? true : 'Поле обязательно')]

const remeber = ref(false)

async function validate () {
  const valid = await form.value.validate()
  if (valid) {
    const resp = await userStorage.login(login.value, pass.value)
    if (resp.status === 401) {
      Notify.create({
        type: 'negative',
        message: 'Неправильный логин или пароль'
      })
    }
    if (userStorage.user.accessToken && userStorage.user.refreshToken) {
      router.push('/')
    } else {
      error.value = true
    }
  }
}

async function loginUser (e?: KeyboardEvent) {
  if (e) {
    const key = e.which || e.keyCode || 0
    if (key === 13) {
      validate()
    }
  } else {
    validate()
  }
}

function loginGuest () {
  if (!login.value) {
    userStorage.user.username = 'user_' + crypto.randomUUID()
  } else {
    userStorage.user.username = login.value + '_' + crypto.randomUUID()
  }

  router.push('/')
}

watch(login, () => {
  loginError.value = false
})

onMounted(() => {
  document.addEventListener('keypress', loginUser)
})
onBeforeUnmount(() => {
  document.removeEventListener('keypress', loginUser)
})
</script>
<style scoped lang="scss">
.login-wrapper {
  height: 100dvh;
  width: 100dvw;
  background-size: contain;
  background-repeat: no-repeat;
  align-items: center;
  display: flex;
  justify-content: space-around;
  background-position: center;
  background-size: cover;

  .auth-card {
    border-radius: 20px;
    padding: 24px 30px 4px 30px;
    width: 440px;
    max-width: 90vw;
    background-color: white;
    &__logo{
      display: flex;
      justify-content: center;
      padding: 24px;
      min-height: 87px;
    }
    .auth-card-body {
      padding: 24px;

      text-align: end;

      .auth-card-form {
        &> :first-child {
          margin-bottom: 8px;
        }

        &> :nth-child(2) {
          margin-bottom: -8px;
        }
      }

      .auth-card-form-actions {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-top: 32px;
        gap: 20px;
        & > :first-child{
          margin-left: -10px;
        }

        .auth-card-form-forgot-link {
          cursor: pointer;
          color: $secondary;
          font-size: 14px;
          text-decoration: underline;
        }
      }

      .auth-card-form-action-btns {
        margin-top: 32px;
      }
    }
  }
}
</style>
