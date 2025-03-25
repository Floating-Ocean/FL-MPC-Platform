<script lang="ts" setup>
import { useRouter } from 'vue-router'
import { ElContainer } from 'element-plus'
import { ref } from 'vue'

const router = useRouter()

const epochs = ref(50)
const dataset = ref('mnist')

const goStart = () => {
  router.push('/train')
}
</script>

<template>
  <el-container class="page-container">
    <el-form class="config-form" label-position="top">
        <el-text class="page-title">配置模型训练参数</el-text>
        <el-form-item label="选择数据集">
          <el-select v-model="dataset" placeholder="请选择数据集">
            <el-option label="MNIST" value="mnist" />
            <el-option label="CIFAR-10" value="cifar10" />
          </el-select>
        </el-form-item>

        <el-form-item label="训练轮数">
          <el-input-number v-model="epochs" :max="100" :min="1" />
        </el-form-item>
        <el-button class="start-button" type="primary" size="large" round
                   @click="goStart">开始训练</el-button>
    </el-form>
    <el-alert class="config-form-intro" title="数据集介绍" type="info" :closable="false" center show-icon
    >Mnist数据集是一个经典的手写数字图片数据集，包含0到9的灰度数字图片，每个类别有成千上万的示例。</el-alert
    >
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
