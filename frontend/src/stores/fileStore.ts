import { type FolderData, type FileData } from 'src/api/services/directoryController'
import { defineStore } from 'pinia'
import DirectoryController from 'src/api/services/directoryController'

export const useFileStore = defineStore('file', {
  state: () => ({
    folders: [] as FolderData[],
    folder: undefined as FolderData | undefined,
    files: [] as FileData[],
    file: undefined as FileData | undefined
  }),
  actions: {
    async setUrlParams () {
      await this.router.replace({
        path: this.router.currentRoute.value.path,
        query: {
          ...this.router.currentRoute.value.query,
          file: this.file?.id,
          folder: this.folder?.id
        }
      })
    },
    async recoverFromUrlParams () {
      this.folders = await DirectoryController.getFolderList()
      if (this.folder === undefined) this.folder = this.folders.find((f) => f.id === Number(this.router.currentRoute.value.query.folder))
      if (this.folder !== undefined) this.files = await DirectoryController.getFileList(this.folder.id)
      if (this.file === undefined) this.file = this.files.find((f) => f.id === Number(this.router.currentRoute.value.query.file))
    },
    fileSelected (file: FileData) {
      if (this.file === undefined) return false
      return this.file.id === file.id
    },
    async selectFile (file: FileData) {
      this.file = file
    },
    async selectFolder (folder: FolderData) {
      this.folder = folder
    }
  },
  getters: {
  }
})
