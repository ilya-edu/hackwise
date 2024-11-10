import { useCookies } from 'vue3-cookies'
import { baseHTTPClient } from '../baseHTTPClient'
import { AxiosResponse } from 'axios'

export interface Tokens {
  access_token: string
  refresh_token: string
}

class AuthController {
  static base_url = 'auth/'

  static async login (pass: string, email: string): Promise<Tokens> {
    const resp = await baseHTTPClient.post(this.base_url + 'authenticate', {
      email,
      password: pass
    })

    return resp.data as Tokens
  }

  static async refresh (): Promise<AxiosResponse> {
    const { cookies } = useCookies()

    const resp = await baseHTTPClient.post(this.base_url + 'refresh-token', null, {
      headers: {
        Authorization: 'Bearer ' + cookies.get('refresh_token')
      }
    })
    cookies.set('access_token', resp.data.access_token as string, '1d')
    return resp
  }
}
export default AuthController
