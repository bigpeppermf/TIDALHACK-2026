export type ProjectStatus = 'converted' | 'processing' | 'failed'

export type ProjectSourceKind = 'pdf' | 'image' | 'unknown'

export interface ProjectRecord {
  id: string
  name: string
  updatedAt: string
  updatedAtIso: string
  status: ProjectStatus
  thumbnail?: string
  latex: string
  sourceFilename?: string
  sourceKind: ProjectSourceKind
  ownerId?: string | null
}

export interface AddConvertedProjectInput {
  name: string
  latex: string
  sourceFilename?: string
  sourceKind?: ProjectSourceKind
  thumbnail?: string
  ownerId?: string | null
}
