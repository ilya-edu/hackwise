import axios from 'axios'

export const baseHTTPClient = axios.create({
  baseURL: 'https://skillscanner-api.kovalev.team/api/v1/'
})
