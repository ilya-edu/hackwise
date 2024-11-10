import { type AxiosResponse } from 'axios'
import coreHTTPClient from '../coreHTTPClient'

export interface FolderData {
  id: number
  name: string
  createdAt: string
}

export interface FileData {
  id: number
  name: string
  url: string
  urlWithError: string | null
  directoryEntity: FolderData
  year: number
  createdAt: string
  updatedAt: string
}

class DirectoryController {
  static async uploadFile (formData: FormData, directory: number, year: number): Promise<AxiosResponse> {
    const resp = await coreHTTPClient.post(`file/excel/upload?directory_id=${directory}&year=${year}`, formData)
    return resp.data || resp
  }

  static async getFileList (directory: number): Promise<FileData[]> {
    const resp = await coreHTTPClient.get('file?directory_id=' + directory)
    return resp.data
  }

  static async deleteFile (id: number): Promise<AxiosResponse> {
    const resp = await coreHTTPClient.delete('file/' + id)
    return resp.data
  }

  static async addFolder (name: string): Promise<AxiosResponse> {
    const resp = await coreHTTPClient.post('directory', { name })
    return resp.data
  }

  static async deleteFolder (id: number): Promise<AxiosResponse> {
    const resp = await coreHTTPClient.delete('directory/' + id)
    return resp.data
  }

  static async getFolderList (): Promise<FolderData[]> {
    const resp = await coreHTTPClient.get('directory')
    return resp.data
  }

  static async renameFolder (id: number, newName: string): Promise<AxiosResponse> {
    const resp = await coreHTTPClient.put('directory/' + id, { name: newName })
    return resp.data
  }
}
export default DirectoryController
