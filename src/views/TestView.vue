<script lang="ts" setup>
import { onUnmounted, ref, onMounted, nextTick } from 'vue'
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
import axios from 'axios'
import { useRouter } from 'vue-router'

type Model = {
  id: string
  name: string
}

interface ModelData {
  id: number;
  name: string;
}

interface ResultData {
  [category: string]: number; // 明确 value 为 number 类型
}

const router = useRouter()

const models = ref<Model[]>([])
const selectedModel = ref('')

const isTesting = ref(false)

// 测试结果数据（后端返回各类别概率）及最终答案
const resultCategory = ref<string[]>([])
const resultData = ref<number[]>([])
const finalAnswer = ref('')

const chartEl = ref<HTMLElement>()
const detailPage = ref<InstanceType<typeof ElContainer>>()
let chart: echarts.ECharts

const initChart = () => {
  if (!chartEl.value) return

  chart = echarts.init(chartEl.value)

  const option = {
    tooltip: {},
    xAxis: {
      type: 'category',
      data: resultCategory.value,
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

const file = ref<File | null>(null)
const uploader = ref<UploadInstance>()

const handleFile = (rawFile: File) => {
  if (!['image/jpeg', 'image/png'].includes(rawFile.type)) {
    ElNotification({
      title: '文件类型错误',
      message: '仅支持 JPG/PNG 格式',
      type: 'error',
    })
  } else {
    file.value = rawFile
  }
}

const handleBeforeUpload = (option: UploadRequestOptions) => {
  const rawFile = option.file
  handleFile(rawFile)
  return false // 阻止 Element Plus 组件自动上传
}

const handleExceed: UploadProps['onExceed'] = (files) => {
  uploader.value!.clearFiles()
  const rawFile = files[0] as UploadRawFile
  handleFile(rawFile)
  uploader.value!.handleStart(rawFile)
}

const startTest = async () => {
  resultCategory.value = []
  resultData.value = []
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

  const formData = new FormData();
  formData.append('file', file.value);
  formData.append('model_id', selectedModel.value);

  await axios.post('/test_accuracy', formData)
    .then(response => {
      const currentData = response.data.result as ResultData;
      Object.entries(currentData).forEach(([key, value]: [string, number]) => {
        resultCategory.value.push(key)
        resultData.value.push(Math.ceil(value * 10000) / 100)
      });
    })
    .catch(() => {
      ElNotification({
        title: '文件损坏，请稍后重试',
        type: "error",
      })
    })

  await nextTick(() => initChart())

  const maxScore = Math.max(...resultData.value)
  const maxIndex = resultData.value.indexOf(maxScore)
  finalAnswer.value = resultCategory.value[maxIndex]
  isTesting.value = false
}

const scrollToBottom = () => {
  if (detailPage.value) {
    detailPage.value.$el.scrollIntoView({
      behavior: 'smooth',
      block: 'end',
    })
  }
}

onMounted(async () => {
  await axios.get('/get_models')
    .then(response => {
      models.value = response.data.models.map((model: ModelData) => {
        return {
          id: model['id'],
          name: model['name']
        }
      })
    })
    .catch(() => {
      router.push('/start')
      ElNotification({
        title: '未找到可用模型，请先进行训练或导入模型',
        type: "error",
      })
    })
})

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
              :key="model.id"
              :label="model.name"
              :value="model.id"
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
            <div class="el-upload__tip">支持 jpg/png 文件，将会被处理为模型支持的形式，包括但不限于修改尺寸和颜色通道数</div>
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

    <el-container ref="detailPage" class="page-full" v-show="resultData.length > 0">
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
