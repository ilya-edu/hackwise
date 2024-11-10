import axios, { AxiosError } from 'axios'
import { useCookies } from 'vue3-cookies'
import AuthController from './services/directoryAuth'

const axiosInstance = axios.create({
  baseURL: 'https://skillscanner-api.kovalev.team/api/v1/'
})

axiosInstance.interceptors.request.use(function (config) {
  const { cookies } = useCookies()

  if (cookies.isKey('access_token') && config.headers.Authorization === undefined) {
    config.headers.Authorization = 'Bearer ' + cookies.get('access_token')
  }

  return config
})
axiosInstance.interceptors.response.use(null, async function (error: AxiosError) {
  const { cookies } = useCookies()

  if (error?.response?.status === 403 && error?.config !== undefined) {
    const resp = await AuthController.login('password', 'admin@mail.com')

    cookies.set('access_token', resp.access_token)
    error.config.headers.Authorization = 'Bearer ' + cookies.get('access_token')

    return await axios.request(error.config)
  }
})

export default axiosInstance
