<script lang="ts" setup>
import { onUnmounted, ref, nextTick } from 'vue'
import * as echarts from 'echarts'
import {
  ElButton,
  ElContainer,
  ElNotification,
  type UploadInstance,
  type UploadProps,
  type UploadRawFile,
  type UploadRequestOptions
} from 'element-plus'

const models = ref([
  { value: 'model1', label: '模型 1' },
  { value: 'model2', label: '模型 2' },
  { value: 'model3', label: '模型 3' },
])
const selectedModel = ref('')

const isTesting = ref(false)

// 测试结果数据（后端返回各类别概率）及最终答案
const resultData = ref<number[] | null>(null)
const finalAnswer = ref('')

const chartEl = ref<HTMLElement>()
const detailPage = ref<InstanceType<typeof ElContainer>>()
let chart: echarts.ECharts

function updateChart() {
  if (!chartEl.value) return

  chart = echarts.init(chartEl.value)

  const option = {
    tooltip: {},
    xAxis: {
      type: 'category',
      data: ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'],
    },
    yAxis: {
      type: 'value',
    },
    series: [
      {
        data: resultData.value,
        type: 'bar',
        itemStyle: {
          color: '#409EFF',
        },
      },
    ],
  }
  chart.setOption(option)
  scrollToBottom()
}

async function startTest() {
  if (!selectedModel.value) {
    ElNotification({
      title: '请先选择一个模型',
      type: "error",
    })
    return
  }
  if (!file.value) {
    ElNotification({
      title: '请导入图片',
      type: "error",
    })
    return
  }

  isTesting.value = true

  try {
    // 这里模拟 3 秒延时后返回结果
    await new Promise((resolve) => setTimeout(resolve, 3000))
    resultData.value = [5, 10, 15, 35, 10, 15, 5, 3, 1, 1]
    const maxScore = Math.max(...resultData.value)
    const maxIndex = resultData.value.indexOf(maxScore)
    finalAnswer.value = maxIndex.toString()
    await nextTick(() => updateChart())
  } catch (error) {
    console.error(error)
    ElNotification({
      title: '测试失败，请重试',
      type: "error",
    })
  } finally {
    isTesting.value = false
  }
}

const file = ref<File | null>(null)
const uploader = ref<UploadInstance>()

const handleBeforeUpload = (option: UploadRequestOptions) => {
  const fileData = option.file
  if (!fileData.type.startsWith('image/')) {
    ElNotification({
      title: '仅支持图片格式',
      type: "error",
    })
    return false
  }
  file.value = fileData
  return false // 阻止 Element Plus 组件自动上传
}

const handleExceed: UploadProps['onExceed'] = (files) => {
  uploader.value!.clearFiles()
  const file = files[0] as UploadRawFile
  uploader.value!.handleStart(file)
}

const scrollToBottom = () => {
  if (detailPage.value) {
    detailPage.value.$el.scrollIntoView({
      behavior: 'smooth',
      block: 'end',
    })
  }
}

onUnmounted(() => {
  if (chart) chart.dispose()
})
</script>

<template>
  <el-container class="page-container">
    <el-container class="page-full">
      <el-text class="page-title">自定义模型测试</el-text>
      <el-form class="model-select" label-position="top" label-width="100px">
        <el-form-item label="选择模型">
          <el-select v-model="selectedModel" placeholder="请选择模型">
            <el-option
              v-for="model in models"
              :key="model.value"
              :label="model.label"
              :value="model.value"
            />
          </el-select>
        </el-form-item>

        <el-upload
          ref="uploader"
          :http-request="handleBeforeUpload"
          :limit="1"
          :on-exceed="handleExceed"
          accept="image/jpeg,image/png"
          class="img-upload"
          list-type="picture"
        >
          <el-button type="primary">上传测试图片</el-button>
          <template #tip>
            <div class="el-upload__tip">支持 jpg/png 文件，将会被拉伸/压缩至模型支持的尺寸</div>
          </template>
        </el-upload>

        <!-- 开始测试按钮 -->
        <el-button
          :disabled="!selectedModel || !file || isTesting"
          :loading="isTesting"
          class="start-button"
          round
          size="large"
          type="primary"
          @click="startTest"
          >开始测试
        </el-button>
      </el-form>
    </el-container>

    <el-container ref="detailPage" class="page-full" v-show="resultData">
      <el-text class="chart-title">答案概率预估图</el-text>
      <el-text>所选定图片可能属于各类型的概率</el-text>

      <div class="chart-container">
        <div ref="chartEl" class="chart" style="height: 400px"></div>
      </div>
        <p class="final-answer">
          预估答案：<strong>{{ finalAnswer }}</strong>
        </p>
    </el-container>
  </el-container>
</template>

<style scoped>
.page-container {
  height: calc(100vh - 64px);
  width: 100vw;
  overflow-x: hidden;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.page-full {
  height: calc(100vh - 64px);
  width: 100vw;
  flex-shrink: 0;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.page-title {
  padding-bottom: 48px;
  font-size: 32px;
  font-weight: bold;
  color: var(--el-text-color-primary);
  letter-spacing: 0.05em;
}

.model-select {
  margin-bottom: 20px;
  width: 300px;
}

.img-upload {
  margin-top: 32px;
}

.start-button {
  width: 100%;
  margin-top: 32px;
  margin-bottom: 10vh;
}

.final-answer {
  padding-bottom: 48px;
  font-size: 18px;
}

.chart-title {
  padding-top: 48px;
  padding-bottom: 4px;
  font-size: 24px;
  color: var(--el-text-color-primary);
  letter-spacing: 0.05em;
}

.chart-container {
  width: 800px;
  margin-top: 12px;
  align-items: flex-end;
}
</style>
