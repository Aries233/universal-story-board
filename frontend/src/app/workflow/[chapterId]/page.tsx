'use client';

/**
 * 工作流执行页面
 * 展示工作流启动、状态轮询、剧本大纲和资产卡片
 */
import { useState, useEffect } from 'react';
import { workflowApi, chapterApi, assetApi } from '@/lib/api';

// ========== 类型定义 ==========

/**
 * 工作流状态
 */
type WorkflowStatus = 'pending' | 'running' | 'completed' | 'failed';

/**
 * 工作流状态响应
 */
interface WorkflowStatusResponse {
  status: WorkflowStatus;
  progress: number;
  message?: string;
}

/**
 * 章节详情
 */
interface ChapterResponse {
  id: string;
  project_id: string;
  chapter_number: number;
  title: string;
  original_text: string;
  script?: string;
  style_guide?: Record<string, any>;
  status: string;
  created_at: string;
  updated_at: string;
}

/**
 * 资产项
 */
interface AssetItem {
  id: string;
  project_id: string;
  chapter_id?: string;
  name: string;
  type: 'character' | 'scene' | 'prop';
  description?: string;
  metadata?: Record<string, any>;
  created_at: string;
}

/**
 * 资产列表响应
 */
interface AssetListResponse {
  items: AssetItem[];
  total: number;
}

// ========== 组件 ==========

export default function WorkflowExecutionPage({
  params,
}: {
  params: { chapterId: string };
}) {
  const chapterId = params.chapterId;

  // 硬编码的项目 ID（用于调试）
  const PROJECT_ID = 'test-project-001';

  // ========== 状态 ==========

  const [workflowStatus, setWorkflowStatus] = useState<WorkflowStatus>('pending');
  const [progress, setProgress] = useState(0);
  const [isStarting, setIsStarting] = useState(false);
  const [isPolling, setIsPolling] = useState(false);
  const [chapter, setChapter] = useState<ChapterResponse | null>(null);
  const [assets, setAssets] = useState<AssetItem[]>([]);
  const [errorMessage, setErrorMessage] = useState('');

  // ========== 启动工作流 ==========

  const handleStartWorkflow = async () => {
    try {
      setIsStarting(true);
      setErrorMessage('');

      // 调用后端 API 启动工作流
      await workflowApi.start(chapterId, 'A');

      // 启动后开始轮询状态
      setIsPolling(true);
    } catch (error: any) {
      setErrorMessage(`启动失败: ${error.message || '未知错误'}`);
      setIsStarting(false);
    }
  };

  // ========== 轮询工作流状态 ==========

  useEffect(() => {
    if (!isPolling) {
      return;
    }

    const pollInterval = setInterval(async () => {
      try {
        const response: WorkflowStatusResponse = await workflowApi.getStatus(chapterId);
        setWorkflowStatus(response.status);
        setProgress(response.progress);

        // 如果工作流完成或失败，停止轮询
        if (response.status === 'completed' || response.status === 'failed') {
          setIsPolling(false);
          setIsStarting(false);

          // 工作流完成后，加载章节和资产数据
          if (response.status === 'completed') {
            await loadChapterAndAssets();
          }
        }
      } catch (error: any) {
        setErrorMessage(`获取状态失败: ${error.message || '未知错误'}`);
        setIsPolling(false);
        setIsStarting(false);
      }
    }, 2000); // 每 2 秒轮询一次

    return () => clearInterval(pollInterval);
  }, [isPolling, chapterId]);

  // ========== 加载章节和资产数据 ==========

  const loadChapterAndAssets = async () => {
    try {
      // 加载章节详情
      const chapterResponse: ChapterResponse = await chapterApi.get(chapterId);
      setChapter(chapterResponse);

      // 加载资产列表
      const assetResponse: AssetListResponse = await assetApi.list(PROJECT_ID);
      setAssets(assetResponse.items);
    } catch (error: any) {
      setErrorMessage(`加载数据失败: ${error.message || '未知错误'}`);
    }
  };

  // ========== 渲染 ==========

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 顶部操作区 */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                工作流执行 - 章节 {chapterId}
              </h1>
              <p className="text-sm text-gray-500 mt-1">
                章节 ID: {chapterId} | 项目 ID: {PROJECT_ID}
              </p>
            </div>
            <button
              onClick={handleStartWorkflow}
              disabled={isStarting || isPolling}
              className="px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isStarting ? '启动中...' : isPolling ? '执行中...' : '启动工作流'}
            </button>
          </div>
        </div>
      </div>

      {/* 状态展示区 */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {errorMessage && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-800">{errorMessage}</p>
          </div>
        )}

        {/* 工作流状态 */}
        <div className="mb-8 bg-white rounded-lg shadow-sm border p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">工作流状态</h2>
          <div className="space-y-4">
            {/* 状态标签 */}
            <div className="flex items-center space-x-3">
              <span className="text-sm font-medium text-gray-700">当前状态:</span>
              <span
                className={`px-3 py-1 rounded-full text-sm font-medium ${
                  workflowStatus === 'completed'
                    ? 'bg-green-100 text-green-800'
                    : workflowStatus === 'failed'
                      ? 'bg-red-100 text-red-800'
                      : workflowStatus === 'running'
                        ? 'bg-blue-100 text-blue-800'
                        : 'bg-gray-100 text-gray-800'
                }`}
              >
                {workflowStatus}
              </span>
            </div>

            {/* 进度条 */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-700">执行进度:</span>
                <span className="text-sm text-gray-600">{progress}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>
          </div>
        </div>

        {/* 结果展示区（双栏布局） */}
        {workflowStatus === 'completed' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* 左栏：剧本大纲 */}
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">剧本大纲</h2>
              {chapter?.script ? (
                <div className="prose prose-sm max-w-none">
                  <pre className="whitespace-pre-wrap text-sm text-gray-800 bg-gray-50 p-4 rounded-lg">
                    {chapter.script}
                  </pre>
                </div>
              ) : (
                <p className="text-sm text-gray-500">暂无剧本内容</p>
              )}
            </div>

            {/* 右栏：资产卡片 */}
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">资产卡片</h2>
              {assets.length > 0 ? (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  {assets.map((asset) => (
                    <div
                      key={asset.id}
                      className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                    >
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="font-medium text-gray-900">{asset.name}</h3>
                        <span
                          className={`px-2 py-1 rounded text-xs font-medium ${
                            asset.type === 'character'
                              ? 'bg-purple-100 text-purple-800'
                              : asset.type === 'scene'
                                ? 'bg-blue-100 text-blue-800'
                                : 'bg-green-100 text-green-800'
                          }`}
                        >
                          {asset.type === 'character'
                            ? '角色'
                            : asset.type === 'scene'
                              ? '场景'
                              : '道具'}
                        </span>
                      </div>
                      {asset.description && (
                        <p className="text-sm text-gray-600 mb-2">
                          {asset.description}
                        </p>
                      )}
                      {asset.metadata && (
                        <div className="space-y-1">
                          {Object.entries(asset.metadata).map(([key, value]) => (
                            <div key={key} className="flex">
                              <span className="text-xs text-gray-500 w-20">{key}:</span>
                              <span className="text-xs text-gray-800">
                                {typeof value === 'string' ? value : JSON.stringify(value)}
                              </span>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-gray-500">暂无资产</p>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
