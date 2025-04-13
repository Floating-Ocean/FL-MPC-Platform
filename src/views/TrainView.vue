<script lang="ts" setup>
import { onMounted, onUnmounted, ref } from 'vue'
import { ElContainer, ElNotification } from 'element-plus'
import TrainingEChart from '@/components/TrainingEChart.vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

const router = useRouter()

const subProgressColor = ref('#e6a23c')
const trainingStatus = ref('正在获取训练进度')
const initLoading = ref(true)
const evalLoading = ref(true)

const chartRef = ref()
const roundPercentage = ref(0)
const epochPercentage = ref(0)
let pollInterval: number | null = null

const startPooling = async () => {
  pollInterval = setInterval(async () => {
    await axios.get('/get_training_progress')
      .then(async (response) => {
        const currentStatus = response.data.status
        const currentData = response.data.data
        switch (currentStatus) {
          case 'INITIALIZING':
            trainingStatus.value = '正在初始化模型训练'
            if (!initLoading.value) initLoading.value = true
            if (evalLoading.value) evalLoading.value = false
            break
          case 'TRAINING':
            trainingStatus.value = `正在进行第${currentData['epoch']}轮训练`
            if (initLoading.value) initLoading.value = false
            if (evalLoading.value) evalLoading.value = false
            const currentEpochPercentage = currentData['epoch_progress']
            const currentRoundPercentage = (currentData['epoch'] - 1) * 100.0 / currentData['total_epoch']
                                           + currentData['epoch_progress'] / currentData['total_epoch']
            if (currentRoundPercentage != roundPercentage.value) roundPercentage.value = currentRoundPercentage
            if (currentEpochPercentage != epochPercentage.value) epochPercentage.value = currentEpochPercentage
            if (chartRef.value.accData.length < currentData['acc_trains'].length) {
                chartRef.value.accData = currentData['acc_trains']
            }
            if (chartRef.value.lossData.length < currentData['loss_trains'].length) {
                chartRef.value.lossData = currentData['loss_trains']
            }
            break
          case 'EVALUATING':
            trainingStatus.value = '正在评估模型'
            if (initLoading.value) initLoading.value = false
            if (!evalLoading.value) evalLoading.value = true
            if (chartRef.value.accData.length < currentData['acc_trains'].length) {
              chartRef.value.accData = currentData['acc_trains']
            }
            if (chartRef.value.lossData.length < currentData['loss_trains'].length) {
              chartRef.value.lossData = currentData['loss_trains']
            }
            break
          case 'TEST_EVALUATING':
            trainingStatus.value = '正在测试集上评估模型'
            if (initLoading.value) initLoading.value = false
            if (!evalLoading.value) evalLoading.value = true
            if (chartRef.value.accData.length < currentData['acc_trains'].length) {
              chartRef.value.accData = currentData['acc_trains']
            }
            if (chartRef.value.lossData.length < currentData['loss_trains'].length) {
              chartRef.value.lossData = currentData['loss_trains']
            }
            break
          case 'FINISHED':
            await axios.get('/train_finish')
              .then(async () => {
                await checkRecord()
              })
              .catch(() => {
                ElNotification({
                  title: '训练异常结束，请稍后重试',
                  type: "error",
                })
                stopPolling()
              })
            break
        }
      })
      .catch(() => {
        ElNotification({
          title: '获取训练进度失败，请稍后重试',
          type: "error",
        })
      })
  }, 2000)
};

const stopPolling = () => {
  if (pollInterval) {
    clearInterval(pollInterval)
  }
}

const checkRecord = async () => {
  stopPolling()
  await axios.get('/get_last_record')
    .then(() => {
      router.push('/train/finish')
      ElNotification({
        title: '训练结束',
        type: "success",
      })
    })
    .catch(() => {
      router.push('/start/param')
      ElNotification({
        title: '训练记录不存在',
        type: "error",
      })
    })
}

onMounted(async () => {
  await axios.get('/get_training_progress')
    .then(async response => {
      if (response.data.message == 'No running task') {
        await checkRecord()
        return
      }
      if (response.data.status == 'FINISHED'){
        await axios.get('/train_finish')
          .then(async () => {
            await checkRecord()
          })
          .catch(() => {
            ElNotification({
              title: '训练异常结束，请稍后重试',
              type: "error",
            })
            stopPolling()
          })
        return
      }
      await startPooling()
    })
    .catch(() => {
      ElNotification({
        title: '获取训练进度失败，请稍后重试',
        type: "error",
      })
    })
})

onUnmounted(() => {
  stopPolling()
})

</script>

<template>
  <el-container class="page-container">
    <el-text class="chart-title">{{ trainingStatus }}</el-text>

    <el-progress v-if="initLoading" :show-text="false" :stroke-width="24" :indeterminate="true" :percentage="80" class="train-progress" />

    <el-container v-else class="training-container">
      <el-progress :text-inside="true" :stroke-width="24" :percentage="roundPercentage"
                   :format="(percentage: number) => `${percentage.toFixed(2)}%`" class="train-progress" />
      <el-progress :text-inside="true" :stroke-width="24" :indeterminate="evalLoading" :show-text="!evalLoading"
                   :percentage="evalLoading ? 100 : epochPercentage" :color="subProgressColor"
                   :format="(percentage: number) => `${percentage.toFixed(2)}%`" class="train-progress" />

      <el-alert type="info" show-icon class="train-alert">
        <p>模型正在后台训练中，您可以：</p>
        <p>1. 最小化本窗口进行其他操作</p>
        <p>2. 随时返回查看实时进度</p>
      </el-alert>
    </el-container>

    <TrainingEChart ref="chartRef" />
  </el-container>
</template>

<style scoped>
.page-container {
  height: calc(100vh - 64px);
  width: 100vw;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.training-container {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.train-progress {
  padding-top: 12px;
  width: 50vw;
}

.train-alert {
  margin-top: 40px;
  width: 40vw;
}

.chart-title {
  padding-top: 48px;
  font-size: 24px;
  color: var(--el-text-color-primary);
  letter-spacing: 0.05em;
}
</style>

<style>
.train-progress {
  .el-progress-bar__inner{
    min-width: 48px;
  }
}
</style>
