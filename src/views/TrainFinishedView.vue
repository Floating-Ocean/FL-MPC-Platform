<script lang="ts" setup>
import { useRouter } from 'vue-router'
import { onMounted, ref } from 'vue'
import { ArrowUp, Download, FolderChecked } from '@element-plus/icons-vue'
import { ElContainer, ElNotification } from 'element-plus'
import TrainingEChart from '@/components/TrainingEChart.vue'
import axios from 'axios'

const router = useRouter()

const chartRef = ref()
const chartContainerEl = ref<InstanceType<typeof ElContainer>>()

const trainAcc = ref<number>(0)
const testAcc = ref<number>(0)
const modelId = ref<string>('')

const scrollToBottom = () => {
  if (chartContainerEl.value) {
    chartContainerEl.value.$el.scrollIntoView({
      behavior: 'smooth',
      block: 'end',
    })
  }
}

const goTest = () => {
  router.push('/test')
}

const downloadModel = async () => {
  await axios({
    method: 'get',
    url: `/download_model/${modelId.value}`,
    responseType: 'blob'
  })
    .then(response => {
      // 创建临时下载链接
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url

      // 从Content-Disposition获取文件名
      const filename = response.request.getResponseHeader('Content-Disposition')
        ?.split('filename=')[1]
        ?.replace(/"/g, '')

      console.log(filename)

      link.setAttribute('download', filename || 'model_nameless.pth')
      document.body.appendChild(link)
      link.click()

      link.remove()
      window.URL.revokeObjectURL(url)
    })
    .catch(() => {
      ElNotification({
        title: '模型不存在',
        type: "error",
      })
    })
}

onMounted(async () => {
  await axios.get('/get_last_record')
    .then(response => {
      const currentData = response.data
      modelId.value = currentData['model_id']
      chartRef.value.lossData = currentData['loss_list']
      chartRef.value.accData = currentData['acc_list']
      testAcc.value = currentData['test_acc']
      trainAcc.value = currentData['train_acc']
    })
    .catch(() => {
      router.push('/start/param')
      ElNotification({
        title: '训练记录不存在',
        type: "error",
      })
    })
})
</script>

<template>
  <el-container class="page-container">
    <el-container class="page-full">
      <el-result icon="success" title="训练完成" class="page-result" />
      <el-row :gutter="10" class="result-statics">
        <el-col :span="12">
          <el-statistic title="训练集准确度" :value="trainAcc" precision="2" suffix="%" />
        </el-col>
        <el-col :span="12">
          <el-statistic title="测试集准确度" :value="testAcc" precision="2" suffix="%" />
        </el-col>
      </el-row>

      <el-row class="page-content">
        <el-button type="primary" class="page-button" @click="downloadModel" round>
          <div class="page-button-content">
            <el-icon class="page-button-icon"><Download /></el-icon>
            <span class="page-button-text">下载模型</span>
          </div>
        </el-button>
        <el-button @click="scrollToBottom" type="warning" class="page-button" round>
          <div class="page-button-content">
            <el-icon class="page-button-icon"><ArrowUp /></el-icon>
            <span class="page-button-text">查看图表</span>
          </div>
        </el-button>
        <el-button type="success" class="page-button" round
                   @click="goTest">
          <div class="page-button-content">
            <el-icon class="page-button-icon"><FolderChecked /></el-icon>
            <span class="page-button-text">测试模型</span>
          </div>
        </el-button>
      </el-row>
    </el-container>

    <el-container ref="chartContainerEl" class="page-full">
      <el-text class="chart-title">训练折线表</el-text>
      <el-text>可通过右键保存的方式下载图表</el-text>
      <TrainingEChart ref="chartRef" />
    </el-container>
  </el-container>
</template>

<style scoped>
.page-container {
  height: calc(100vh - 64px);
  width: 100vw;
  overflow-x: hidden;
  overflow-y: scroll;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.page-result {
  width: 100vw;
}

.page-full {
  height: calc(100vh - 64px);
  flex-shrink: 0;
  flex-direction: column;
  align-items: center;
}

.result-statics {
  justify-self: center;
  padding-top: 24px;
  min-width: 400px;
  text-align: center;
}

.chart-title {
  padding-top: 48px;
  padding-bottom: 4px;
  font-size: 24px;
  color: var(--el-text-color-primary);
  letter-spacing: 0.05em;
}

.page-content {
  flex-grow: 1;
  margin-bottom: 48px;
  align-items: flex-end;
}

.page-button {
  width: 160px;
  height: 240px;
  margin-left: 12px;
  margin-right: 12px;
}

.page-button-content {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.page-button-icon {
  font-size: 52px;
  margin-bottom: 56px;
}

.page-button-text {
  font-size: 18px;
  margin-bottom: 4px;
  font-weight: bold;
  letter-spacing: 0.12em;
}
</style>
