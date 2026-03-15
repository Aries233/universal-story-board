/**
 * API 封装层
 * 统一管理所有后端 API 请求
 */
import axios from 'axios';

// 后端 API 基础 URL
const API_BASE_URL = 'http://127.0.0.1:8000/api/v1';

// 创建 axios 实例
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ========== API 接口定义 ==========

/**
 * 工作流相关 API
 */
export const workflowApi = {
  /**
   * 启动工作流
   * @param chapterId 章节 ID
   * @param mode 工作流模式（"A" = 编剧 + 角色）
   * @returns 工作流启动响应
   */
  async start(chapterId: string, mode: 'A' | 'B' = 'A') {
    const response = await api.post('/workflow/start', {
      chapter_id: chapterId,
      mode,
    });
    return response.data;
  },

  /**
   * 获取工作流状态
   * @param chapterId 章节 ID
   * @returns 工作流状态
   */
  async getStatus(chapterId: string) {
    const response = await api.get(`/workflow/status/${chapterId}`);
    return response.data;
  },
};

/**
 * 章节相关 API
 */
export const chapterApi = {
  /**
   * 获取章节详情
   * @param chapterId 章节 ID
   * @returns 章节详情
   */
  async get(chapterId: string) {
    const response = await api.get(`/chapters/${chapterId}`);
    return response.data;
  },
};

/**
 * 资产相关 API
 */
export const assetApi = {
  /**
   * 获取资产列表
   * @param projectId 项目 ID
   * @returns 资产列表
   */
  async list(projectId: string) {
    const response = await api.get('/assets', {
      params: {
        project_id: projectId,
      },
    });
    return response.data;
  },
};

/**
 * 项目相关 API
 */
export const projectApi = {
  /**
   * 获取项目列表
   * @returns 项目列表
   */
  async list() {
    const response = await api.get('/projects');
    return response.data;
  },

  /**
   * 获取项目详情
   * @param projectId 项目 ID
   * @returns 项目详情
   */
  async get(projectId: string) {
    const response = await api.get(`/projects/${projectId}`);
    return response.data;
  },
};

export default api;
