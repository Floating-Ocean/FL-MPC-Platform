<script lang="ts" setup>
import { useRouter } from 'vue-router'
import { ElContainer, ElNotification } from 'element-plus'
import { onMounted, ref } from 'vue'
import axios from 'axios'

const router = useRouter()

type Dataset = {
  id: string
  name: string
  intro: string
}

const epochs = ref(50)
const selectedDataset = ref<Dataset>()
const dataset = ref<Dataset[]>([])
const datasetIntro = ref('未选择数据集，可在左侧下拉框中选择。选择数据集后，此处会给出数据集的简介。')

const goStart = () => {
  router.push('/train')
}

const onDatasetChanged = (val: string) => {
  const selected = dataset.value.find((item: Dataset) => item.id == val)
  if (selected) {
    datasetIntro.value = selected.intro
  }else{
    datasetIntro.value = '未选择数据集，可在左侧下拉框中选择。选择数据集后，此处会给出数据集的简介。'
  }
}

onMounted(async () => {
  await axios.get('/get_models')
    .then(response => {
      dataset.value = response.data.models.map((array: Array<string>) => {
        return {
          id: array[0],
          name: array[1],
          intro: array[2]
        }
      })
    })
    .catch(() => {
      ElNotification({
        title: '获取可用模型失败，请稍后重试',
        type: "error",
      })
    })
})
</script>

<template>
  <el-container class="page-container">
    <el-form class="config-form" label-position="top">
        <el-text class="page-title">配置模型训练参数</el-text>
        <el-form-item label="选择数据集">
          <el-select v-model="selectedDataset" placeholder="请选择数据集"
                     @change="onDatasetChanged">
            <el-option
              v-for="item in dataset"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="训练轮数">
          <el-input-number v-model="epochs" :max="100" :min="1" />
        </el-form-item>
        <el-button class="start-button" type="primary" size="large" round
                   @click="goStart"
                   :disabled="selectedDataset == undefined">开始训练</el-button>
    </el-form>
    <el-alert class="config-form-intro" title="数据集介绍" type="info" :description="datasetIntro" :closable="false" center show-icon/>
  </el-container>
</template>

<style scoped>
.page-container {
  height: calc(100vh - 64px);
  width: 100vw;
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  padding: 0 64px 0 6vw;
}

.page-title {
  padding-bottom: 48px;
  font-size: 32px;
  font-weight: bold;
  color: var(--el-text-color-primary);
  letter-spacing: 0.05em;
}

.config-form-intro {
  padding: 24px;
  width: 30vw;
  border-radius: 24px;
  margin-bottom: 2vh;
}

.config-form {
  display: flex;
  flex-direction: column;
}

.start-button {
  width: 100%;
  margin-top: 48px;
  margin-bottom: 10vh;
}
</style>
